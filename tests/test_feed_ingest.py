"""Test RSS feed ingestion functionality."""
from datetime import datetime, timezone
import pytest
import requests
from src.feed_ingest import fetch_rss_feed, parse_rss_feed
from src.models import Episode

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

def test_parse_rss_feed_empty():
    """Test parse_rss_feed handles empty feed."""
    empty_feed = "<rss><channel></channel></rss>"
    
    with pytest.raises(ValueError) as exc_info:
        parse_rss_feed(empty_feed)
    assert "No episodes found in feed" in str(exc_info.value)

def test_parse_rss_feed_success():
    """Test parse_rss_feed successfully parses feed content."""
    test_feed = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
        <channel>
            <title>Test Podcast</title>
            <item>
                <title>Test Episode</title>
                <description>Test Description</description>
                <link>https://example.com/episode1</link>
                <guid>12345</guid>
                <pubDate>Mon, 01 Jan 2024 12:00:00 +0000</pubDate>
                <itunes:duration>30:00</itunes:duration>
                <enclosure url="https://example.com/audio.mp3" type="audio/mpeg" length="1234"/>
            </item>
        </channel>
    </rss>"""
    
    episodes = parse_rss_feed(test_feed)
    assert len(episodes) == 1
    
    episode = episodes[0]
    assert isinstance(episode, Episode)
    assert episode.title == "Test Episode"
    assert episode.description == "Test Description"
    assert episode.link == "https://example.com/episode1"
    assert episode.guid == "12345"
    assert episode.published_date == datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert episode.duration == "30:00"
    assert episode.audio_url == "https://example.com/audio.mp3"

def test_parse_rss_feed_minimal():
    """Test parse_rss_feed works with minimal required fields."""
    test_feed = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <title>Test Episode</title>
                <description>Test Description</description>
                <link>https://example.com/episode1</link>
                <guid>12345</guid>
                <pubDate>Mon, 01 Jan 2024 12:00:00 +0000</pubDate>
            </item>
        </channel>
    </rss>"""
    
    episodes = parse_rss_feed(test_feed)
    assert len(episodes) == 1
    
    episode = episodes[0]
    assert episode.title == "Test Episode"
    assert episode.duration is None
    assert episode.audio_url is None 