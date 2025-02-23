"""Test configuration and fixtures."""
import os
import pytest
import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

@pytest.fixture(autouse=True)
def test_env():
    """Set up test environment.
    
    This fixture runs automatically for all tests and:
    1. Sets APP_ENV to "test" to use test database
    2. Copies production database to test database if it exists
    3. Cleans up test database after tests
    """
    # Set test environment before importing config
    os.environ["APP_ENV"] = "test"
    
    # Now import config to get correct DB paths
    from src import config
    
    # Copy production database if it exists
    prod_db = config.DATA_DIR / "episodes.db"
    if prod_db.exists():
        shutil.copy2(prod_db, config.DB_PATH)
        config.logger.info("Copied production database to test database")
    
    # Run the test
    yield
    
    # Clean up test database
    if config.DB_PATH.exists():
        config.DB_PATH.unlink()
        config.logger.info("Cleaned up test database")

@pytest.fixture
def mock_feed():
    """Sample RSS feed content for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
        <channel>
            <title>Test Podcast</title>
            <item>
                <title>Test Episode</title>
                <description>Test Description</description>
                <guid>test-123</guid>
                <pubDate>Mon, 01 Jan 2024 12:00:00 +0000</pubDate>
                <link>https://example.com/episode1</link>
                <itunes:duration>3600</itunes:duration>
                <enclosure url="https://example.com/audio1.mp3" type="audio/mpeg"/>
            </item>
        </channel>
    </rss>'''

@pytest.fixture
def mock_feed_content():
    """Create a mock RSS feed that matches the structure of the real feed."""
    # Generate 729 episodes to match real feed count
    items = []
    base_date = datetime(2025, 2, 20, 0, 5, tzinfo=timezone.utc)
    
    for i in range(729):
        pub_date = base_date - timedelta(days=i)
        # Make some episodes part of a series with episode numbers
        is_series = i % 3 == 0  # Every third episode is part of a series
        title = f"Episode {i}: Test Title"
        if is_series:
            title = f"Episode {i}: (Ep {i//3 + 1}) Test Title"
        
        items.append(f'''
            <item>
                <title>{title}</title>
                <description>Test description for episode {i}</description>
                <guid>test-{i}</guid>
                <pubDate>{pub_date.strftime("%a, %d %b %Y %H:%M:%S %z")}</pubDate>
                <itunes:duration>3600</itunes:duration>
                <enclosure url="https://example.com/episode{i}.mp3" type="audio/mpeg" length="1234567"/>
            </item>
        ''')
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
        <channel>
            <title>Test Podcast Feed</title>
            <description>Test feed description</description>
            <language>en-us</language>
            <pubDate>{base_date.strftime("%a, %d %b %Y %H:%M:%S %z")}</pubDate>
            {"".join(items)}
        </channel>
    </rss>'''

@pytest.fixture
def mock_feed_url(requests_mock, mock_feed_content):
    """Mock the feed URL to return our test content."""
    test_url = "https://test.feed/episodes.rss"
    requests_mock.get(test_url, text=mock_feed_content)
    return test_url 