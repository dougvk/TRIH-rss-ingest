"""Tests for CLI utility functions."""
import pytest
from src.cli.utils import validate_environment, setup_environment

def test_validate_environment_none():
    """Test environment validation with None."""
    with pytest.raises(ValueError, match="Environment .* is required"):
        validate_environment(None)

def test_validate_environment_empty():
    """Test environment validation with empty string."""
    with pytest.raises(ValueError, match="Environment .* is required"):
        validate_environment("")

def test_validate_environment_invalid():
    """Test environment validation with invalid value."""
    with pytest.raises(ValueError, match="Invalid environment"):
        validate_environment("invalid")

def test_validate_environment_test():
    """Test environment validation with test environment."""
    env = validate_environment("test")
    assert env == "test"
    
    # Should work with different cases
    env = validate_environment("TEST")
    assert env == "test"
    
    env = validate_environment(" Test ")
    assert env == "test"

def test_validate_environment_prod():
    """Test environment validation with production environment."""
    env = validate_environment("prod")
    assert env == "prod"
    
    # Should work with different cases
    env = validate_environment("PROD")
    assert env == "prod"
    
    env = validate_environment(" Prod ")
    assert env == "prod"

def test_setup_environment(monkeypatch):
    """Test environment setup."""
    env_vars = {}
    monkeypatch.setattr(
        "os.environ",
        env_vars
    )
    
    setup_environment("test")
    assert env_vars["APP_ENV"] == "test"
    
    setup_environment("prod")
    assert env_vars["APP_ENV"] == "prod" 