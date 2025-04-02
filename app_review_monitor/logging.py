import logging
import logging.handlers
import os
import json
from logging.handlers import RotatingFileHandler

class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""
    def format(self, record):
        log_obj = {
            "asctime": self.formatTime(record),
            "levelname": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "taskName": getattr(record, "taskName", None)
        }
        
        # Add extra fields from the record
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in log_obj and not key.startswith("_"):
                    log_obj[key] = value
        
        return json.dumps(log_obj)

def setup_logging(debug: bool = False) -> logging.Logger:
    """
    Configure logging with appropriate level and format.
    
    Args:
        debug: Whether to enable debug logging
        
    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger('app_review_monitor')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

def get_logger(name):
    """Get a logger instance.

    Args:
        name (str): Name for the logger.

    Returns:
        logging.Logger: Logger instance.
    """
    return logging.getLogger(name) 
    return logger 