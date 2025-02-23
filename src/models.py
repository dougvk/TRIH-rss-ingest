"""Data models for the RSS feed processor.

This module defines the core data structures used throughout the application.
The models are implemented as dataclasses for clean, immutable data representation.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from dateutil.parser import parse

@dataclass
class Episode:
    """Represents a single podcast episode with all its metadata."""
    
    # Required fields
    guid: str
    title: str
    description: str
    published_date: datetime
    
    # Optional fields with defaults
    link: str = ''
    duration: Optional[str] = None
    audio_url: Optional[str] = None
    cleaned_description: Optional[str] = None
    cleaning_timestamp: Optional[datetime] = None
    cleaning_status: str = "pending"
    tags: Optional[str] = None
    tagging_timestamp: Optional[datetime] = None
    episode_number: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate and convert fields after initialization."""
        if isinstance(self.published_date, str):
            self.published_date = parse(self.published_date)
            
        if isinstance(self.cleaning_timestamp, str):
            self.cleaning_timestamp = parse(self.cleaning_timestamp)
            
        if isinstance(self.tagging_timestamp, str):
            self.tagging_timestamp = parse(self.tagging_timestamp)

    """Represents a podcast episode from the RSS feed.
    
    This class captures all relevant metadata about a podcast episode,
    with required and optional fields matching common RSS feed structures.
    
    Required Attributes:
        title (str): The episode title
        description (str): Full episode description/show notes
        published_date (datetime): Publication date with timezone
        guid (str): Globally unique identifier for the episode
    
    Optional Attributes:
        link (str): Web link to episode page (defaults to empty string)
        duration (str | None): Episode duration (e.g., "45:00" or None)
        audio_url (str | None): Direct URL to audio file (from enclosure tag)
        cleaned_description (str | None): Cleaned version of the description
    
    Example:
        >>> episode = Episode(
        ...     title="Test Episode",
        ...     description="Episode description",
        ...     published_date=datetime.now(timezone.utc),
        ...     guid="unique-id-123",
        ...     duration="30:00",
        ...     audio_url="https://example.com/audio.mp3"
        ... )
    """
    title: str
    description: str
    published_date: datetime
    guid: str  # Unique identifier for the episode
    
    # Optional fields that might not be in every feed
    link: str = ''  # Made optional with default empty string
    duration: str | None = None
    audio_url: str | None = None
    cleaned_description: str | None = None 