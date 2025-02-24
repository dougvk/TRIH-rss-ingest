"""Main entry point for the RSS Feed Processor CLI."""
import sys
import argparse
import logging
import textwrap
from typing import List, Optional

from . import __version__
from .utils import validate_environment, setup_environment
from .commands import commands

logger = logging.getLogger(__name__)

# Comprehensive help text
DESCRIPTION = """
A comprehensive tool for managing podcast RSS feeds, including ingestion, content cleaning,
taxonomy tagging, data export, and tag validation.

Environment:
    RSS_FEED_URL    URL of the RSS feed to process
    DATA_DIR        Directory for data storage (default: data)
    OPENAI_API_KEY  API key for OpenAI services (required for cleaning and tagging)

Files:
    data/              Base directory for all data storage
    data/episodes.db   Production SQLite database
    data/test.db       Test SQLite database
    data/logs/         Log files directory

Examples:
    # Ingest feed in test environment
    %(prog)s --env test ingest

    # Clean specific episode in production
    %(prog)s --env prod clean --guid episode-123

    # Tag episodes with limit in test environment
    %(prog)s --env test tag --limit 10

    # Export all episodes to JSON
    %(prog)s --env test export --output episodes.json

    # Validate tags and generate report
    %(prog)s --env test validate --report validation.json
"""

def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser.
    
    Returns:
        Configured argument parser
    """
    # Main parser with global options
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See README.md for more detailed documentation."
    )
    
    # Global arguments
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--env",
        choices=["test", "prod"],
        required=True,
        help="Environment to run in (required)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        description="valid commands",
        help="Command to execute",
        required=True  # Make command required
    )
    
    # Each command will register its own subparser with detailed help
    for name, command_class in commands.items():
        command_parser = subparsers.add_parser(
            name,
            help=command_class.__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        command_class.setup_parser(command_parser)
        
        # Add detailed description for each command
        if name == "ingest":
            command_parser.description = textwrap.dedent("""
                Fetch and store feed data from configured RSS URL.
                
                This command will:
                - Fetch the RSS feed from the configured URL
                - Parse the feed content
                - Store episodes in the database
                
                The RSS_FEED_URL environment variable must be set.
            """)
        elif name == "clean":
            command_parser.description = textwrap.dedent("""
                Clean episode descriptions by removing promotional content.
                
                This command will:
                - Remove promotional content using regex patterns
                - Clean content using OpenAI API
                - Store cleaned descriptions in the database
                
                The OPENAI_API_KEY environment variable must be set.
            """)
        elif name == "tag":
            command_parser.description = textwrap.dedent("""
                Tag episodes with taxonomy categories.
                
                This command will:
                - Analyze episode content using OpenAI API
                - Apply taxonomy tags (Format, Theme, Track)
                - Extract episode numbers where applicable
                - Store tags in the database
                
                The OPENAI_API_KEY environment variable must be set.
            """)
        elif name == "export":
            command_parser.description = textwrap.dedent("""
                Export episode data to various formats.
                
                Available fields:
                - guid: Episode unique identifier
                - title: Episode title
                - description: Original description
                - published_date: Publication date
                - link: Episode URL
                - duration: Episode duration
                - audio_url: Audio file URL
                - episode_number: Extracted episode number
                - tags: Applied taxonomy tags
                - cleaned_description: Cleaned description
            """)
        elif name == "validate":
            command_parser.description = textwrap.dedent("""
                Validate episode tags against taxonomy.
                
                This command will:
                - Check tag format and structure
                - Validate tags against taxonomy
                - Generate validation report
                - List any invalid or missing tags
                
                Use --report to generate a detailed JSON report.
            """)
    
    return parser

def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point.
    
    Args:
        argv: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Validate and setup environment
        env = validate_environment(args.env)
        setup_environment(env)
        
        # Create and run command
        command_class = commands[args.command]
        
        # Convert args to dict and remove command-specific args
        command_args = vars(args)
        command_args.pop('command')
        
        # Create command instance with all arguments
        command = command_class(**command_args)
        
        success = command.run()
        return 0 if success else 1
        
    except Exception as e:
        logger.error("Error: %s", str(e))
        if args.debug:
            logger.exception("Detailed error:")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 