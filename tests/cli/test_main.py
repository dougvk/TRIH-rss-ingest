"""Tests for main CLI functionality."""
import pytest
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
    result = main(cli_args)
    assert result == 1  # Should fail without command

def test_main_invalid_env():
    """Test main function with invalid environment."""
    with pytest.raises(SystemExit):
        main(["--env", "invalid"])

def test_main_debug(debug_args: list[str]):
    """Test main function with debug enabled."""
    result = main(debug_args)
    assert result == 1  # Should fail without command, but with debug output

def test_main_dry_run(dry_run_args: list[str]):
    """Test main function with dry run enabled."""
    result = main(dry_run_args)
    assert result == 1  # Should fail without command 