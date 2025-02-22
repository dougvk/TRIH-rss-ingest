"""Test SQLite storage functionality."""
import sqlite3
from pathlib import Path
import pytest

from src.storage import init_db, get_connection
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