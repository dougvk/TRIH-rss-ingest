"""Main orchestration module for the RSS feed processor."""
import logging
from typing import List

from . import config
from .feed_ingest import fetch_rss_feed, parse_rss_feed
from .models import Episode
from .storage import init_db, store_episodes, get_episodes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_feed() -> List[Episode]:
    """Fetch and process the RSS feed.
    
    Returns:
        List[Episode]: List of processed episodes
        
    Raises:
        Exception: If feed processing fails
    """
    try:
        logger.info("Fetching RSS feed from %s", config.get_feed_url())
        content = fetch_rss_feed()
        
        logger.info("Parsing feed content")
        episodes = parse_rss_feed(content)
        logger.info("Found %d episodes in feed", len(episodes))
        
        return episodes
    except Exception as e:
        logger.error("Failed to process feed: %s", str(e))
        raise

def store_feed_data(episodes: List[Episode]) -> None:
    """Store processed episodes in the database.
    
    Args:
        episodes: List of episodes to store
        
    Raises:
        Exception: If storage fails
    """
    try:
        logger.info("Storing %d episodes in database", len(episodes))
        store_episodes(episodes)
        logger.info("Successfully stored episodes")
    except Exception as e:
        logger.error("Failed to store episodes: %s", str(e))
        raise

def main() -> None:
    """Main entry point for the RSS feed processor."""
    try:
        # Validate configuration
        config.validate_config()
        
        # Initialize database
        logger.info("Initializing database")
        init_db()
        
        # Process feed
        episodes = process_feed()
        
        # Store episodes
        store_feed_data(episodes)
        
        # Get latest episodes to verify storage
        stored = get_episodes(limit=5)
        logger.info("Latest episodes in database:")
        for episode in stored:
            logger.info("- %s (published: %s)", episode.title, episode.published_date)
            
    except Exception as e:
        logger.error("Application error: %s", str(e))
        raise

if __name__ == "__main__":
    main() 