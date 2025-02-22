"""Data models for the RSS feed processor.

This module defines the core data structures used throughout the application.
The models are implemented as dataclasses for clean, immutable data representation.
"""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Episode:
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