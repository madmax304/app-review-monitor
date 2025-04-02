import os
import logging
import pytest
from unittest.mock import patch, MagicMock
from app_review_monitor.logging import setup_logging, get_logger
from tests.test_config import TEST_DATA_DIR

@pytest.fixture
def setup_test_logs():
    """Setup test log directory"""
    log_dir = os.path.join(TEST_DATA_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    yield log_dir
    # Cleanup log files
    for file in os.listdir(log_dir):
        if file.endswith('.log'):
            os.remove(os.path.join(log_dir, file))

def test_setup_logging_success(setup_test_logs):
    """Test successful logging setup"""
    log_dir = setup_test_logs
    setup_logging(log_dir)
    logger = get_logger(__name__)
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO

def test_setup_logging_file_creation(setup_test_logs):
    """Test log file creation"""
    log_dir = setup_test_logs
    setup_logging(log_dir)
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    assert len(log_files) > 0

def test_setup_logging_file_permissions(setup_test_logs):
    """Test log file permissions"""
    log_dir = setup_test_logs
    setup_logging(log_dir)
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    for log_file in log_files:
        file_path = os.path.join(log_dir, log_file)
        assert os.access(file_path, os.W_OK)

def test_logger_message_formatting(setup_test_logs):
    """Test log message formatting"""
    log_dir = setup_test_logs
    setup_logging(log_dir)
    logger = get_logger(__name__)
    
    # Test different log levels
    test_message = "Test log message"
    logger.info(test_message)
    logger.error(test_message)
    
    # Verify log file contents
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    with open(os.path.join(log_dir, log_files[0]), 'r') as f:
        log_content = f.read()
        assert test_message in log_content
        assert "INFO" in log_content
        assert "ERROR" in log_content

def test_logger_exception_handling(setup_test_logs):
    """Test logging of exceptions"""
    log_dir = setup_test_logs
    setup_logging(log_dir)
    logger = get_logger(__name__)
    
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        logger.exception("Exception occurred")
    
    # Verify log file contents
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    with open(os.path.join(log_dir, log_files[0]), 'r') as f:
        log_content = f.read()
        assert "Test exception" in log_content
        assert "ValueError" in log_content
        assert "Exception occurred" in log_content

def test_logger_rotation(setup_test_logs):
    """Test log file rotation"""
    log_dir = setup_test_logs
    setup_logging(log_dir)
    logger = get_logger(__name__)
    
    # Generate enough log messages to trigger rotation
    for i in range(1000):
        logger.info(f"Test message {i}")
    
    # Verify log files
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    assert len(log_files) > 1  # Should have multiple log files due to rotation

def test_logger_different_levels(setup_test_logs):
    """Test different log levels"""
    log_dir = setup_test_logs
    setup_logging(log_dir)
    logger = get_logger(__name__)
    
    # Test all log levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    # Verify log file contents
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    with open(os.path.join(log_dir, log_files[0]), 'r') as f:
        log_content = f.read()
        assert "Debug message" not in log_content  # Debug should be filtered
        assert "Info message" in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content
        assert "Critical message" in log_content

def test_logger_context(setup_test_logs):
    """Test logging with context"""
    log_dir = setup_test_logs
    setup_logging(log_dir)
    logger = get_logger(__name__)
    
    # Test logging with context
    logger.info("Message with context", extra={'context': 'test_context'})
    
    # Verify log file contents
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    with open(os.path.join(log_dir, log_files[0]), 'r') as f:
        log_content = f.read()
        assert "Message with context" in log_content
        assert "test_context" in log_content

def test_logger_performance(setup_test_logs):
    """Test logging performance"""
    log_dir = setup_test_logs
    setup_logging(log_dir)
    logger = get_logger(__name__)
    
    # Test logging performance with many messages
    import time
    start_time = time.time()
    for i in range(1000):
        logger.info(f"Performance test message {i}")
    end_time = time.time()
    
    # Logging 1000 messages should take less than 1 second
    assert end_time - start_time < 1.0 