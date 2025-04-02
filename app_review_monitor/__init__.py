import os
import json
import tempfile
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from appstoreconnect import Api
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Create a temporary file for the private key
temp_key_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
temp_key_file.write(os.getenv('PRIVATE_KEY', ''))
temp_key_file.close()

# Initialize App Store Connect API
api = Api(
    key_id=os.getenv('KEY_ID'),
    key_file=temp_key_file.name,
    issuer_id=os.getenv('ISSUER_ID')
)

# Clean up the temporary file
os.unlink(temp_key_file.name)

# Initialize Slack client
slack_client = WebClient(token=os.getenv('SLACK_WEBHOOK_URL'))

def get_recent_reviews(app_id: str, days: int = 1) -> list:
    """Fetch recent reviews from App Store Connect.
    
    Args:
        app_id: The App Store ID of the app to fetch reviews for
        days: Number of days to look back for reviews (default: 1)
    
    Returns:
        list: List of reviews from the specified time period
    """
    try:
        # Get reviews for the specified number of days
        end_date = datetime.now(pytz.UTC)
        start_date = end_date - timedelta(days=days)
        
        logger.info("Fetching reviews", extra={
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "days": days
        })
        
        reviews = api.reviews.list_reviews(
            filter_app=app_id,
            filter_created_date=f"{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
        )
        
        logger.info(f"Successfully fetched {len(reviews)} reviews")
        return reviews
    except Exception as e:
        logger.error("Error fetching reviews", extra={"error": str(e)})
        return []

def send_slack_notification(reviews: list, channel: str = "#app-reviews") -> None:
    """Send reviews to Slack channel.
    
    Args:
        reviews: List of reviews to send
        channel: Slack channel to send notifications to
    """
    if not reviews:
        logger.info("No reviews to send to Slack")
        return
    
    # Format the message
    message = "📱 *App Store Reviews Update*\n\n"
    
    for review in reviews:
        rating = "⭐" * review.attributes.rating
        message += f"*Rating:* {rating}\n"
        message += f"*Title:* {review.attributes.title}\n"
        message += f"*Review:* {review.attributes.body}\n"
        message += f"*Date:* {review.attributes.created_date}\n"
        message += "-------------------\n"
    
    try:
        response = slack_client.chat_postMessage(
            channel=channel,
            text=message,
            parse="mrkdwn"
        )
        logger.info("Message sent successfully", extra={"ts": response['ts']})
    except SlackApiError as e:
        logger.error("Error sending message to Slack", extra={"error": e.response['error']})

def main() -> None:
    """Main function to run the review monitor."""
    logger.info("Starting App Review Monitor")
    reviews = get_recent_reviews(os.getenv('APP_ID'))
    send_slack_notification(reviews)
    logger.info("Review monitoring completed")

if __name__ == "__main__":
    main() 