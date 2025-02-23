"""Main orchestration module for the RSS feed processor."""
import logging
import time
from typing import List

from src import config
from src.feed_ingest import fetch_rss_feed, parse_rss_feed
from src.models import Episode
from src.storage import init_db, store_episodes, get_episodes

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
        start_time = time.time()
        logger.info("Fetching RSS feed from %s", config.get_feed_url())
        content = fetch_rss_feed()
        fetch_time = time.time()
        logger.info("Feed fetched in %.2f seconds", fetch_time - start_time)
        
        logger.info("Parsing feed content")
        episodes = parse_rss_feed(content)
        parse_time = time.time()
        logger.info("Feed parsed in %.2f seconds", parse_time - fetch_time)
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
        start_time = time.time()
        logger.info("Storing %d episodes in database", len(episodes))
        store_episodes(episodes)
        end_time = time.time()
        logger.info("Successfully stored episodes in %.2f seconds", end_time - start_time)
    except Exception as e:
        logger.error("Failed to store episodes: %s", str(e))
        raise

def main() -> None:
    """Main entry point for the RSS feed processor."""
    try:
        start_time = time.time()
        
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
            
        end_time = time.time()
        logger.info("Total processing time: %.2f seconds", end_time - start_time)
            
    except Exception as e:
        logger.error("Application error: %s", str(e))
        raise

if __name__ == "__main__":
    main() 