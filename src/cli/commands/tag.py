"""Command to tag episodes with taxonomy."""
import logging
import argparse
from typing import Optional

from src.storage import get_episode
from src.tagging import tag_episode
from src.tagging.processor import process_episodes
from src.cli.commands.base import Command
from src.cli.commands.registry import register

logger = logging.getLogger(__name__)

@register("tag")
class TagCommand(Command):
    """Tag episodes with taxonomy."""
    
    def __init__(
        self,
        env: str,
        dry_run: bool = False,
        debug: bool = False,
        guid: str = None,
        limit: int = None
    ):
        """Initialize command.
        
        Args:
            env: Environment (test/prod)
            dry_run: If True, show what would be done
            debug: If True, enable debug output
            guid: Process single episode by GUID
            limit: Maximum number of episodes to process
        """
        super().__init__(env, dry_run, debug)
        self.guid = guid
        self.limit = limit
    
    @staticmethod
    def setup_parser(parser: argparse.ArgumentParser) -> None:
        """Set up argument parser for this command.
        
        Args:
            parser: Parser to configure
        """
        parser.add_argument(
            "--guid",
            help="Process a single episode by GUID"
        )
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
            
        # No additional validation needed - all params optional
        return True
    
    def execute(self) -> bool:
        """Execute the command.
        
        Returns:
            True if successful
        """
        try:
            if self.guid:
                # Tag single episode
                logger.info("Tagging episode %s", self.guid)
                episode = get_episode(self.guid)
                if not episode:
                    logger.error("Episode not found: %s", self.guid)
                    return self.dry_run  # Return True in dry run mode
                    
                tags = tag_episode(episode, dry_run=self.dry_run)
                if self.dry_run:
                    return True
                if tags:
                    logger.info("Successfully tagged episode %s", self.guid)
                    logger.debug("Tags: %s", tags)
                    return True
                logger.error("Failed to tag episode %s", self.guid)
                return False
            
            # Tag multiple episodes
            logger.info("Tagging episodes (limit: %s)", self.limit or "none")
            results = process_episodes(
                limit=self.limit,
                dry_run=self.dry_run
            )
            logger.info("Successfully tagged %d episodes", len(results))
            return True
            
        except Exception as e:
            logger.error("Failed to tag content: %s", str(e))
            if self.debug:
                logger.exception("Detailed error:")
            return self.dry_run  # Return True in dry run mode
    
    def verify(self) -> bool:
        """Verify command execution was successful.
        
        Returns:
            True if verification passes
        """
        if self.dry_run:
            return True
            
        try:
            from src.storage import get_episode, get_episodes
            
            if self.guid:
                # Verify single episode
                episode = get_episode(self.guid)
                if not episode or not episode.tags:
                    return False
            else:
                # Verify at least one episode was tagged
                episodes = get_episodes(limit=1)
                if not episodes or not any(
                    e.tags for e in episodes
                ):
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Verification failed: %s", str(e))
            return False 