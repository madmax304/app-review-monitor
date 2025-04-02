import os
import pytest
from unittest.mock import patch, MagicMock
from app_review_monitor.core import process_reviews, send_slack_notification
from app_review_monitor.config import load_config
from tests.test_config import (
    TEST_APP_ID,
    TEST_APP_NAME,
    TEST_SLACK_WEBHOOK,
    MOCK_REVIEWS,
    TEST_DATA_DIR
)

@pytest.fixture
def setup_test_env():
    """Setup test environment"""
    os.environ['APP_ID'] = TEST_APP_ID
    os.environ['APP_NAME'] = TEST_APP_NAME
    os.environ['SLACK_WEBHOOK'] = TEST_SLACK_WEBHOOK
    yield
    # Cleanup
    for key in ['APP_ID', 'APP_NAME', 'SLACK_WEBHOOK']:
        if key in os.environ:
            del os.environ[key]

def test_complete_workflow_success(setup_test_env):
    """Test complete workflow with successful execution"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            # Process reviews
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 2
            
            # Send notifications
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            mock_slack.assert_called_once()

def test_complete_workflow_no_reviews(setup_test_env):
    """Test complete workflow with no new reviews"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = []
            mock_slack.return_value = None
            
            # Process reviews
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 0
            
            # Send notifications
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            mock_slack.assert_called_once()

def test_complete_workflow_api_error(setup_test_env):
    """Test complete workflow with API error"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            process_reviews(TEST_APP_ID, days=1)
        assert str(exc_info.value) == "API Error"

def test_complete_workflow_slack_error(setup_test_env):
    """Test complete workflow with Slack error"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.side_effect = Exception("Slack Error")
            
            # Process reviews
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 2
            
            # Send notifications
            with pytest.raises(Exception) as exc_info:
                send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            assert str(exc_info.value) == "Slack Error"

def test_complete_workflow_config_error():
    """Test complete workflow with configuration error"""
    with pytest.raises(ValueError) as exc_info:
        load_config()
    assert "APP_ID is required" in str(exc_info.value)

def test_complete_workflow_review_tracking(setup_test_env):
    """Test complete workflow with review tracking"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            # First run
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 2
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            
            # Second run with same reviews
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 0
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)

def test_complete_workflow_different_periods(setup_test_env):
    """Test complete workflow with different time periods"""
    for days in [1, 7, 30]:
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
                mock_get_reviews.return_value = MOCK_REVIEWS
                mock_slack.return_value = None
                
                reviews = process_reviews(TEST_APP_ID, days=days)
                assert len(reviews) == 2
                send_slack_notification(TEST_SLACK_WEBHOOK, reviews)

def test_complete_workflow_mixed_reviews(setup_test_env):
    """Test complete workflow with mix of new and processed reviews"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            # First run with one review
            mock_get_reviews.return_value = [MOCK_REVIEWS[0]]
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 1
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            
            # Second run with both reviews
            mock_get_reviews.return_value = MOCK_REVIEWS
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 1
            assert reviews[0]['id'] == 'test_review_2'
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)

def test_complete_workflow_performance(setup_test_env):
    """Test complete workflow performance"""
    import time
    start_time = time.time()
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    end_time = time.time()
    assert end_time - start_time < 1.0  # Complete workflow should take less than 1 second 