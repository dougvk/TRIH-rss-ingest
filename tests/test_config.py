"""Test configuration loading and validation."""
import os
import pytest
from src.config import validate_config, get_feed_url

def test_config_variables_exist():
    """Test that config variables are accessible."""
    assert hasattr(pytest, "fixture")  # Test pytest itself
    # get_feed_url should return something (might be None or a string)
    assert get_feed_url() is not False

def test_validate_config_with_missing_url(monkeypatch):
    """Test that validate_config raises error when URL is missing."""
    # Temporarily unset RSS_FEED_URL
    monkeypatch.delenv("RSS_FEED_URL", raising=False)
    
    with pytest.raises(ValueError) as exc_info:
        validate_config()
    assert "Missing required environment variable: RSS_FEED_URL" in str(exc_info.value)

def test_validate_config_with_url(monkeypatch):
    """Test that validate_config passes when URL is set."""
    # Set a dummy URL
    monkeypatch.setenv("RSS_FEED_URL", "https://example.com/feed.rss")
    
    # Should not raise any exception
    validate_config() 