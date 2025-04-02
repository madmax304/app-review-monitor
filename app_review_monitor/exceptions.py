class AppReviewMonitorError(Exception):
    """Base exception class for App Review Monitor."""
    pass

class APIError(AppReviewMonitorError):
    """Raised when there is an error with the App Store Connect API."""
    pass

class SlackError(AppReviewMonitorError):
    """Raised when there is an error sending notifications to Slack."""
    pass

class ConfigurationError(AppReviewMonitorError):
    """Raised when there is an error with the configuration."""
    pass 