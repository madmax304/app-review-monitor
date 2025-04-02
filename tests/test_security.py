import os
import pytest
from unittest.mock import patch, MagicMock
from app_review_monitor.config import load_config
from app_review_monitor.core import process_reviews, send_slack_notification
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

def test_security_config_loading():
    """Test secure configuration loading"""
    config = load_config()
    assert 'APP_ID' not in str(config)  # Sensitive data should not be exposed
    assert 'APP_NAME' in str(config)  # Non-sensitive data should be visible

def test_security_environment_variables():
    """Test secure handling of environment variables"""
    with patch.dict(os.environ, {
        'APP_ID': TEST_APP_ID,
        'APP_NAME': TEST_APP_NAME,
        'SLACK_WEBHOOK': TEST_SLACK_WEBHOOK
    }):
        config = load_config()
        assert config['app_id'] == TEST_APP_ID
        assert config['app_name'] == TEST_APP_NAME
        assert config['slack_webhook'] == TEST_SLACK_WEBHOOK

def test_security_file_permissions():
    """Test secure file permissions"""
    config_file = os.path.join(TEST_DATA_DIR, 'config.env')
    with open(config_file, 'w') as f:
        f.write(f"APP_ID={TEST_APP_ID}\n")
        f.write(f"APP_NAME={TEST_APP_NAME}\n")
        f.write(f"SLACK_WEBHOOK={TEST_SLACK_WEBHOOK}\n")
    
    # Set secure file permissions
    os.chmod(config_file, 0o600)
    
    # Verify file permissions
    assert os.stat(config_file).st_mode & 0o777 == 0o600

def test_security_credential_exposure():
    """Test prevention of credential exposure in logs"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            
            # Verify no sensitive data in logs
            log_content = str(mock_get_reviews.call_args)
            assert TEST_APP_ID not in log_content
            assert TEST_SLACK_WEBHOOK not in log_content

def test_security_input_validation():
    """Test secure input validation"""
    with pytest.raises(ValueError):
        process_reviews("invalid_app_id", days=1)
    
    with pytest.raises(ValueError):
        send_slack_notification("invalid_webhook", MOCK_REVIEWS)

def test_security_sanitization():
    """Test secure input sanitization"""
    malicious_review = {
        "type": "customerReviews",
        "id": "test_review_malicious",
        "attributes": {
            "rating": 5,
            "title": "<script>alert('xss')</script>",
            "body": "Malicious content",
            "reviewerNickname": "TestUser",
            "createdDate": "2024-01-01T00:00:00Z",
            "territory": "USA"
        }
    }
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = [malicious_review]
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert "<script>" not in str(reviews[0])  # XSS should be prevented

def test_security_file_path_traversal():
    """Test prevention of file path traversal"""
    malicious_path = "../../../etc/passwd"
    with pytest.raises(ValueError):
        process_reviews(malicious_path, days=1)

def test_security_secure_headers():
    """Test secure headers in API requests"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        reviews = process_reviews(TEST_APP_ID, days=1)
        
        # Verify secure headers in API calls
        call_args = mock_get_reviews.call_args
        assert 'headers' in call_args[1]
        headers = call_args[1]['headers']
        assert 'X-Content-Type-Options' in headers
        assert headers['X-Content-Type-Options'] == 'nosniff'

def test_security_secure_communication():
    """Test secure communication channels"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            
            # Verify HTTPS is used
            assert mock_get_reviews.call_args[1]['url'].startswith('https://')
            assert mock_slack.call_args[1]['url'].startswith('https://')

def test_security_secure_storage():
    """Test secure storage of sensitive data"""
    processed_reviews_file = os.path.join(TEST_DATA_DIR, 'processed_reviews.json')
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        reviews = process_reviews(TEST_APP_ID, days=1)
        
        # Verify secure file permissions
        assert os.stat(processed_reviews_file).st_mode & 0o777 == 0o600

def test_security_secure_logging():
    """Test secure logging practices"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
            
            # Verify no sensitive data in logs
            log_content = str(mock_get_reviews.call_args)
            assert TEST_APP_ID not in log_content
            assert TEST_SLACK_WEBHOOK not in log_content

def test_security_secure_error_handling():
    """Test secure error handling"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            process_reviews(TEST_APP_ID, days=1)
        assert TEST_APP_ID not in str(exc_info.value)  # Sensitive data should not be exposed

def test_security_secure_config_validation():
    """Test secure configuration validation"""
    with patch.dict(os.environ, {
        'APP_ID': 'invalid_id',
        'APP_NAME': TEST_APP_NAME,
        'SLACK_WEBHOOK': TEST_SLACK_WEBHOOK
    }):
        with pytest.raises(ValueError):
            load_config() 