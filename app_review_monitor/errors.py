class AppReviewMonitorError(Exception):
    """Base exception class for App Review Monitor."""
    def __init__(self, message, cause=None, context=None):
        super().__init__(message)
        self.message = message
        self.cause = cause
        self.context = context or {}

class APIError(AppReviewMonitorError):
    """Exception raised for API-related errors."""
    def __init__(self, message, details=None, **kwargs):
        super().__init__(message, **kwargs)
        self.details = details or {}

class ConfigurationError(AppReviewMonitorError):
    """Exception raised for configuration-related errors."""
    def __init__(self, message, missing_keys=None, **kwargs):
        super().__init__(message, **kwargs)
        self.missing_keys = missing_keys or []

class SlackError(AppReviewMonitorError):
    """Exception raised for Slack notification errors."""
    def __init__(self, message, response=None, **kwargs):
        super().__init__(message, **kwargs)
        self.response = response or {}

class ReviewProcessingError(AppReviewMonitorError):
    """Exception raised for review processing errors."""
    def __init__(self, message, review=None, **kwargs):
        super().__init__(message, **kwargs)
        self.review = review 