"""Test SQLite storage functionality."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import pytest

from src.storage import init_db, get_connection, store_episode, store_episodes, get_episode, get_episodes
from src.models import Episode
from src import config

@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database path for testing."""
    db_path = tmp_path / "test.db"
    original_path = config.DB_PATH
    
    # Update config to use test database
    config.DB_PATH = db_path
    
    yield db_path
    
    # Cleanup and restore original path
    if db_path.exists():
        db_path.unlink()
    config.DB_PATH = original_path

@pytest.fixture
def sample_episode():
    """Create a sample episode for testing."""
    return Episode(
        guid="test-123",
        title="Test Episode",
        description="Test Description",
        link="https://example.com/test",
        published_date=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
        duration="30:00",
        audio_url="https://example.com/test.mp3"
    )

@pytest.fixture
def sample_episodes():
    """Create multiple sample episodes for testing."""
    return [
        Episode(
            guid=f"test-{i}",
            title=f"Test Episode {i}",
            description=f"Test Description {i}",
            link=f"https://example.com/test-{i}",
            published_date=datetime(2024, 1, i+1, 12, 0, tzinfo=timezone.utc),
            duration=f"{30+i}:00",
            audio_url=f"https://example.com/test-{i}.mp3"
        )
        for i in range(3)
    ]

def test_get_connection(test_db_path):
    """Test database connection is properly configured."""
    with get_connection() as conn:
        # Test connection is working
        result = conn.execute("SELECT 1").fetchone()
        assert result[0] == 1
        
        # Test Row factory is configured
        assert isinstance(result, sqlite3.Row)
        
        # Test foreign keys are enabled
        pragma = conn.execute("PRAGMA foreign_keys").fetchone()
        assert pragma[0] == 1

def test_init_db_creates_tables(test_db_path):
    """Test database initialization creates required tables."""
    # Initialize database
    init_db()
    
    with get_connection() as conn:
        # Check episodes table exists
        result = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='episodes'
        """).fetchone()
        assert result is not None
        assert result['name'] == 'episodes'
        
        # Check required columns exist
        columns = conn.execute("PRAGMA table_info(episodes)").fetchall()
        column_names = [col['name'] for col in columns]
        
        assert 'id' in column_names
        assert 'guid' in column_names
        assert 'title' in column_names
        assert 'description' in column_names
        assert 'link' in column_names
        assert 'published_date' in column_names
        assert 'duration' in column_names
        assert 'audio_url' in column_names
        assert 'created_at' in column_names
        assert 'updated_at' in column_names

def test_init_db_creates_indexes(test_db_path):
    """Test database initialization creates required indexes."""
    # Initialize database
    init_db()
    
    with get_connection() as conn:
        # Check indexes exist
        indexes = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='episodes'
        """).fetchall()
        index_names = [idx['name'] for idx in indexes]
        
        assert 'idx_episodes_guid' in index_names
        assert 'idx_episodes_published_date' in index_names

def test_connection_rollback_on_error(test_db_path):
    """Test connection is rolled back on error."""
    init_db()
    
    # Try an operation that should fail
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection() as conn:
            # This should fail due to NOT NULL constraint
            conn.execute("INSERT INTO episodes (guid) VALUES (?)", ('test',))
    
    # Verify no data was inserted
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
        assert count == 0

def test_store_episode(test_db_path, sample_episode):
    """Test storing a single episode."""
    init_db()
    
    # Store the episode
    store_episode(sample_episode)
    
    # Verify it was stored correctly
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM episodes WHERE guid = ?", (sample_episode.guid,)).fetchone()
        
        assert row is not None
        assert row['title'] == sample_episode.title
        assert row['description'] == sample_episode.description
        assert row['link'] == sample_episode.link
        assert row['published_date'] == sample_episode.published_date
        assert row['duration'] == sample_episode.duration
        assert row['audio_url'] == sample_episode.audio_url

def test_store_episode_update(test_db_path, sample_episode):
    """Test updating an existing episode."""
    init_db()
    
    # Store the episode
    store_episode(sample_episode)
    
    # Update the episode
    updated_episode = Episode(
        guid=sample_episode.guid,  # Same guid
        title="Updated Title",
        description="Updated Description",
        link=sample_episode.link,
        published_date=sample_episode.published_date,
        duration="45:00",
        audio_url=sample_episode.audio_url
    )
    store_episode(updated_episode)
    
    # Verify it was updated
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
        assert count == 1  # Still only one episode
        
        row = conn.execute("SELECT * FROM episodes WHERE guid = ?", (sample_episode.guid,)).fetchone()
        assert row['title'] == "Updated Title"
        assert row['description'] == "Updated Description"
        assert row['duration'] == "45:00"

def test_store_episodes_batch(test_db_path, sample_episodes):
    """Test storing multiple episodes in a batch."""
    init_db()
    
    # Store episodes
    store_episodes(sample_episodes)
    
    # Verify all were stored
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
        assert count == len(sample_episodes)
        
        # Check each episode
        for episode in sample_episodes:
            row = conn.execute("SELECT * FROM episodes WHERE guid = ?", (episode.guid,)).fetchone()
            assert row is not None
            assert row['title'] == episode.title

def test_get_episode(test_db_path, sample_episode):
    """Test retrieving a single episode."""
    init_db()
    store_episode(sample_episode)
    
    # Get the episode
    episode = get_episode(sample_episode.guid)
    
    assert episode is not None
    assert episode.guid == sample_episode.guid
    assert episode.title == sample_episode.title
    assert episode.description == sample_episode.description
    assert episode.link == sample_episode.link
    assert episode.published_date == sample_episode.published_date
    assert episode.duration == sample_episode.duration
    assert episode.audio_url == sample_episode.audio_url

def test_get_episode_not_found(test_db_path):
    """Test retrieving a non-existent episode."""
    init_db()
    
    episode = get_episode("non-existent")
    assert episode is None

def test_get_episodes_ordered(test_db_path, sample_episodes):
    """Test retrieving episodes ordered by published date."""
    init_db()
    store_episodes(sample_episodes)
    
    # Get all episodes
    episodes = get_episodes()
    
    assert len(episodes) == len(sample_episodes)
    
    # Should be in reverse chronological order
    for i in range(len(episodes) - 1):
        assert episodes[i].published_date > episodes[i + 1].published_date

def test_get_episodes_limit_offset(test_db_path, sample_episodes):
    """Test pagination of episodes."""
    init_db()
    store_episodes(sample_episodes)
    
    # Get with limit
    episodes = get_episodes(limit=2)
    assert len(episodes) == 2
    
    # Get with offset
    episodes = get_episodes(limit=2, offset=1)
    assert len(episodes) == 2
    assert episodes[0].guid == sample_episodes[1].guid  # Second episode 