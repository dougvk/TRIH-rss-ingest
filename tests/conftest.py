"""Common test fixtures."""
import pytest
from datetime import datetime, timezone, timedelta

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