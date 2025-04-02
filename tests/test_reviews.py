import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app_review_monitor.core import get_recent_reviews, process_reviews, load_processed_reviews, save_processed_reviews
from tests.test_config import (
    TEST_APP_ID,
    TEST_APP_NAME,
    MOCK_REVIEWS,
    TEST_PERIODS,
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

def test_load_processed_reviews_empty(setup_test_data):
    """Test loading processed reviews when file doesn't exist"""
    processed_reviews = load_processed_reviews()
    assert processed_reviews == set()

def test_save_and_load_processed_reviews(setup_test_data):
    """Test saving and loading processed reviews"""
    review_ids = {'test_review_1', 'test_review_2'}
    save_processed_reviews(review_ids)
    loaded_reviews = load_processed_reviews()
    assert loaded_reviews == review_ids

def test_process_reviews_new(setup_test_data):
    """Test processing new reviews"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 2
        assert reviews[0]['id'] == 'test_review_1'
        assert reviews[1]['id'] == 'test_review_2'

def test_process_reviews_already_processed(setup_test_data):
    """Test processing already processed reviews"""
    # First process
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 2

    # Second process with same reviews
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 0

def test_process_reviews_mixed(setup_test_data):
    """Test processing mix of new and processed reviews"""
    # First process
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = [MOCK_REVIEWS[0]]
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 1

    # Second process with mix of old and new reviews
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 1
        assert reviews[0]['id'] == 'test_review_2'

def test_process_reviews_different_periods(setup_test_data):
    """Test processing reviews with different time periods"""
    for days in TEST_PERIODS:
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            mock_get_reviews.return_value = MOCK_REVIEWS
            reviews = process_reviews(TEST_APP_ID, days=days)
            assert len(reviews) == 2

def test_process_reviews_empty(setup_test_data):
    """Test processing when no reviews are found"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = []
        reviews = process_reviews(TEST_APP_ID, days=1)
        assert len(reviews) == 0

def test_process_reviews_api_error(setup_test_data):
    """Test handling of API errors during review processing"""
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.side_effect = Exception("API Error")
        with pytest.raises(Exception) as exc_info:
            process_reviews(TEST_APP_ID, days=1)
        assert str(exc_info.value) == "API Error"

def test_process_reviews_file_error(setup_test_data):
    """Test handling of file system errors during review processing"""
    # Create a directory that can't be written to
    os.chmod(TEST_DATA_DIR, 0o444)
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = MOCK_REVIEWS
        with pytest.raises(Exception) as exc_info:
            process_reviews(TEST_APP_ID, days=1)
        assert "Failed to save processed reviews" in str(exc_info.value)
    
    # Restore directory permissions
    os.chmod(TEST_DATA_DIR, 0o755) 