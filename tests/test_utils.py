import pytest
from datetime import datetime, timedelta
from app_review_monitor.utils import (
    format_date,
    parse_date,
    truncate_string,
    sanitize_string,
    calculate_date_range
)
import pytz

def test_format_date():
    """Test date formatting"""
    test_date = datetime(2024, 1, 1, 12, 0, 0)
    formatted_date = format_date(test_date)
    assert formatted_date == "2024-01-01 12:00:00"

def test_format_date_none():
    """Test date formatting with None value"""
    formatted_date = format_date(None)
    assert formatted_date == "None"

def test_parse_date():
    """Test date parsing"""
    date_string = "2024-01-01 12:00:00"
    parsed_date = parse_date(date_string)
    assert isinstance(parsed_date, datetime)
    assert parsed_date.year == 2024
    assert parsed_date.month == 1
    assert parsed_date.day == 1
    assert parsed_date.hour == 12
    assert parsed_date.minute == 0
    assert parsed_date.second == 0

def test_parse_date_invalid():
    """Test date parsing with invalid string"""
    with pytest.raises(ValueError):
        parse_date("invalid_date")

def test_parse_date_none():
    """Test date parsing with None value"""
    parsed_date = parse_date(None)
    assert parsed_date is None

def test_truncate_string():
    """Test string truncation"""
    test_string = "This is a very long string that needs to be truncated"
    truncated = truncate_string(test_string, max_length=20)
    assert len(truncated) <= 20
    assert truncated.endswith("...")

def test_truncate_string_short():
    """Test string truncation with short string"""
    test_string = "Short string"
    truncated = truncate_string(test_string, max_length=20)
    assert truncated == test_string

def test_truncate_string_empty():
    """Test string truncation with empty string"""
    truncated = truncate_string("", max_length=20)
    assert truncated == ""

def test_sanitize_string():
    """Test string sanitization"""
    test_string = "Test\nString\tWith\rSpecial\nCharacters"
    sanitized = sanitize_string(test_string)
    assert sanitized == "Test String With Special Characters"

def test_sanitize_string_empty():
    """Test string sanitization with empty string"""
    sanitized = sanitize_string("")
    assert sanitized == ""

def test_sanitize_string_none():
    """Test string sanitization with None value"""
    sanitized = sanitize_string(None)
    assert sanitized == ""

def test_calculate_date_range():
    """Test date range calculation"""
    end_date = datetime(2024, 1, 1)
    days = 7
    start_date = calculate_date_range(end_date, days)
    assert start_date == end_date - timedelta(days=days)

def test_calculate_date_range_zero_days():
    """Test date range calculation with zero days"""
    end_date = datetime(2024, 1, 1)
    days = 0
    start_date = calculate_date_range(end_date, days)
    assert start_date == end_date

def test_calculate_date_range_negative_days():
    """Test date range calculation with negative days"""
    end_date = datetime(2024, 1, 1)
    days = -1
    with pytest.raises(ValueError):
        calculate_date_range(end_date, days)

def test_calculate_date_range_none():
    """Test date range calculation with None value"""
    with pytest.raises(ValueError):
        calculate_date_range(None, 7)

def test_format_date_different_formats():
    """Test date formatting with different formats"""
    test_date = datetime(2024, 1, 1, 12, 0, 0)
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%Y/%m/%d"
    ]
    for fmt in formats:
        formatted = format_date(test_date, fmt)
        parsed = parse_date(formatted, fmt)
        assert parsed == test_date

def test_sanitize_string_special_characters():
    """Test string sanitization with special characters"""
    test_string = "Test!@#$%^&*()_+String"
    sanitized = sanitize_string(test_string)
    assert sanitized == "Test!@#$%^&*()_+String"  # Special characters should be preserved

def test_truncate_string_unicode():
    """Test string truncation with Unicode characters"""
    test_string = "Test string with Unicode: 🌟 💪 😊"
    truncated = truncate_string(test_string, max_length=20)
    assert len(truncated) <= 20
    assert truncated.endswith("...")

def test_calculate_date_range_timezone():
    """Test date range calculation with timezone-aware dates"""
    end_date = datetime(2024, 1, 1, tzinfo=pytz.UTC)
    days = 7
    start_date = calculate_date_range(end_date, days)
    assert start_date.tzinfo == end_date.tzinfo
    assert start_date == end_date - timedelta(days=days) 