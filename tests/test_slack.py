import pytest
from unittest.mock import patch, MagicMock
from app_review_monitor.core import send_slack_notification, format_review_message
from tests.test_config import (
    TEST_SLACK_WEBHOOK,
    MOCK_REVIEWS
)

def test_format_review_message():
    """Test review message formatting"""
    review = MOCK_REVIEWS[0]
    message = format_review_message(review)
    assert "New App Store Review" in message
    assert "Rating: 5" in message
    assert "Title: Great app!" in message
    assert "Reviewer: TestUser1" in message
    assert "Territory: USA" in message

def test_format_review_message_no_title():
    """Test review message formatting without title"""
    review = MOCK_REVIEWS[1]
    message = format_review_message(review)
    assert "New App Store Review" in message
    assert "Rating: 1" in message
    assert "Title: (No title)" in message
    assert "Reviewer: TestUser2" in message
    assert "Territory: USA" in message

def test_send_slack_notification_success():
    """Test successful Slack notification sending"""
    with patch('app_review_monitor.core.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        send_slack_notification(TEST_SLACK_WEBHOOK, MOCK_REVIEWS)
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert 'json' in call_args
        assert 'blocks' in call_args['json']

def test_send_slack_notification_empty_reviews():
    """Test Slack notification with empty reviews list"""
    with patch('app_review_monitor.core.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        send_slack_notification(TEST_SLACK_WEBHOOK, [])
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert 'json' in call_args
        assert 'No new reviews found' in str(call_args['json'])

def test_send_slack_notification_http_error():
    """Test handling of HTTP errors in Slack notification"""
    with patch('app_review_monitor.core.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=400, text="Bad Request")
        with pytest.raises(Exception) as exc_info:
            send_slack_notification(TEST_SLACK_WEBHOOK, MOCK_REVIEWS)
        assert "Failed to send Slack notification" in str(exc_info.value)

def test_send_slack_notification_connection_error():
    """Test handling of connection errors in Slack notification"""
    with patch('app_review_monitor.core.requests.post') as mock_post:
        mock_post.side_effect = Exception("Connection refused")
        with pytest.raises(Exception) as exc_info:
            send_slack_notification(TEST_SLACK_WEBHOOK, MOCK_REVIEWS)
        assert "Connection refused" in str(exc_info.value)

def test_send_slack_notification_message_length():
    """Test handling of long review messages"""
    long_review = {
        "type": "customerReviews",
        "id": "test_review_long",
        "attributes": {
            "rating": 5,
            "title": "A" * 1000,  # Very long title
            "body": "B" * 5000,   # Very long body
            "reviewerNickname": "TestUser3",
            "createdDate": "2024-01-01T00:00:00Z",
            "territory": "USA"
        }
    }
    with patch('app_review_monitor.core.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        send_slack_notification(TEST_SLACK_WEBHOOK, [long_review])
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        message = str(call_args['json'])
        assert len(message) <= 4000  # Slack message length limit

def test_send_slack_notification_special_characters():
    """Test handling of special characters in review messages"""
    special_review = {
        "type": "customerReviews",
        "id": "test_review_special",
        "attributes": {
            "rating": 5,
            "title": "Special chars: !@#$%^&*",
            "body": "Emojis: 😊 🌟 💪",
            "reviewerNickname": "TestUser3",
            "createdDate": "2024-01-01T00:00:00Z",
            "territory": "USA"
        }
    }
    with patch('app_review_monitor.core.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        send_slack_notification(TEST_SLACK_WEBHOOK, [special_review])
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        message = str(call_args['json'])
        assert "Special chars: !@#$%^&*" in message
        assert "Emojis: 😊 🌟 💪" in message 