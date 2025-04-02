import os
import json
import jwt
import time
from datetime import datetime, timedelta
from typing import List, Dict, Union
import pytz
import requests
from dotenv import load_dotenv
from .logging import setup_logging
import logging
from appstoreconnect import Api
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .exceptions import APIError, SlackError, ConfigurationError

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Constants
APP_ID = os.getenv('APP_ID')
API_KEY_ID = os.getenv('KEY_ID')
API_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
API_ISSUER_ID = os.getenv('ISSUER_ID')

def get_today():
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now().strftime('%Y-%m-%d')

def get_date_n_days_ago(n):
    """Get the date n days ago in YYYY-MM-DD format."""
    date = datetime.now() - timedelta(days=n)
    return date.strftime('%Y-%m-%d')

def generate_token():
    """Generate a JWT token for App Store Connect API authentication."""
    logger.debug("Generating JWT token")
    key_id = os.getenv("KEY_ID")
    issuer_id = os.getenv("ISSUER_ID")
    private_key = os.getenv("PRIVATE_KEY")

    logger.debug(f"Using key_id: {key_id}, issuer_id: {issuer_id}")

    if not all([key_id, issuer_id, private_key]):
        raise ValueError("Missing required environment variables for token generation")

    # Convert the private key string to bytes
    private_key_bytes = private_key.encode('utf-8')

    # Set token expiration to 20 minutes from now
    expiration = int(time.time()) + 1200

    # Define the token payload
    payload = {
        'iss': issuer_id,
        'exp': expiration,
        'aud': 'appstoreconnect-v1'
    }

    # Define the token headers
    headers = {
        'kid': key_id,
        'typ': 'JWT',
        'alg': 'ES256'
    }

    try:
        # Generate the JWT token
        token = jwt.encode(
            payload,
            private_key_bytes,
            algorithm='ES256',
            headers=headers
        )
        # Ensure token is a string, not bytes
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        logger.debug("JWT token generated successfully")
        return token
    except Exception as e:
        logger.error(f"Error generating JWT token: {e}")
        raise

def make_api_request(endpoint: str, params: Dict) -> Dict:
    """
    Make a request to the App Store Connect API.
    
    Args:
        endpoint: API endpoint to call
        params: Query parameters
        
    Returns:
        Response data
        
    Raises:
        APIError: If the request fails
    """
    try:
        # Initialize API client
        api = Api(
            key_id=os.getenv("KEY_ID"),
            key_file=os.getenv("PRIVATE_KEY"),
            issuer_id=os.getenv("ISSUER_ID")
        )
        
        # Build URL
        base_url = "https://api.appstoreconnect.apple.com"
        url = f"{base_url}/{endpoint}"
        
        # Add JWT token
        headers = {
            "Authorization": f"Bearer {api.token}",
            "Content-Type": "application/json"
        }
        
        # Make request
        logging.debug(f"Making request to {url} with params {params}")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            logging.error(f"API request failed with status {response.status_code}")
            logging.error(f"Response body: {response.text}")
            return None
            
        return response.json()
        
    except Exception as e:
        logging.error(f"Error making API request: {str(e)}")
        return None

def get_recent_reviews(app_id: str, days: int = 1) -> List[Dict]:
    """
    Fetch recent App Store reviews.
    
    Args:
        app_id: The App Store ID of the app
        days: Number of days to look back for reviews
        
    Returns:
        List of review dictionaries
        
    Raises:
        APIError: If there is an error fetching reviews
    """
    try:
        # Calculate date range
        end_date = datetime.now(pytz.UTC)
        start_date = end_date - timedelta(days=days)
        
        logging.info("Fetching reviews", extra={
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "days": days
        })
        
        # Initialize API client
        key_id = os.getenv("KEY_ID")
        private_key = os.getenv("PRIVATE_KEY")
        issuer_id = os.getenv("ISSUER_ID")
        
        if not all([key_id, private_key, issuer_id]):
            raise APIError("Missing required API credentials")
            
        # Make API request
        endpoint = f"v1/apps/{app_id}/customerReviews"
        params = {
            "fields[customerReviews]": "rating,title,body,reviewerNickname,territory,createdDate",
            "sort": "-createdDate",
            "limit": 100
        }
        
        response = make_api_request(endpoint, params)
        
        if not response:
            raise APIError("Failed to fetch reviews from App Store Connect API")
            
        # Extract reviews from response
        if isinstance(response, dict) and 'data' in response:
            reviews = []
            for item in response['data']:
                if 'attributes' in item:
                    attrs = item['attributes']
                    review = {
                        'id': item.get('id', ''),
                        'rating': attrs.get('rating', 0),
                        'title': attrs.get('title', 'No title'),
                        'body': attrs.get('body', 'No review text'),
                        'author': attrs.get('reviewerNickname', 'Anonymous'),
                        'territory': attrs.get('territory', 'Unknown'),
                        'date': attrs.get('createdDate', '')
                    }
                    reviews.append(review)
        else:
            raise APIError("Invalid response format from App Store Connect API")
            
        # Filter reviews by date
        filtered_reviews = []
        for review in reviews:
            try:
                created_date = datetime.fromisoformat(review['date'].replace('Z', '+00:00'))
                if start_date <= created_date <= end_date:
                    filtered_reviews.append(review)
            except (KeyError, ValueError):
                continue
            
        logging.info(f"Successfully fetched {len(filtered_reviews)} reviews")
        return filtered_reviews
            
    except APIError:
        raise
    except Exception as e:
        raise APIError(f"Error fetching reviews: {str(e)}")

