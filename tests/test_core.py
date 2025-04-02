import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app_review_monitor.core import get_recent_reviews, process_reviews, send_slack_notification
from tests.test_config import (
    TEST_APP_ID,
    TEST_APP_NAME,
    TEST_SLACK_WEBHOOK,
    MOCK_REVIEWS,
    TEST_PERIODS,
    ERROR_SCENARIOS,
    TEST_DATA_DIR,
    PROCESSED_REVIEWS_FILE
)

@pytest.fixture
def setup_test_data():
    """Setup test data directory and files"""
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    if os.path.exists(PROCESSED_REVIEWS_FILE):
        os.remove(PROCESSED_REVIEWS_FILE)
    yield
    if os.path.exists(PROCESSED_REVIEWS_FILE):
        os.remove(PROCESSED_REVIEWS_FILE)

def test_get_recent_reviews_success(setup_test_data):
    """Test successful retrieval of recent reviews"""
    with patch('app_review_monitor.core.Api') as mock_api:
        mock_api.return_value.get_reviews.return_value = MOCK_REVIEWS
        reviews = get_recent_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 2
        assert reviews[0]['id'] == 'test_review_1'
        assert reviews[1]['id'] == 'test_review_2'

def test_get_recent_reviews_api_error(setup_test_data):
    """Test handling of API errors"""
    with patch('app_review_monitor.core.Api') as mock_api:
        mock_api.return_value.get_reviews.side_effect = Exception(ERROR_SCENARIOS['api_connection'])
        with pytest.raises(Exception) as exc_info:
            get_recent_reviews(TEST_APP_ID, days=1)
        assert str(exc_info.value) == ERROR_SCENARIOS['api_connection']

def test_process_reviews(setup_test_data):
    """Test review processing and filtering"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 2
        assert reviews[0]['rating'] == 5
        assert reviews[1]['rating'] == 1

def test_send_slack_notification(setup_test_data):
    """Test Slack notification sending"""
    with patch('app_review_monitor.core.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        send_slack_notification(TEST_SLACK_WEBHOOK, MOCK_REVIEWS)
        mock_post.assert_called_once()

def test_send_slack_notification_error(setup_test_data):
    """Test handling of Slack notification errors"""
    with patch('app_review_monitor.core.requests.post') as mock_post:
        mock_post.side_effect = Exception("Slack API error")
        with pytest.raises(Exception) as exc_info:
            send_slack_notification(TEST_SLACK_WEBHOOK, MOCK_REVIEWS)
        assert str(exc_info.value) == "Slack API error"

def test_review_tracking(setup_test_data):
    """Test that processed reviews are tracked correctly"""
    # Process reviews first time
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 2

    # Process same reviews again
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 0  # Should be filtered out as already processed

def test_different_time_periods(setup_test_data):
    """Test review processing with different time periods"""
    for days in TEST_PERIODS:
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            mock_get_reviews.return_value = MOCK_REVIEWS
            reviews = process_reviews(TEST_APP_ID, days=days)
            assert len(reviews) == 2  # All reviews should be included for longer periods

def test_special_characters(setup_test_data):
    """Test handling of reviews with special characters"""
    special_review = {
        "type": "customerReviews",
        "id": "test_review_special",
        "attributes": {
            "rating": 5,
            "title": "Special chars: !@#$%^&*",
            "body": "Emojis: 😊 🌟 💪",
            "reviewerNickname": "TestUser3",
            "createdDate": datetime.now().isoformat(),
            "territory": "USA"
        }
    }
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = [special_review]
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 1
        assert reviews[0]['id'] == 'test_review_special' 