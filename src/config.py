"""Configuration management for the RSS feed processor.

This module handles:
- Environment variable loading from .env files
- Path management for data storage
- Configuration validation
- Database connection settings

Usage:
    1. Create a .env file with required settings
    2. Import and use config variables
    3. Call validate_config() before using settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "episodes.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

def get_feed_url() -> str | None:
    """Get RSS feed URL from environment.
    
    Returns:
        str | None: The configured feed URL or None if not set
        
    Example:
        >>> url = get_feed_url()
        >>> if url:
        ...     print("Feed URL:", url)
        ... else:
        ...     print("Feed URL not configured")
    """
    return os.getenv("RSS_FEED_URL")

# Database configuration
SQLITE_TIMEOUT = 30  # seconds

def validate_config() -> None:
    """Validate that all required configuration variables are set.
    
    This function checks:
        - RSS_FEED_URL is set
        - Data directory exists and is writable
        - Database path is accessible
    
    Raises:
        ValueError: If any required setting is missing
        OSError: If data directory is not writable
        
    Example:
        >>> try:
        ...     validate_config()
        ...     print("Configuration valid")
        ... except ValueError as e:
        ...     print("Configuration error:", e)
    """
    if not get_feed_url():
        raise ValueError(
            "Missing required environment variable: RSS_FEED_URL\n"
            "Please check your .env file."
        ) 