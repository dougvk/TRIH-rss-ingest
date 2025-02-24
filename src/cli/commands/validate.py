"""Command to validate episode tags against taxonomy."""
import logging
from typing import Optional, List
import json
from pathlib import Path

from src.cli.commands.base import Command
from src.cli.commands.registry import register
from src.storage import get_episode, get_episodes, Episode
from src.tagging.processor import process_episodes
from src.tagging.taxonomy import taxonomy

logger = logging.getLogger(__name__)

@register("validate")
class ValidateCommand(Command):
    """Command to validate episode tags against taxonomy."""

    def __init__(
        self,
        env: str,
        dry_run: bool = False,
        debug: bool = False,
        guid: Optional[str] = None,
        limit: Optional[int] = None,
        report: Optional[Path] = None
    ):
        """Initialize validate command.
        
        Args:
            env: Environment to run in
            dry_run: Whether to run in dry run mode
            debug: Whether to run in debug mode
            guid: Optional GUID of episode to validate
            limit: Optional limit on number of episodes to validate
            report: Optional path to generate detailed validation report
        """
        super().__init__(env=env, dry_run=dry_run, debug=debug)
        self.guid = guid
        self.limit = limit
        self.report = report
        self.invalid_episodes: List[Episode] = []

    @staticmethod
    def setup_parser(parser):
        """Setup argument parser."""
        parser.add_argument(
            "--guid",
            help="GUID of episode to validate",
            required=False
        )
        parser.add_argument(
            "--limit",
            help="Limit number of episodes to validate",
            type=int,
            required=False
        )
        parser.add_argument(
            "--report",
            type=Path,
            help="Generate detailed validation report to specified file",
            required=False
        )

    def validate(self) -> bool:
        """Validate command can be executed."""
        return True

    def generate_report(self) -> None:
        """Generate detailed validation report."""
        if not self.report:
            return
            
        report = {
            "summary": {
                "total_episodes": len(self.episodes),
                "invalid_episodes": len(self.invalid_episodes),
            },
            "invalid_episodes": []
        }
        
        for episode in self.invalid_episodes:
            try:
                tags = json.loads(episode.tags)
                issues = []
                
                # Check each validation rule
                if not all(c in tags for c in ["Format", "Theme", "Track"]):
                    issues.append("Missing required categories")
                
                for category in ["Format", "Theme", "Track"]:
                    if category in tags:
                        invalid = [t for t in tags[category] if t not in taxonomy[category]]
                        if invalid:
                            issues.append(f"Invalid {category} tags: {invalid}")
                
                report["invalid_episodes"].append({
                    "guid": episode.guid,
                    "title": episode.title,
                    "tags": tags,
                    "issues": issues
                })
                
            except json.JSONDecodeError:
                report["invalid_episodes"].append({
                    "guid": episode.guid,
                    "title": episode.title,
                    "issues": ["Invalid JSON in tags"]
                })
        
        # Write report
        with open(self.report, 'w') as f:
            json.dump(report, f, indent=2)
            logger.info(f"Validation report written to {self.report}")

    def execute(self) -> bool:
        """Execute validate command."""
        try:
            if self.guid:
                # Validate single episode
                episode = get_episode(self.guid)
                if not episode:
                    logger.error(f"Episode with GUID {self.guid} not found")
                    self.invalid_episodes.append(None)  # Mark as invalid
                    return False
                
                if not episode.tags:
                    logger.warning(f"Episode {self.guid} has no tags")
                    return True
                
                try:
                    tags = json.loads(episode.tags)
                    if not taxonomy.validate_tags(tags):
                        self.invalid_episodes.append(episode)
                        logger.error(f"Invalid tags found for episode {self.guid}")
                        return self.dry_run  # Return True in dry run mode
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON tags for episode {self.guid}")
                    self.invalid_episodes.append(episode)
                    return self.dry_run  # Return True in dry run mode
                except Exception as e:
                    logger.error(f"Error validating tags: {e}")
                    self.invalid_episodes.append(episode)
                    return self.dry_run  # Return True in dry run mode
                
                return True
            
            # Validate multiple episodes
            episodes = get_episodes(limit=self.limit)
            success = True
            for episode in episodes:
                if not episode.tags:
                    logger.warning(f"Episode {episode.guid} has no tags")
                    continue
                
                try:
                    tags = json.loads(episode.tags)
                    if not taxonomy.validate_tags(tags):
                        self.invalid_episodes.append(episode)
                        logger.error(f"Invalid tags found for episode {episode.guid}")
                        if not self.dry_run:  # Only mark as failed if not dry run
                            success = False
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON tags for episode {episode.guid}")
                    self.invalid_episodes.append(episode)
                    if not self.dry_run:  # Only mark as failed if not dry run
                        success = False
                except Exception as e:
                    logger.error(f"Error validating tags: {e}")
                    self.invalid_episodes.append(episode)
                    if not self.dry_run:  # Only mark as failed if not dry run
                        success = False
            
            if not success:
                logger.error("Failed to validate all episodes")
            elif self.invalid_episodes:
                logger.warning(f"Found {len(self.invalid_episodes)} episodes with invalid tags")
            
            if self.report:
                self.generate_report()
            
            return success or self.dry_run  # Return True in dry run mode
            
        except Exception as e:
            logger.error(f"Error validating tags: {e}")
            if self.debug:
                raise
            return self.dry_run  # Return True in dry run mode

    def verify(self) -> bool:
        """Verify validate command execution."""
        if self.dry_run:
            return True
        
        # Return False if any episodes were invalid
        return len(self.invalid_episodes) == 0 