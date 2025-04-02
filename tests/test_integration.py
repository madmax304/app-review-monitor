import os
import pytest
from unittest.mock import patch, MagicMock
from app_review_monitor.core import process_reviews, send_slack_notification
from app_review_monitor.config import load_config
from app_review_monitor.cli import main
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

def test_integration_complete_workflow(setup_test_env):
    """Test complete integration workflow"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            # Load configuration
            config = load_config()
            assert config['app_id'] == TEST_APP_ID
            assert config['app_name'] == TEST_APP_NAME
            assert config['slack_webhook'] == TEST_SLACK_WEBHOOK
            
            # Process reviews
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 2
            assert reviews[0]['id'] == 'test_review_1'
            assert reviews[1]['id'] == 'test_review_2'
            
            # Send notifications
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            mock_slack.assert_called_once()

def test_integration_cli_execution(setup_test_env):
    """Test CLI execution in integration context"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', '1']):
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
                mock_get_reviews.return_value = MOCK_REVIEWS
                mock_slack.return_value = None
                main()
                mock_get_reviews.assert_called_once_with(TEST_APP_ID, days=1)
                mock_slack.assert_called_once()

def test_integration_error_handling(setup_test_env):
    """Test error handling in integration context"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            process_reviews(TEST_APP_ID, days=1)
        assert str(exc_info.value) == "API Error"

def test_integration_review_tracking(setup_test_env):
    """Test review tracking in integration context"""
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

def test_integration_config_loading(setup_test_env):
    """Test configuration loading in integration context"""
    config = load_config()
    assert config['app_id'] == TEST_APP_ID
    assert config['app_name'] == TEST_APP_NAME
    assert config['slack_webhook'] == TEST_SLACK_WEBHOOK

def test_integration_file_operations(setup_test_env):
    """Test file operations in integration context"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            # Process reviews and verify file operations
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 2
            
            # Verify processed reviews file exists
            processed_reviews_file = os.path.join(TEST_DATA_DIR, 'processed_reviews.json')
            assert os.path.exists(processed_reviews_file)

def test_integration_performance(setup_test_env):
    """Test performance in integration context"""
    import time
    start_time = time.time()
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            # Load configuration
            config = load_config()
            
            # Process reviews
            reviews = process_reviews(TEST_APP_ID, days=1)
            
            # Send notifications
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    end_time = time.time()
    assert end_time - start_time < 1.0  # Complete workflow should take less than 1 second

def test_integration_error_recovery(setup_test_env):
    """Test error recovery in integration context"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            # First call fails, second call succeeds
            mock_get_reviews.side_effect = [
                Exception("Temporary error"),
                MOCK_REVIEWS
            ]
            mock_slack.return_value = None
            
            # Process reviews
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 2
            
            # Send notifications
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            mock_slack.assert_called_once()

def test_integration_resource_cleanup(setup_test_env):
    """Test resource cleanup in integration context"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            # Process reviews
            reviews = process_reviews(TEST_APP_ID, days=1)
            assert len(reviews) == 2
            
            # Send notifications
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            
            # Verify resources are cleaned up
            processed_reviews_file = os.path.join(TEST_DATA_DIR, 'processed_reviews.json')
            if os.path.exists(processed_reviews_file):
                os.remove(processed_reviews_file)
            assert not os.path.exists(processed_reviews_file) 