"""Clean command for episode descriptions."""
import logging
import argparse

from src.cleaning import clean_episode, process_episodes, get_episodes
from .base import Command
from .registry import register

logger = logging.getLogger(__name__)

@register("clean")
class CleanCommand(Command):
    """Clean episode descriptions."""
    
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
        self._execution_success = None  # Track execution success state
    
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
                # Clean single episode
                logger.info("Cleaning episode %s", self.guid)
                # Check if episode exists first
                from src.storage import get_episode
                episode = get_episode(self.guid)
                if not episode:
                    logger.error("Episode not found: %s", self.guid)
                    self._execution_success = False
                    return False  # Return False even in dry run mode if episode doesn't exist
                    
                result = clean_episode(
                    self.guid,
                    dry_run=self.dry_run
                )
                if self.dry_run:
                    self._execution_success = True
                    return True
                if result:
                    logger.info(
                        "Successfully cleaned episode %s (modified: %s)",
                        self.guid, result.is_modified
                    )
                    self._execution_success = True
                    return True
                logger.error("Failed to clean episode %s", self.guid)
                self._execution_success = False
                return False
            
            # Clean multiple episodes
            logger.info("Cleaning episodes (limit: %s)", self.limit or "none")
            episodes = get_episodes(limit=self.limit)
            logger.info("Would process %d episodes", len(episodes))
            
            results = process_episodes(
                limit=self.limit,
                dry_run=self.dry_run
            )
            if self.dry_run:
                self._execution_success = True
                return True
                
            success = bool(results)  # Return True if any episodes were cleaned
            self._execution_success = success
            logger.info("Successfully cleaned %d episodes", len(results))
            return success
            
        except Exception as e:
            logger.error("Failed to clean content: %s", str(e))
            if self.debug:
                logger.exception("Detailed error:")
            self._execution_success = False
            return False  # Always return False on error, even in dry run mode
    
    def verify(self) -> bool:
        """Verify command execution was successful.
        
        Returns:
            True if verification passes
        """
        # First check execution state
        if self._execution_success is False:
            return False
            
        if self.dry_run:
            return self._execution_success
            
        try:
            from src.storage import get_episode, get_episodes
            
            if self.guid:
                # Verify single episode
                episode = get_episode(self.guid)
                if not episode or not episode.cleaned_description:
                    return False
            else:
                # Verify at least one episode was cleaned
                episodes = get_episodes(limit=1)
                if not episodes or not any(
                    e.cleaned_description for e in episodes
                ):
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Verification failed: %s", str(e))
            return False 