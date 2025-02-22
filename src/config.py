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

# Feed configuration
RSS_FEED_URL = os.getenv("RSS_FEED_URL")
FEED_TOKEN = os.getenv("FEED_TOKEN")

# Database configuration
SQLITE_TIMEOUT = 30  # seconds

def validate_config():
    """Validate that all required configuration variables are set."""
    required_vars = {
        "RSS_FEED_URL": RSS_FEED_URL,
        "FEED_TOKEN": FEED_TOKEN,
    }
    
    missing = [var for var, value in required_vars.items() if not value]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please check your .env file."
        ) 