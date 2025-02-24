"""Feed ingestion command."""
import logging
from typing import Optional
import argparse

from src import config
from src.feed_ingest import fetch_rss_feed, parse_rss_feed
from src.storage import init_db, store_episodes
from .base import Command
from .registry import register

logger = logging.getLogger(__name__)

@register("ingest")
class IngestCommand(Command):
    """Fetch and store feed data."""
    
    def __init__(
        self,
        env: str,
        dry_run: bool = False,
        debug: bool = False,
        limit: Optional[int] = None
    ):
        """Initialize command.
        
        Args:
            env: Environment (test/prod)
            dry_run: If True, show what would be done
            debug: If True, enable debug output
            limit: Maximum number of episodes to process
        """
        super().__init__(env, dry_run, debug)
        self.limit = limit
    
    @staticmethod
    def setup_parser(parser: argparse.ArgumentParser) -> None:
        """Set up argument parser for this command.
        
        Args:
            parser: Parser to configure
        """
        parser.add_argument(
            "--limit",
            type=int,
            help="Maximum number of episodes to process"
        )
    
    def validate(self) -> bool:
        """Validate command can be executed.
        
        Returns:
            True if validation passes
        """
        if not super().validate():
            return False
            
        # Validate feed URL is configured
        if not config.get_feed_url():
            raise ValueError("RSS feed URL not configured")
            
        return True
    
    def execute(self) -> bool:
        """Execute the command.
        
        Returns:
            True if successful
        """
        try:
            # Initialize database if not dry run
            if not self.dry_run:
                init_db()
                logger.info("Initialized database schema")
            
            # Fetch feed content
            logger.info("Fetching RSS feed...")
            content = fetch_rss_feed()
            
            # Parse episodes
            logger.info("Parsing feed content...")
            episodes = parse_rss_feed(content, limit=self.limit)
            logger.info("Found %d episodes in feed", len(episodes))
            
            if self.dry_run:
                logger.info(
                    "Dry run - would store %d episodes in database",
                    len(episodes)
                )
                return True
            
            # Store episodes
            logger.info("Storing episodes in database...")
            store_episodes(episodes)
            logger.info("Successfully stored %d episodes", len(episodes))
            
            return True
            
        except Exception as e:
            logger.error("Failed to ingest feed: %s", str(e))
            if self.debug:
                logger.exception("Detailed error:")
            return False
    
    def verify(self) -> bool:
        """Verify command execution was successful.
        
        Returns:
            True if verification passes
        """
        if self.dry_run:
            return True
            
        try:
            from src.storage import get_episodes
            episodes = get_episodes(limit=1)
            return len(episodes) > 0
        except Exception as e:
            logger.error("Verification failed: %s", str(e))
            return False 