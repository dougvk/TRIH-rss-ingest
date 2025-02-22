"""SQLite storage functionality for podcast episodes."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

from . import config

def init_db() -> None:
    """Initialize the database and create tables if they don't exist."""
    with get_connection() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guid TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            link TEXT NOT NULL,
            published_date TIMESTAMP NOT NULL,
            duration TEXT,
            audio_url TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create indexes for common queries
        conn.execute('CREATE INDEX IF NOT EXISTS idx_episodes_guid ON episodes(guid)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_episodes_published_date ON episodes(published_date)')

@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection with proper configuration.
    
    Yields:
        sqlite3.Connection: Configured database connection
        
    Raises:
        sqlite3.Error: If connection fails
    """
    conn = sqlite3.connect(
        config.DB_PATH,
        timeout=config.SQLITE_TIMEOUT,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    
    try:
        # Enable foreign keys and configure connection
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Use Row factory for better column access
        conn.row_factory = sqlite3.Row
        
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close() 