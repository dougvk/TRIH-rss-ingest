"""Export command for episode data."""
import os
import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any
import argparse

from src.storage import get_episodes
from .base import Command
from .registry import register

logger = logging.getLogger(__name__)

@register("export")
class ExportCommand(Command):
    """Export episode data to various formats."""
    
    def __init__(
        self,
        env: str,
        output: Path = None,
        format: str = "json",
        fields: List[str] = None,
        dry_run: bool = False,
        debug: bool = False
    ):
        """Initialize command.
        
        Args:
            env: Environment (test/prod)
            output: Output file path
            format: Output format (json/csv)
            fields: Fields to include in export
            dry_run: If True, show what would be done
            debug: If True, enable debug output
        """
        super().__init__(env, dry_run, debug)
        self.output = output
        self.format = format.lower()
        self.fields = fields or [
            "guid", "title", "description", "published_date",
            "link", "duration", "audio_url", "episode_number",
            "tags", "cleaned_description"
        ]
    
    @staticmethod
    def setup_parser(parser: argparse.ArgumentParser) -> None:
        """Set up argument parser for this command.
        
        Args:
            parser: Parser to configure
        """
        parser.add_argument(
            "--output",
            type=Path,
            required=True,
            help="Output file path"
        )
        parser.add_argument(
            "--format",
            choices=["json", "csv"],
            default="json",
            help="Output format (default: json)"
        )
        parser.add_argument(
            "--fields",
            nargs="+",
            help="Fields to include in export"
        )
    
    def validate(self) -> bool:
        """Validate command can be executed.
        
        Returns:
            True if validation passes
        """
        if not super().validate():
            return False
        
        # Check output is provided
        if not self.output:
            raise ValueError("Output file path is required")
        
        # Check output directory exists and is writable
        output_dir = self.output.parent
        if not output_dir.exists():
            raise ValueError(f"Output directory does not exist: {output_dir}")
        if not os.access(output_dir, os.W_OK):
            raise ValueError(f"Output directory is not writable: {output_dir}")
        
        # Validate format
        if self.format not in ["json", "csv"]:
            raise ValueError(f"Invalid format: {self.format}")
        
        # Validate fields
        valid_fields = {
            "guid", "title", "description", "published_date",
            "link", "duration", "audio_url", "episode_number",
            "tags", "cleaned_description"
        }
        if self.fields:
            invalid_fields = set(self.fields) - valid_fields
            if invalid_fields:
                raise ValueError(f"Invalid fields: {invalid_fields}")
        
        return True
    
    def execute(self) -> bool:
        """Execute the command.
        
        Returns:
            True if successful
        """
        try:
            # Get episodes
            episodes = get_episodes()
            if not episodes:
                logger.error("No episodes found in database")
                return False
            
            logger.info("Found %d episodes", len(episodes))
            
            # Convert episodes to dict
            data = []
            for episode in episodes:
                episode_dict = {
                    field: getattr(episode, field)
                    for field in self.fields
                }
                # Handle special fields
                if "published_date" in episode_dict:
                    episode_dict["published_date"] = episode_dict["published_date"].isoformat()
                if "tags" in episode_dict and episode_dict["tags"]:
                    episode_dict["tags"] = json.loads(episode_dict["tags"])
                data.append(episode_dict)
            
            if self.dry_run:
                logger.info(
                    "Would export %d episodes to %s in %s format",
                    len(data), self.output, self.format
                )
                return True
            
            # Export data
            if self.format == "json":
                self._export_json(data)
            else:
                self._export_csv(data)
            
            logger.info(
                "Successfully exported %d episodes to %s",
                len(data), self.output
            )
            return True
            
        except Exception as e:
            logger.error("Failed to export data: %s", str(e))
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
            # Check file exists and is not empty
            if not self.output.exists():
                logger.error("Output file not created: %s", self.output)
                return False
            
            if self.output.stat().st_size == 0:
                logger.error("Output file is empty: %s", self.output)
                return False
            
            return True
            
        except Exception as e:
            logger.error("Verification failed: %s", str(e))
            return False
    
    def _export_json(self, data: List[Dict[str, Any]]) -> None:
        """Export data as JSON.
        
        Args:
            data: List of episode dictionaries
        """
        with open(self.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, data: List[Dict[str, Any]]) -> None:
        """Export data as CSV.
        
        Args:
            data: List of episode dictionaries
        """
        if not data:
            return
            
        with open(self.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(data) 