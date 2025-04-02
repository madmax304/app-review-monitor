import os
from typing import Dict
from dotenv import load_dotenv
from .exceptions import ConfigurationError

def validate_config(config: Dict) -> None:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    required_keys = ["app_id", "app_name", "slack_webhook"]
    
    # Check for missing keys
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ConfigurationError(f"Missing required configuration keys: {', '.join(missing_keys)}")
    
    # Check for empty values
    empty_keys = [key for key in required_keys if not str(config.get(key, '')).strip()]
    if empty_keys:
        raise ConfigurationError(f"Configuration values cannot be empty: {', '.join(empty_keys)}")
    
    # Validate app_id format
    try:
        app_id = str(config["app_id"]).strip()
        if not app_id.isdigit():
            raise ConfigurationError("Invalid APP_ID format - must be numeric")
    except (TypeError, ValueError):
        raise ConfigurationError("Invalid APP_ID format - must be numeric")
    
    # Validate slack_webhook format
    webhook = str(config["slack_webhook"]).strip()
    if not webhook.startswith(("https://hooks.slack.com/", "https://slack.com/")):
        raise ConfigurationError("Invalid SLACK_WEBHOOK format - must be a valid Slack webhook URL")

def load_config(config_file: str = None) -> Dict:
    """
    Load configuration from environment variables or config file.
    
    Args:
        config_file: Optional path to config file
        
    Returns:
        Dictionary containing configuration values
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    load_dotenv(config_file)
    
    # Load environment variables with default empty strings
    config = {
        "app_id": os.getenv("APP_ID", "").strip(),
        "app_name": os.getenv("APP_NAME", "").strip(),
        "slack_webhook": os.getenv("SLACK_WEBHOOK", "").strip(),
        "slack_channel": os.getenv("SLACK_CHANNEL", "#app-reviews").strip(),
        "log_level": os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        "days_to_look_back": int(os.getenv("DAYS_TO_LOOK_BACK", "1"))
    }
    
    validate_config(config)
    return config 