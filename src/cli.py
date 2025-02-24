"""Command line interface for the RSS feed processor.

This module provides a CLI for:
- Feed ingestion: Fetch and store RSS feed data with optional limits
- Content cleaning: Remove promotional content using regex and OpenAI
- Episode tagging: Apply taxonomy tags using OpenAI
- Data export: Export episode data to JSON

Environment Handling:
- Uses --env flag to switch between production and test databases
- Defaults to production environment
- Test environment uses a separate database to protect production data

Safety Features:
- Dry run mode for all data-modifying operations
- Batch size limits for testing and gradual processing
- Single episode processing by GUID
- Environment validation before operations
- Proper error handling and logging

Usage Examples:
    # Ingest feed (test environment, limit 20 episodes)
    python -m src.cli --env test ingest --limit 20
    
    # Clean content (dry run, 5 episodes)
    python -m src.cli --env test clean --dry-run --limit 5
    
    # Tag episodes (single episode)
    python -m src.cli --env test tag --guid <GUID>
    
    # Export data
    python -m src.cli --env test export --output data/episodes.json
"""
import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

from src import config
from src.feed_ingest import fetch_rss_feed, parse_rss_feed
from src.cleaning import clean_episode, process_episodes as clean_episodes
from src.storage import init_db, store_episodes
from src.tagging.processor import process_episodes as tag_episodes
from src.tagging.tagger import tag_episode
from src.models import Episode

# Configure logging
logger = logging.getLogger(__name__)

def setup_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="RSS Feed Processor CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add global arguments
    parser.add_argument(
        "--env",
        choices=["production", "test"],
        default="production",
        help="Environment to run in (default: production)"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Fetch and store feed data")
    ingest_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    ingest_parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of episodes to process (for testing)"
    )
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean episode descriptions")
    clean_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    clean_parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of episodes to process"
    )
    clean_parser.add_argument(
        "--guid",
        help="Process a single episode by GUID"
    )
    
    # Tag command
    tag_parser = subparsers.add_parser("tag", help="Tag episodes with taxonomy")
    tag_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    tag_parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of episodes to process"
    )
    tag_parser.add_argument(
        "--guid",
        help="Process a single episode by GUID"
    )
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export episode data")
    export_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output file path"
    )
    
    return parser

def ingest_feed(dry_run: bool = False, limit: Optional[int] = None) -> Optional[List[Episode]]:
    """Fetch and store feed data.
    
    Args:
        dry_run: If True, don't save to database
        limit: Maximum number of episodes to process
        
    Returns:
        List of episodes if successful, None if failed
    """
    try:
        # Initialize database
        if not dry_run:
            init_db()
        
        # Fetch and parse feed
        content = fetch_rss_feed()
        episodes = parse_rss_feed(content, limit=limit)
        logger.info("Found %d episodes in feed", len(episodes))
        
        # Store episodes
        if not dry_run:
            store_episodes(episodes)
            logger.info("Successfully stored episodes in database")
        else:
            logger.info("Dry run - would store %d episodes", len(episodes))
            
        return episodes
        
    except Exception as e:
        logger.error("Failed to ingest feed: %s", str(e))
        return None

def clean_content(
    dry_run: bool = False,
    limit: Optional[int] = None,
    guid: Optional[str] = None
) -> bool:
    """Clean episode descriptions.
    
    Args:
        dry_run: If True, don't save changes
        limit: Maximum episodes to process
        guid: Process single episode by GUID
        
    Returns:
        True if successful, False if failed
    """
    try:
        if guid:
            # Clean single episode
            result = clean_episode(guid, dry_run)
            if result:
                logger.info(
                    "Successfully cleaned episode %s (modified: %s)",
                    guid, result.is_modified
                )
                return True
            return False
        else:
            # Clean multiple episodes
            results = clean_episodes(limit=limit, dry_run=dry_run)
            logger.info("Successfully cleaned %d episodes", len(results))
            return True
            
    except Exception as e:
        logger.error("Failed to clean content: %s", str(e))
        return False

def tag_content(
    dry_run: bool = False,
    limit: Optional[int] = None,
    guid: Optional[str] = None
) -> bool:
    """Tag episodes with taxonomy.
    
    Args:
        dry_run: If True, don't save changes
        limit: Maximum episodes to process
        guid: Process single episode by GUID
        
    Returns:
        True if successful, False if failed
    """
    try:
        if guid:
            # Tag single episode
            from src.storage import get_episode
            episode = get_episode(guid)
            if not episode:
                logger.error("Episode not found: %s", guid)
                return False
                
            from src.tagging.tagger import tag_episode
            tags = tag_episode(episode, dry_run)
            
            if tags:
                logger.info("Successfully tagged episode %s", guid)
                return True
            return False
        else:
            # Tag multiple episodes
            from src.tagging.processor import process_episodes
            results = process_episodes(
                limit=limit,
                dry_run=dry_run
            )
            logger.info("Successfully tagged %d episodes", len(results))
            return True
            
    except Exception as e:
        logger.error("Failed to tag content: %s", str(e))
        return False

def export_data(output_path: Path) -> bool:
    """Export episode data to file.
    
    Args:
        output_path: Path to output file
        
    Returns:
        True if successful, False if failed
    """
    try:
        from src.storage import get_episodes
        import json
        
        episodes = get_episodes()
        if not episodes:
            logger.error("No episodes found in database")
            return False
            
        # Convert episodes to dict for JSON serialization
        data = []
        for episode in episodes:
            episode_dict = {
                'guid': episode.guid,
                'title': episode.title,
                'description': episode.description,
                'cleaned_description': episode.cleaned_description,
                'published_date': episode.published_date.isoformat(),
                'link': episode.link,
                'duration': episode.duration,
                'audio_url': episode.audio_url,
                'episode_number': episode.episode_number,
                'tags': json.loads(episode.tags) if episode.tags else None
            }
            data.append(episode_dict)
            
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info("Successfully exported %d episodes to %s", len(episodes), output_path)
        return True
        
    except Exception as e:
        logger.error("Failed to export data: %s", str(e))
        return False

def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for CLI.
    
    Args:
        argv: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = setup_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    
    # Set environment
    os.environ["APP_ENV"] = args.env
    
    # Validate config before proceeding
    try:
        config.validate_config()
    except (ValueError, OSError) as e:
        logger.error("Configuration error: %s", str(e))
        return 1
        
    # Execute command
    success = False
    if args.command == "ingest":
        success = ingest_feed(args.dry_run, args.limit) is not None
    elif args.command == "clean":
        success = clean_content(args.dry_run, args.limit, args.guid)
    elif args.command == "tag":
        success = tag_content(args.dry_run, args.limit, args.guid)
    elif args.command == "export":
        success = export_data(args.output)
    else:
        parser.print_help()
        return 1
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 