def get_processed_reviews_file():
    """Get the path to the processed reviews file."""
    return os.path.join(os.path.dirname(__file__), 'processed_reviews.json')

def load_processed_reviews():
    """Load the processed reviews data from file."""
    file_path = get_processed_reviews_file()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return {
                    'review_ids': data.get('review_ids', []),
                    'last_run': data.get('last_run', None)
                }
        except json.JSONDecodeError:
            logging.warning("Error reading processed reviews file, starting fresh")
            return {'review_ids': [], 'last_run': None}
    return {'review_ids': [], 'last_run': None}

def save_processed_reviews(review_ids: List[str], last_run: str) -> None:
    """
    Save processed review IDs and last run timestamp.
    
    Args:
        review_ids: List of review IDs that have been processed
        last_run: ISO format timestamp of when reviews were last processed
        
    Raises:
        IOError: If there is an error saving to file
    """
    data = {
        "review_ids": review_ids,
        "last_run": last_run
    }
    try:
        with open(get_processed_reviews_file(), "w") as f:
            json.dump(data, f)
    except IOError as e:
        logging.error(f"Error saving processed reviews: {e}")
        raise

def send_slack_notification(webhook_url: str, reviews: List[Dict], channel: str = "#app-reviews") -> None:
    """
    Send reviews to Slack channel.
    
    Args:
        webhook_url: Slack webhook URL
        reviews: List of reviews to send
        channel: Slack channel to send to
        
    Raises:
        SlackError: If there is an error sending to Slack
    """
    if not reviews:
        logging.info("No new reviews to send")
        return
        
    try:
        for review in reviews:
            # Format the review message
            rating = "⭐" * review.get("rating", 0)
            text = (
                "*New App Store Review*\n"
                f"Rating: {rating}\n"
                f"Title: {review.get('title', 'No title')}\n"
                f"Review: {review.get('body', 'No review text')}\n"
                f"Reviewer: {review.get('author', 'Anonymous')}\n"
                f"Territory: {review.get('territory', 'Unknown')}\n"
                f"Date: {review.get('date', 'Unknown')}"
            )
            
            # Create message payload
            payload = {
                "text": text,
                "channel": channel
            }
            
            # Send the notification
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code != 200:
                error_msg = response.text
                raise SlackError(f"Failed to send notification: {error_msg}")
                
            logging.info("Successfully sent notification for review", extra={
                "review_id": review.get("id"),
                "rating": review.get("rating")
            })
                    
    except SlackError:
        raise
    except Exception as e:
        raise SlackError(f"Error sending notification: {str(e)}")

def process_reviews(app_id: str, days: int = 1) -> list:
    """Process reviews for a specific app.

    Args:
        app_id (str): The App Store ID of the app to process reviews for.
        days (int): Number of days to look back for reviews. Defaults to 1.

    Returns:
        list: List of new reviews that haven't been processed before.
    """
    try:
        # Get recent reviews
        reviews = get_recent_reviews(app_id, days)
        if not reviews:
            logging.info("No new reviews found")
            return []

        # Load previously processed reviews
        processed_data = load_processed_reviews()
        processed_review_ids = set(processed_data['review_ids'])
        
        logging.info(f"Found {len(reviews)} reviews, checking for new ones...")
        logging.debug(f"Previously processed reviews: {len(processed_review_ids)}")

        # Filter out already processed reviews
        new_reviews = []
        for review in reviews:
            if review['id'] not in processed_review_ids:
                new_reviews.append(review)
                processed_review_ids.add(review['id'])
                logging.debug(f"New review found: {review['id']}")
            else:
                logging.debug(f"Skipping already processed review: {review['id']}")

        # Save updated processed reviews
        if new_reviews:
            save_processed_reviews(list(processed_review_ids), datetime.now().isoformat())
            logging.info(f"Found {len(new_reviews)} new reviews")
        else:
            logging.info("No new reviews to process")

        return new_reviews

    except Exception as e:
        logging.error(f"Error processing reviews: {e}")
        return []

def format_review_message(review):
    """Format a review for Slack notification.

    Args:
        review (dict): Review data.

    Returns:
        str: Formatted message.
    """
    attributes = review.get('attributes', {})
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*New App Store Review*\n"
                   f"Rating: {'⭐' * attributes.get('rating', 0)}\n"
                   f"Title: {attributes.get('title', '(No title)')}\n"
                   f"Review: {attributes.get('body', '(No content)')}\n"
                   f"Reviewer: {attributes.get('reviewerNickname', 'Anonymous')}\n"
                   f"Territory: {attributes.get('territory', 'Unknown')}\n"
                   f"Date: {attributes.get('createdDate', 'Unknown')}"
        }
    }

def main() -> None:
    """Main function to fetch reviews and send notifications."""
    reviews = get_recent_reviews(APP_ID)
    if not reviews:
        print("No reviews found in the specified time period.")
        return
        
    send_slack_notification(os.getenv('SLACK_WEBHOOK_URL'), reviews)

if __name__ == "__main__":
    main() 