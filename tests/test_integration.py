"""Integration tests using a mock feed."""
import os
from pathlib import Path
import sqlite3
import pytest
from datetime import datetime, timezone
import re

from src.main import main
from src.feed_ingest import fetch_rss_feed, parse_rss_feed
from src.storage import init_db, get_episodes, get_episode
from src import config

@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test.db"
    original_path = config.DB_PATH
    
    # Update config to use test database
    config.DB_PATH = db_path
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()
    config.DB_PATH = original_path

@pytest.fixture
def mock_config(monkeypatch, mock_feed_url):
    """Configure the app to use mock feed URL."""
    monkeypatch.setenv("RSS_FEED_URL", mock_feed_url)

def test_full_feed_processing(test_db_path, mock_config):
    """Test processing the entire feed end-to-end."""
    # Run main process
    main()
    
    # Verify database was created
    assert test_db_path.exists()
    
    # Check episode count
    episodes = get_episodes()
    assert len(episodes) == 729  # Known episode count
    
    # Verify episode data integrity
    for episode in episodes[:5]:  # Check first 5 episodes
        assert episode.title.startswith("Episode ")
        assert episode.description.startswith("Test description")
        assert episode.guid.startswith("test-")
        assert isinstance(episode.published_date, datetime)
        assert episode.published_date.tzinfo == timezone.utc
        assert episode.audio_url.startswith("https://example.com/episode")
        assert episode.duration == "3600"
        
        # Verify episode number if it's a series episode
        if "(Ep " in episode.title:
            assert episode.episode_number is not None
            assert isinstance(episode.episode_number, int)
            # Extract the expected episode number from the title
            match = re.search(r'\(Ep\s*(\d+)\)', episode.title)
            assert match is not None
            expected_number = int(match.group(1))
            assert episode.episode_number == expected_number
        else:
            assert episode.episode_number is None
        
        # Verify we can fetch individual episodes
        stored = get_episode(episode.guid)
        assert stored is not None
        assert stored.title == episode.title
        assert stored.published_date == episode.published_date
        assert stored.episode_number == episode.episode_number

def test_incremental_update(test_db_path, mock_config):
    """Test updating with same feed doesn't duplicate episodes."""
    # First run
    main()
    first_count = len(get_episodes())
    
    # Second run
    main()
    second_count = len(get_episodes())
    
    # Should have same number of episodes
    assert first_count == second_count
    assert first_count == 729

def test_database_integrity(test_db_path):
    """Test database constraints and indexes."""
    # Initialize database
    init_db()
    
    with sqlite3.connect(test_db_path) as conn:
        # Check indexes exist
        indexes = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='episodes'
        """).fetchall()
        index_names = [idx[0] for idx in indexes]
        
        assert 'idx_episodes_guid' in index_names
        assert 'idx_episodes_published_date' in index_names
        
        # Check UNIQUE constraint on guid
        assert any(
            'UNIQUE' in sql[0]
            for sql in conn.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='episodes'
            """)
        )

def test_feed_content_integrity(mock_config):
    """Test feed content validity."""
    # Fetch feed
    content = fetch_rss_feed()
    episodes = parse_rss_feed(content)
    
    # Basic content checks
    assert len(episodes) == 729
    assert all(isinstance(e.title, str) for e in episodes)
    assert all(isinstance(e.description, str) for e in episodes)
    assert all(isinstance(e.published_date, datetime) for e in episodes)
    assert all(e.published_date.tzinfo == timezone.utc for e in episodes)
    
    # Check chronological order
    dates = [e.published_date for e in episodes]
    assert dates == sorted(dates, reverse=True)  # Most recent first
    
    # Check for required fields
    for episode in episodes:
        assert episode.guid, "Episode missing guid"
        assert episode.title, "Episode missing title"
        assert episode.description, "Episode missing description"
        assert episode.published_date, "Episode missing date"
        assert episode.audio_url, "Episode missing audio URL"
        assert episode.duration == "3600", "Episode has wrong duration" 