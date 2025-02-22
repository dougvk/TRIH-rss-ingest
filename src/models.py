"""Data models for the RSS feed processor."""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Episode:
    """Represents a podcast episode from the RSS feed."""
    title: str
    description: str
    link: str
    published_date: datetime
    guid: str  # Unique identifier for the episode
    
    # Optional fields that might not be in every feed
    duration: str | None = None
    audio_url: str | None = None 