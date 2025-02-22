"""Test RSS feed ingestion functionality."""
import pytest
import requests
from src.feed_ingest import fetch_rss_feed

def test_fetch_rss_feed_missing_url(monkeypatch):
    """Test fetch_rss_feed raises error when URL not configured."""
    # Ensure URL is not set
    monkeypatch.setenv("RSS_FEED_URL", "")
    
    with pytest.raises(ValueError) as exc_info:
        fetch_rss_feed()
    assert "RSS feed URL not configured" in str(exc_info.value)

def test_fetch_rss_feed_network_error(monkeypatch, requests_mock):
    """Test fetch_rss_feed handles network errors."""
    test_url = "https://example.com/feed.rss"
    monkeypatch.setenv("RSS_FEED_URL", test_url)
    
    # Mock a network error
    requests_mock.get(test_url, exc=requests.RequestException("Network error"))
    
    with pytest.raises(requests.RequestException) as exc_info:
        fetch_rss_feed()
    assert "Network error" in str(exc_info.value)

def test_fetch_rss_feed_success(monkeypatch, requests_mock):
    """Test fetch_rss_feed successfully returns feed content."""
    test_url = "https://example.com/feed.rss"
    test_content = "<rss><channel><title>Test Feed</title></channel></rss>"
    
    monkeypatch.setenv("RSS_FEED_URL", test_url)
    requests_mock.get(test_url, text=test_content)
    
    result = fetch_rss_feed()
    assert result == test_content

def test_fetch_rss_feed_with_limit(monkeypatch, requests_mock):
    """Test fetch_rss_feed limits the number of entries."""
    test_url = "https://example.com/feed.rss"
    # Create a feed with 5 entries
    test_content = """
    <rss><channel>
        <item><title>Episode 1</title></item>
        <item><title>Episode 2</title></item>
        <item><title>Episode 3</title></item>
        <item><title>Episode 4</title></item>
        <item><title>Episode 5</title></item>
    </channel></rss>
    """
    
    monkeypatch.setenv("RSS_FEED_URL", test_url)
    requests_mock.get(test_url, text=test_content)
    
    # Request only 2 entries
    result = fetch_rss_feed(limit_entries=2)
    
    # Should only contain 2 items
    assert result.count("<item>") == 2
    assert "Episode 1" in result
    assert "Episode 2" in result
    assert "Episode 5" not in result 