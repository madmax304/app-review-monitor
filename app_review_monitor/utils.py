from datetime import datetime, timedelta
import re

def format_date(date_obj, fmt="%Y-%m-%d %H:%M:%S"):
    """Format a datetime object to string.

    Args:
        date_obj (datetime): Datetime object to format.
        fmt (str, optional): Format string. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: Formatted date string.
    """
    if date_obj is None:
        return "None"
    return date_obj.strftime(fmt)

def parse_date(date_str, fmt="%Y-%m-%d %H:%M:%S"):
    """Parse a date string to datetime object.

    Args:
        date_str (str): Date string to parse.
        fmt (str, optional): Format string. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        datetime: Parsed datetime object.
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}")

def truncate_string(text, max_length=100):
    """Truncate a string to a maximum length.

    Args:
        text (str): String to truncate.
        max_length (int, optional): Maximum length. Defaults to 100.

    Returns:
        str: Truncated string.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def sanitize_string(text):
    """Sanitize a string by removing special characters.

    Args:
        text (str): String to sanitize.

    Returns:
        str: Sanitized string.
    """
    if not text:
        return ""
    # Replace newlines and tabs with spaces
    text = re.sub(r'[\n\t\r]+', ' ', text)
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def calculate_date_range(end_date, days):
    """Calculate the start date based on end date and number of days.

    Args:
        end_date (datetime): End date.
        days (int): Number of days to look back.

    Returns:
        datetime: Start date.
    """
    if end_date is None:
        raise ValueError("End date cannot be None")
    if days < 0:
        raise ValueError("Days cannot be negative")
    return end_date - timedelta(days=days) 