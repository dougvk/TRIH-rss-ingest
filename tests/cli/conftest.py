"""Test configuration and fixtures for CLI tests."""
import os
import pytest
from pathlib import Path
from typing import Generator, Any

@pytest.fixture(autouse=True)
def cli_env() -> Generator[None, Any, None]:
    """Set up test environment for CLI tests.
    
    This fixture:
    1. Sets APP_ENV to test
    2. Restores original environment after test
    """
    # Store original environment
    original_env = os.environ.copy()
    
    # Set test environment
    os.environ["APP_ENV"] = "test"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def cli_args() -> list[str]:
    """Basic CLI arguments for testing."""
    return ["--env", "test"]

@pytest.fixture
def debug_args(cli_args: list[str]) -> list[str]:
    """CLI arguments with debug enabled."""
    return cli_args + ["--debug"]

@pytest.fixture
def dry_run_args(cli_args: list[str]) -> list[str]:
    """CLI arguments with dry run enabled."""
    return cli_args + ["--dry-run"] 