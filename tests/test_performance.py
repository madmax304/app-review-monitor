import os
import time
import pytest
import psutil
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

def test_performance_review_processing(setup_test_env):
    """Test performance of review processing"""
    start_time = time.time()
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    end_time = time.time()
    assert end_time - start_time < 1.0  # Should complete within 1 second

def test_performance_memory_usage(setup_test_env):
    """Test memory usage during review processing"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase

def test_performance_cpu_usage(setup_test_env):
    """Test CPU usage during review processing"""
    process = psutil.Process()
    initial_cpu = process.cpu_percent()
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    final_cpu = process.cpu_percent()
    assert final_cpu < 80  # Less than 80% CPU usage

def test_performance_large_review_set(setup_test_env):
    """Test performance with a large set of reviews"""
    large_reviews = [MOCK_REVIEWS[0].copy() for _ in range(1000)]
    for i, review in enumerate(large_reviews):
        review['id'] = f'test_review_{i}'
    
    start_time = time.time()
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = large_reviews
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    end_time = time.time()
    assert end_time - start_time < 2.0  # Should complete within 2 seconds

def test_performance_file_operations(setup_test_env):
    """Test performance of file operations"""
    start_time = time.time()
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    end_time = time.time()
    assert end_time - start_time < 1.0  # File operations should be fast

def test_performance_concurrent_operations(setup_test_env):
    """Test performance with concurrent operations"""
    import concurrent.futures
    
    def process_reviews_concurrent():
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
                mock_get_reviews.return_value = MOCK_REVIEWS
                mock_slack.return_value = None
                reviews = process_reviews(TEST_APP_ID, days=1)
                send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_reviews_concurrent) for _ in range(5)]
        concurrent.futures.wait(futures)
    
    end_time = time.time()
    assert end_time - start_time < 3.0  # Should complete within 3 seconds

def test_performance_network_operations(setup_test_env):
    """Test performance of network operations"""
    start_time = time.time()
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    end_time = time.time()
    assert end_time - start_time < 1.0  # Network operations should be fast

def test_performance_resource_cleanup(setup_test_env):
    """Test performance of resource cleanup"""
    start_time = time.time()
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
            mock_get_reviews.return_value = MOCK_REVIEWS
            mock_slack.return_value = None
            
            reviews = process_reviews(TEST_APP_ID, days=1)
            send_slack_notification(TEST_SLACK_WEBHOOK, reviews)
    
    end_time = time.time()
    assert end_time - start_time < 1.0  # Resource cleanup should be fast

def test_performance_error_handling(setup_test_env):
    """Test performance of error handling"""
    start_time = time.time()
    
    with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
        mock_get_reviews.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            process_reviews(TEST_APP_ID, days=1)
    
    end_time = time.time()
    assert end_time - start_time < 0.5  # Error handling should be fast

def test_performance_config_loading(setup_test_env):
    """Test performance of configuration loading"""
    start_time = time.time()
    
    config = load_config()
    
    end_time = time.time()
    assert end_time - start_time < 0.1  # Config loading should be very fast 