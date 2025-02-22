"""Configuration management for the RSS feed processor."""
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

def get_feed_url():
    """Get RSS feed URL from environment."""
    return os.getenv("RSS_FEED_URL")

# Database configuration
SQLITE_TIMEOUT = 30  # seconds

def validate_config():
    """Validate that all required configuration variables are set."""
    if not get_feed_url():
        raise ValueError(
            "Missing required environment variable: RSS_FEED_URL\n"
            "Please check your .env file."
        ) 