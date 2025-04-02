import os
import click
from dotenv import load_dotenv
from .core import process_reviews, send_slack_notification
from .logging import setup_logging
import logging
from datetime import datetime, timedelta
import pytz

# Load environment variables
load_dotenv()

def get_next_check_time(current_time: datetime) -> datetime:
    """Calculate the next check time (9am PST daily).
    
    If current time is before 9am PST, next check will be 9am PST today.
    If current time is after 9am PST, next check will be 9am PST tomorrow.
    """
    # Convert current time to PST
    pst = pytz.timezone('America/Los_Angeles')
    current_time_pst = current_time.astimezone(pst)
    
    # Create target time (9am PST)
    target_time = current_time_pst.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # If current time is after 9am, set target to tomorrow
    if current_time_pst > target_time:
        target_time += timedelta(days=1)
    
    # Convert back to UTC for storage
    return target_time.astimezone(pytz.UTC)

@click.command()
@click.option('--days', default=1, help='Number of days to look back for reviews')
@click.option('--dry-run', is_flag=True, help='Print reviews without sending to Slack')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--config', default='.env', help='Path to config file')
def main(days: int, dry_run: bool, debug: bool, config: str):
    """Monitor App Store reviews and send them to Slack."""
    try:
        # Setup logging with debug flag
        logger = setup_logging(debug)
        
        # Load config file
        load_dotenv(config)
        
        # Get app ID from config
        app_id = os.getenv('APP_ID')
        if not app_id:
            raise ValueError("APP_ID not found in config")
            
        # Process new reviews
        new_reviews = process_reviews(app_id, days)
        
        if not new_reviews:
            logger.info("No new reviews to process")
            if not dry_run:
                webhook_url = os.getenv('SLACK_WEBHOOK_URL')
                if not webhook_url:
                    raise ValueError("SLACK_WEBHOOK_URL not found in config")
                
                # Calculate current time and next run time
                current_time = datetime.now(pytz.UTC)
                next_run = get_next_check_time(current_time)
                
                # Format the message
                message = (
                    f"*App Review Check*\n"
                    f"Time: {current_time.astimezone(pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
                    f"Status: No new reviews found in the last {days} days\n"
                    f"Next check: {next_run.astimezone(pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M:%S %Z')}"
                )
                
                # Send "no new reviews" message to Slack
                send_slack_notification(webhook_url, [{
                    "id": "no_reviews",
                    "rating": 0,
                    "title": "Review Check Complete",
                    "body": message,
                    "date": current_time.isoformat()
                }])
                print("No new reviews found in the specified time period.")
            return
            
        # Send to Slack if not dry run
        if not dry_run:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            if not webhook_url:
                raise ValueError("SLACK_WEBHOOK_URL not found in config")
                
            send_slack_notification(webhook_url, new_reviews)
            logger.info(f"Successfully processed {len(new_reviews)} reviews")
        else:
            # Print reviews in dry run mode
            print(f"\nFound {len(new_reviews)} new reviews:")
            for review in new_reviews:
                print("\nFound review:")
                print(f"Rating: {'⭐' * review.get('rating', 0)}")
                print(f"Title: {review.get('title', 'No title')}")
                print(f"Review: {review.get('body', 'No review text')}")
                print(f"Date: {review.get('date', 'Unknown')}")
                print("--------------------------------------------------")
                
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == '__main__':
    main() 