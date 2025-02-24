"""Tests for main CLI functionality."""
import pytest
from unittest.mock import patch
from src.cli.main import main, create_parser

def test_parser_creation():
    """Test argument parser setup."""
    parser = create_parser()
    
    # Test required arguments
    with pytest.raises(SystemExit):
        parser.parse_args([])  # Missing required --env and command
    
    with pytest.raises(SystemExit):
        parser.parse_args(["--env", "test"])  # Missing required command
    
    # Test environment validation
    args = parser.parse_args(["--env", "test", "clean"])  # Valid command
    assert args.env == "test"
    assert args.command == "clean"
    assert not args.dry_run
    assert not args.debug
    
    # Test optional arguments
    args = parser.parse_args(["--env", "test", "--dry-run", "--debug", "clean"])
    assert args.dry_run
    assert args.debug
    assert args.command == "clean"

def test_main_no_command(cli_args: list[str]):
    """Test main function with no command."""
    with pytest.raises(SystemExit) as exc_info:
        main(cli_args)
    assert exc_info.value.code == 2  # argparse exits with code 2 for argument errors

def test_main_invalid_env():
    """Test main function with invalid environment."""
    with pytest.raises(SystemExit):
        main(["--env", "invalid"])

def test_main_debug(debug_args: list[str]):
    """Test main function with debug enabled but no command."""
    with pytest.raises(SystemExit) as exc_info:
        main(debug_args)
    assert exc_info.value.code == 2

def test_main_dry_run(dry_run_args: list[str]):
    """Test main function with dry run enabled but no command."""
    with pytest.raises(SystemExit) as exc_info:
        main(dry_run_args)
    assert exc_info.value.code == 2

def test_main_valid_command():
    """Test main function with a valid command."""
    # Mock dependencies to prevent slow initialization
    with patch('src.cli.commands.clean.process_episodes') as mock_process, \
         patch('src.cli.commands.clean.get_episodes') as mock_get_episodes:
        # Setup mock to return empty list (dry run mode)
        mock_get_episodes.return_value = []
        mock_process.return_value = []
        
        # Using clean command as an example - note --dry-run comes before the command
        result = main(["--env", "test", "--dry-run", "clean"])
        assert result == 0  # Should succeed with dry run
        
        # Verify mocks were called correctly
        mock_get_episodes.assert_called_once()
        mock_process.assert_called_once_with(limit=None, dry_run=True) 