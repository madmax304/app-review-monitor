import pytest
from unittest.mock import patch, MagicMock
from app_review_monitor.core import get_recent_reviews
from tests.test_config import (
    TEST_APP_ID,
    TEST_APP_NAME,
    MOCK_REVIEWS,
    ERROR_SCENARIOS
)

def test_get_recent_reviews_success():
    """Test successful API request for recent reviews"""
    with patch('app_review_monitor.core.Api') as mock_api:
        mock_api.return_value.get_reviews.return_value = MOCK_REVIEWS
        reviews = get_recent_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 2
        assert reviews[0]['id'] == 'test_review_1'
        assert reviews[1]['id'] == 'test_review_2'

def test_get_recent_reviews_api_connection_error():
    """Test handling of API connection errors"""
    with patch('app_review_monitor.core.Api') as mock_api:
        mock_api.return_value.get_reviews.side_effect = Exception(ERROR_SCENARIOS['api_connection'])
        with pytest.raises(Exception) as exc_info:
            get_recent_reviews(TEST_APP_ID, days=1)
        assert str(exc_info.value) == ERROR_SCENARIOS['api_connection']

def test_get_recent_reviews_invalid_credentials():
    """Test handling of invalid credentials"""
    with patch('app_review_monitor.core.Api') as mock_api:
        mock_api.return_value.get_reviews.side_effect = Exception(ERROR_SCENARIOS['invalid_credentials'])
        with pytest.raises(Exception) as exc_info:
            get_recent_reviews(TEST_APP_ID, days=1)
        assert str(exc_info.value) == ERROR_SCENARIOS['invalid_credentials']

def test_get_recent_reviews_rate_limit():
    """Test handling of rate limiting"""
    with patch('app_review_monitor.core.Api') as mock_api:
        mock_api.return_value.get_reviews.side_effect = Exception(ERROR_SCENARIOS['rate_limit'])
        with pytest.raises(Exception) as exc_info:
            get_recent_reviews(TEST_APP_ID, days=1)
        assert str(exc_info.value) == ERROR_SCENARIOS['rate_limit']

def test_get_recent_reviews_timeout():
    """Test handling of request timeouts"""
    with patch('app_review_monitor.core.Api') as mock_api:
        mock_api.return_value.get_reviews.side_effect = Exception(ERROR_SCENARIOS['timeout'])
        with pytest.raises(Exception) as exc_info:
            get_recent_reviews(TEST_APP_ID, days=1)
        assert str(exc_info.value) == ERROR_SCENARIOS['timeout']

def test_get_recent_reviews_empty_response():
    """Test handling of empty API response"""
    with patch('app_review_monitor.core.Api') as mock_api:
        mock_api.return_value.get_reviews.return_value = []
        reviews = get_recent_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 0

def test_get_recent_reviews_invalid_response():
    """Test handling of invalid API response format"""
    with patch('app_review_monitor.core.Api') as mock_api:
        mock_api.return_value.get_reviews.return_value = {"invalid": "format"}
        with pytest.raises(Exception) as exc_info:
            get_recent_reviews(TEST_APP_ID, days=1)
        assert "Invalid response format" in str(exc_info.value)

def test_get_recent_reviews_different_time_periods():
    """Test API requests with different time periods"""
    for days in [1, 7, 30]:
        with patch('app_review_monitor.core.Api') as mock_api:
            mock_api.return_value.get_reviews.return_value = MOCK_REVIEWS
            reviews = get_recent_reviews(TEST_APP_ID, days=days)
            assert len(reviews) == 2
            mock_api.return_value.get_reviews.assert_called_with(
                TEST_APP_ID,
                filter_rating=None,
                filter_territory=None,
                sort='-createdDate',
                limit=100
            )

def test_get_recent_reviews_retry():
    """Test API request retry mechanism"""
    with patch('app_review_monitor.core.Api') as mock_api:
        # First call fails, second call succeeds
        mock_api.return_value.get_reviews.side_effect = [
            Exception("Temporary error"),
            MOCK_REVIEWS
        ]
        reviews = get_recent_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 2
        assert mock_api.return_value.get_reviews.call_count == 2 