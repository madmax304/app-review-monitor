import pytest
from app_review_monitor.errors import (
    AppReviewMonitorError,
    APIError,
    ConfigurationError,
    SlackError,
    ReviewProcessingError
)

def test_app_review_monitor_error():
    """Test base AppReviewMonitorError"""
    error = AppReviewMonitorError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)

def test_api_error():
    """Test APIError"""
    error = APIError("API connection failed")
    assert str(error) == "API connection failed"
    assert isinstance(error, AppReviewMonitorError)

def test_api_error_with_details():
    """Test APIError with additional details"""
    error = APIError("API error", details={"status_code": 404, "endpoint": "/reviews"})
    assert str(error) == "API error"
    assert error.details == {"status_code": 404, "endpoint": "/reviews"}

def test_configuration_error():
    """Test ConfigurationError"""
    error = ConfigurationError("Missing required configuration")
    assert str(error) == "Missing required configuration"
    assert isinstance(error, AppReviewMonitorError)

def test_configuration_error_missing_keys():
    """Test ConfigurationError with missing keys"""
    error = ConfigurationError("Missing required configuration", missing_keys=["APP_ID", "APP_NAME"])
    assert str(error) == "Missing required configuration"
    assert error.missing_keys == ["APP_ID", "APP_NAME"]

def test_slack_error():
    """Test SlackError"""
    error = SlackError("Failed to send Slack notification")
    assert str(error) == "Failed to send Slack notification"
    assert isinstance(error, AppReviewMonitorError)

def test_slack_error_with_response():
    """Test SlackError with response details"""
    error = SlackError("Slack error", response={"status_code": 400, "text": "Bad Request"})
    assert str(error) == "Slack error"
    assert error.response == {"status_code": 400, "text": "Bad Request"}

def test_review_processing_error():
    """Test ReviewProcessingError"""
    error = ReviewProcessingError("Failed to process review")
    assert str(error) == "Failed to process review"
    assert isinstance(error, AppReviewMonitorError)

def test_review_processing_error_with_review():
    """Test ReviewProcessingError with review details"""
    review = {"id": "test_review", "rating": 5}
    error = ReviewProcessingError("Processing error", review=review)
    assert str(error) == "Processing error"
    assert error.review == review

def test_error_inheritance():
    """Test error class inheritance"""
    assert issubclass(APIError, AppReviewMonitorError)
    assert issubclass(ConfigurationError, AppReviewMonitorError)
    assert issubclass(SlackError, AppReviewMonitorError)
    assert issubclass(ReviewProcessingError, AppReviewMonitorError)

def test_error_attributes():
    """Test error attributes"""
    error = AppReviewMonitorError("Test error")
    assert hasattr(error, 'message')
    assert error.message == "Test error"

def test_error_with_cause():
    """Test error with cause"""
    cause = Exception("Original error")
    error = AppReviewMonitorError("Test error", cause=cause)
    assert str(error) == "Test error"
    assert error.cause == cause

def test_error_representation():
    """Test error string representation"""
    error = AppReviewMonitorError("Test error")
    assert repr(error) == "AppReviewMonitorError('Test error')"

def test_error_equality():
    """Test error equality"""
    error1 = AppReviewMonitorError("Test error")
    error2 = AppReviewMonitorError("Test error")
    assert error1 == error2

def test_error_inequality():
    """Test error inequality"""
    error1 = AppReviewMonitorError("Test error 1")
    error2 = AppReviewMonitorError("Test error 2")
    assert error1 != error2

def test_error_with_context():
    """Test error with context"""
    context = {"operation": "process_reviews", "app_id": "123"}
    error = AppReviewMonitorError("Test error", context=context)
    assert str(error) == "Test error"
    assert error.context == context

def test_error_chain():
    """Test error chaining"""
    try:
        try:
            raise Exception("Original error")
        except Exception as e:
            raise APIError("API error", cause=e)
    except APIError as e:
        assert str(e) == "API error"
        assert isinstance(e.cause, Exception)
        assert str(e.cause) == "Original error" 