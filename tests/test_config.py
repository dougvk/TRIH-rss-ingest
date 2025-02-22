"""Test configuration loading and validation."""
import pytest
from src.config import validate_config, RSS_FEED_URL, FEED_TOKEN

def test_config_variables_exist():
    """Test that config variables are accessible."""
    assert hasattr(pytest, "fixture")  # Test pytest itself
    assert RSS_FEED_URL is None  # Should be None since we haven't set it
    assert FEED_TOKEN is None  # Should be None since we haven't set it

def test_validate_config_raises_error():
    """Test that validate_config raises error when vars missing."""
    with pytest.raises(ValueError) as exc_info:
        validate_config()
    assert "Missing required environment variables" in str(exc_info.value)
    assert "RSS_FEED_URL" in str(exc_info.value)
    assert "FEED_TOKEN" in str(exc_info.value) 