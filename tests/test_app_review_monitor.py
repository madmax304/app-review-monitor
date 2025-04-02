import pytest
from unittest.mock import Mock, patch
from app_review_monitor import get_recent_reviews, send_slack_notification

@pytest.fixture
def mock_api():
    with patch('app_review_monitor.api') as mock:
        yield mock

@pytest.fixture
def mock_slack():
    with patch('app_review_monitor.slack_client') as mock:
        yield mock

def test_get_recent_reviews_success(mock_api):
    # Mock successful API response
    mock_review = Mock()
    mock_review.attributes.rating = 5
    mock_review.attributes.title = "Great app!"
    mock_review.attributes.body = "Really enjoying this app"
    mock_review.attributes.created_date = "2024-02-20T10:00:00Z"
    
    mock_api.reviews.list_reviews.return_value = [mock_review]
    
    reviews = get_recent_reviews()
    assert len(reviews) == 1
    assert reviews[0].attributes.rating == 5
    assert reviews[0].attributes.title == "Great app!"

def test_get_recent_reviews_error(mock_api):
    # Mock API error
    mock_api.reviews.list_reviews.side_effect = Exception("API Error")
    
    reviews = get_recent_reviews()
    assert len(reviews) == 0

def test_send_slack_notification_success(mock_slack):
    # Mock successful Slack message
    mock_slack.chat_postMessage.return_value = {"ts": "1234567890"}
    
    mock_review = Mock()
    mock_review.attributes.rating = 5
    mock_review.attributes.title = "Great app!"
    mock_review.attributes.body = "Really enjoying this app"
    mock_review.attributes.created_date = "2024-02-20T10:00:00Z"
    
    send_slack_notification([mock_review])
    mock_slack.chat_postMessage.assert_called_once()

def test_send_slack_notification_error(mock_slack):
    # Mock Slack error
    mock_slack.chat_postMessage.side_effect = Exception("Slack Error")
    
    mock_review = Mock()
    mock_review.attributes.rating = 5
    mock_review.attributes.title = "Great app!"
    mock_review.attributes.body = "Really enjoying this app"
    mock_review.attributes.created_date = "2024-02-20T10:00:00Z"
    
    # Should not raise exception
    send_slack_notification([mock_review]) 