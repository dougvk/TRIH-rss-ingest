"""SQLite storage functionality for podcast episodes."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, List, Optional

from . import config
from .models import Episode

# Register adapters and converters for datetime with timezone
def adapt_datetime(dt: datetime) -> str:
    """Convert datetime to string for SQLite storage."""
    return dt.isoformat()

def convert_datetime(s: bytes) -> datetime:
    """Convert string from SQLite to datetime."""
    return datetime.fromisoformat(s.decode())

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)

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

def store_episode(episode: Episode) -> None:
    """Store a single episode in the database.
    
    If an episode with the same guid exists, it will be updated.
    
    Args:
        episode: Episode object to store
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    with get_connection() as conn:
        conn.execute('''
        INSERT INTO episodes (
            guid, title, description, link, published_date, 
            duration, audio_url, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(guid) DO UPDATE SET
            title = excluded.title,
            description = excluded.description,
            link = excluded.link,
            published_date = excluded.published_date,
            duration = excluded.duration,
            audio_url = excluded.audio_url,
            updated_at = CURRENT_TIMESTAMP
        ''', (
            episode.guid,
            episode.title,
            episode.description,
            episode.link,
            episode.published_date,
            episode.duration,
            episode.audio_url
        ))

def store_episodes(episodes: List[Episode]) -> None:
    """Store multiple episodes in the database.
    
    Args:
        episodes: List of Episode objects to store
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    with get_connection() as conn:
        conn.executemany('''
        INSERT INTO episodes (
            guid, title, description, link, published_date, 
            duration, audio_url, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(guid) DO UPDATE SET
            title = excluded.title,
            description = excluded.description,
            link = excluded.link,
            published_date = excluded.published_date,
            duration = excluded.duration,
            audio_url = excluded.audio_url,
            updated_at = CURRENT_TIMESTAMP
        ''', [
            (
                episode.guid,
                episode.title,
                episode.description,
                episode.link,
                episode.published_date,
                episode.duration,
                episode.audio_url
            )
            for episode in episodes
        ])

def get_episode(guid: str) -> Optional[Episode]:
    """Retrieve a single episode by guid.
    
    Args:
        guid: Unique identifier of the episode
        
    Returns:
        Episode object if found, None otherwise
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    with get_connection() as conn:
        row = conn.execute('''
        SELECT guid, title, description, link, published_date, 
               duration, audio_url
        FROM episodes 
        WHERE guid = ?
        ''', (guid,)).fetchone()
        
        if row is None:
            return None
            
        return Episode(
            guid=row['guid'],
            title=row['title'],
            description=row['description'],
            link=row['link'],
            published_date=row['published_date'],
            duration=row['duration'],
            audio_url=row['audio_url']
        )

def get_episodes(limit: Optional[int] = None, offset: int = 0) -> List[Episode]:
    """Retrieve episodes ordered by published date.
    
    Args:
        limit: Maximum number of episodes to return
        offset: Number of episodes to skip
        
    Returns:
        List of Episode objects
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    with get_connection() as conn:
        query = '''
        SELECT guid, title, description, link, published_date, 
               duration, audio_url
        FROM episodes 
        ORDER BY published_date DESC
        '''
        
        if limit is not None:
            query += f' LIMIT {limit} OFFSET {offset}'
            
        rows = conn.execute(query).fetchall()
        
        return [
            Episode(
                guid=row['guid'],
                title=row['title'],
                description=row['description'],
                link=row['link'],
                published_date=row['published_date'],
                duration=row['duration'],
                audio_url=row['audio_url']
            )
            for row in rows
        ] 