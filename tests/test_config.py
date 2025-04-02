import os
from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock
from app_review_monitor.config import load_config, validate_config

# Test configuration
TEST_APP_ID = "6596773195"
TEST_APP_NAME = "Natal"
TEST_SLACK_WEBHOOK = os.getenv("TEST_SLACK_WEBHOOK", "https://hooks.slack.com/services/test/test/test")

# Mock review data
MOCK_REVIEWS = [
    {
        "type": "customerReviews",
        "id": "test_review_1",
        "attributes": {
            "rating": 5,
            "title": "Great app!",
            "body": "This is a test review with emojis 😊",
            "reviewerNickname": "TestUser1",
            "createdDate": (datetime.now() - timedelta(hours=1)).isoformat(),
            "territory": "USA"
        }
    },
    {
        "type": "customerReviews",
        "id": "test_review_2",
        "attributes": {
            "rating": 1,
            "title": "Not working",
            "body": "This is a negative review with special chars: !@#$%^&*",
            "reviewerNickname": "TestUser2",
            "createdDate": (datetime.now() - timedelta(hours=2)).isoformat(),
            "territory": "CAN"
        }
    }
]

# Test time periods
TEST_PERIODS = [1, 7, 30]  # days

# Error scenarios
ERROR_SCENARIOS = {
    "api_connection": "Connection refused",
    "invalid_credentials": "Invalid credentials",
    "rate_limit": "Rate limit exceeded",
    "timeout": "Request timed out"
}

# Test file paths
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
PROCESSED_REVIEWS_FILE = os.path.join(TEST_DATA_DIR, "processed_reviews.json")

def test_load_config_success():
    """Test successful loading of configuration"""
    config = {
        'app_id': TEST_APP_ID,
        'app_name': TEST_APP_NAME,
        'slack_webhook': TEST_SLACK_WEBHOOK
    }
    with patch('app_review_monitor.config.load_dotenv') as mock_load_dotenv:
        with patch.dict(os.environ, config):
            loaded_config = load_config()
            assert loaded_config['app_id'] == TEST_APP_ID
            assert loaded_config['app_name'] == TEST_APP_NAME
            assert loaded_config['slack_webhook'] == TEST_SLACK_WEBHOOK

def test_load_config_missing_app_id():
    """Test loading configuration with missing app_id"""
    config = {
        'app_name': TEST_APP_NAME,
        'slack_webhook': TEST_SLACK_WEBHOOK
    }
    with patch('app_review_monitor.config.load_dotenv') as mock_load_dotenv:
        with patch.dict(os.environ, config):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            assert "APP_ID is required" in str(exc_info.value)

def test_load_config_missing_app_name():
    """Test loading configuration with missing app_name"""
    config = {
        'app_id': TEST_APP_ID,
        'slack_webhook': TEST_SLACK_WEBHOOK
    }
    with patch('app_review_monitor.config.load_dotenv') as mock_load_dotenv:
        with patch.dict(os.environ, config):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            assert "APP_NAME is required" in str(exc_info.value)

def test_load_config_missing_slack_webhook():
    """Test loading configuration with missing slack_webhook"""
    config = {
        'app_id': TEST_APP_ID,
        'app_name': TEST_APP_NAME
    }
    with patch('app_review_monitor.config.load_dotenv') as mock_load_dotenv:
        with patch.dict(os.environ, config):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            assert "SLACK_WEBHOOK is required" in str(exc_info.value)

def test_load_config_invalid_app_id():
    """Test loading configuration with invalid app_id"""
    config = {
        'app_id': 'invalid_id',
        'app_name': TEST_APP_NAME,
        'slack_webhook': TEST_SLACK_WEBHOOK
    }
    with patch('app_review_monitor.config.load_dotenv') as mock_load_dotenv:
        with patch.dict(os.environ, config):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            assert "Invalid APP_ID format" in str(exc_info.value)

def test_load_config_invalid_slack_webhook():
    """Test loading configuration with invalid slack_webhook"""
    config = {
        'app_id': TEST_APP_ID,
        'app_name': TEST_APP_NAME,
        'slack_webhook': 'invalid_webhook'
    }
    with patch('app_review_monitor.config.load_dotenv') as mock_load_dotenv:
        with patch.dict(os.environ, config):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            assert "Invalid SLACK_WEBHOOK format" in str(exc_info.value)

def test_validate_config_success():
    """Test successful configuration validation"""
    config = {
        'app_id': TEST_APP_ID,
        'app_name': TEST_APP_NAME,
        'slack_webhook': TEST_SLACK_WEBHOOK
    }
    validate_config(config)

def test_validate_config_missing_keys():
    """Test configuration validation with missing keys"""
    config = {}
    with pytest.raises(ValueError) as exc_info:
        validate_config(config)
    assert "Missing required configuration keys" in str(exc_info.value)

def test_validate_config_invalid_types():
    """Test configuration validation with invalid types"""
    config = {
        'app_id': 123,  # Should be string
        'app_name': TEST_APP_NAME,
        'slack_webhook': TEST_SLACK_WEBHOOK
    }
    with pytest.raises(ValueError) as exc_info:
        validate_config(config)
    assert "Invalid configuration value types" in str(exc_info.value)

def test_validate_config_empty_values():
    """Test configuration validation with empty values"""
    config = {
        'app_id': '',
        'app_name': '',
        'slack_webhook': ''
    }
    with pytest.raises(ValueError) as exc_info:
        validate_config(config)
    assert "Configuration values cannot be empty" in str(exc_info.value)

def test_load_config_from_file():
    """Test loading configuration from file"""
    config_content = f"""
    APP_ID={TEST_APP_ID}
    APP_NAME={TEST_APP_NAME}
    SLACK_WEBHOOK={TEST_SLACK_WEBHOOK}
    """
    with patch('app_review_monitor.config.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = config_content
        loaded_config = load_config()
        assert loaded_config['app_id'] == TEST_APP_ID
        assert loaded_config['app_name'] == TEST_APP_NAME
        assert loaded_config['slack_webhook'] == TEST_SLACK_WEBHOOK 