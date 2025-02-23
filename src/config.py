"""Configuration management for the RSS feed processor.

This module handles:
- Environment variable loading from .env files
- Path management for data storage
- Configuration validation
- Database connection settings
- Logging configuration
- API settings and timeouts
- Processing limits

Usage:
    1. Create a .env file with required settings
    2. Import and use config variables
    3. Call validate_config() before using settings
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment
ENV = os.getenv("APP_ENV", "production")  # Default to production if not set

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Database paths
if ENV == "test":
    DB_PATH = DATA_DIR / "test.db"
    logger = logging.getLogger(__name__)
    logger.info("Using test database: %s", DB_PATH)
else:
    DB_PATH = DATA_DIR / "episodes.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Database configuration
SQLITE_TIMEOUT = 30  # seconds

# API configuration
OPENAI_MODEL = "gpt-4o-mini"  # Model for cleaning and tagging
API_TIMEOUT = 30  # seconds
API_MAX_RETRIES = 3

# Processing configuration
DEFAULT_LIMIT = None  # No limit by default
FEED_FETCH_TIMEOUT = 30  # seconds

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

def setup_logging():
    """Configure logging with standard format."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT
    )

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

def get_openai_api_key() -> str | None:
    """Get OpenAI API key from environment.
    
    Returns:
        str | None: The configured API key or None if not set
    """
    return os.getenv("OPENAI_API_KEY")

def validate_config() -> None:
    """Validate that all required configuration variables are set.
    
    This function checks:
        - RSS_FEED_URL is set
        - Data directory exists and is writable
        - Database path is accessible
        - OpenAI API key is set for cleaning/tagging operations
    
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
        
    if not get_openai_api_key():
        raise ValueError(
            "Missing required environment variable: OPENAI_API_KEY\n"
            "Please check your .env file."
        )

    if not DATA_DIR.exists():
        raise OSError(f"Data directory does not exist: {DATA_DIR}")
        
    if not os.access(DATA_DIR, os.W_OK):
        raise OSError(f"Data directory is not writable: {DATA_DIR}")

# Initialize logging when module is imported
setup_logging() 