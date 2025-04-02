import os
import pytest
from unittest.mock import patch, MagicMock
from app_review_monitor.cli import main
from tests.test_config import (
    TEST_APP_ID,
    TEST_APP_NAME,
    TEST_SLACK_WEBHOOK,
    MOCK_REVIEWS
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

def test_cli_help():
    """Test CLI help command"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

def test_cli_dry_run(setup_test_env):
    """Test CLI dry run mode"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', '1', '--dry-run']):
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            mock_get_reviews.return_value = MOCK_REVIEWS
            main()
            mock_get_reviews.assert_called_once_with(TEST_APP_ID, days=1)

def test_cli_invalid_days():
    """Test CLI with invalid days parameter"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', 'invalid']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0

def test_cli_negative_days():
    """Test CLI with negative days parameter"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', '-1']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0

def test_cli_no_reviews(setup_test_env):
    """Test CLI when no new reviews are found"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', '1']):
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            mock_get_reviews.return_value = []
            main()
            mock_get_reviews.assert_called_once_with(TEST_APP_ID, days=1)

def test_cli_api_error(setup_test_env):
    """Test CLI handling of API errors"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', '1']):
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            mock_get_reviews.side_effect = Exception("API Error")
            with pytest.raises(Exception) as exc_info:
                main()
            assert str(exc_info.value) == "API Error"

def test_cli_slack_error(setup_test_env):
    """Test CLI handling of Slack notification errors"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', '1']):
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
                mock_get_reviews.return_value = MOCK_REVIEWS
                mock_slack.side_effect = Exception("Slack Error")
                with pytest.raises(Exception) as exc_info:
                    main()
                assert str(exc_info.value) == "Slack Error"

def test_cli_successful_run(setup_test_env):
    """Test successful CLI execution"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', '1']):
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
                mock_get_reviews.return_value = MOCK_REVIEWS
                mock_slack.return_value = None
                main()
                mock_get_reviews.assert_called_once_with(TEST_APP_ID, days=1)
                mock_slack.assert_called_once()

def test_cli_missing_required_args():
    """Test CLI with missing required arguments"""
    with patch('sys.argv', ['app_review_monitor/cli.py']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0

def test_cli_invalid_args():
    """Test CLI with invalid arguments"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--invalid-arg']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0

def test_cli_version():
    """Test CLI version command"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--version']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

def test_cli_verbose_mode(setup_test_env):
    """Test CLI verbose mode"""
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', '1', '--verbose']):
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
                mock_get_reviews.return_value = MOCK_REVIEWS
                mock_slack.return_value = None
                main()
                mock_get_reviews.assert_called_once_with(TEST_APP_ID, days=1)
                mock_slack.assert_called_once()

def test_cli_config_file(setup_test_env):
    """Test CLI with custom config file"""
    config_file = 'test_config.env'
    with patch('sys.argv', ['app_review_monitor/cli.py', '--days', '1', '--config', config_file]):
        with patch('app_review_monitor.core.get_recent_reviews') as mock_get_reviews:
            with patch('app_review_monitor.core.send_slack_notification') as mock_slack:
                mock_get_reviews.return_value = MOCK_REVIEWS
                mock_slack.return_value = None
                main()
                mock_get_reviews.assert_called_once_with(TEST_APP_ID, days=1)
                mock_slack.assert_called_once() 