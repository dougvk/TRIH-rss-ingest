"""Test script for episode tagging."""
import os
import glob
import logging
import textwrap
import json
from datetime import datetime
from pathlib import Path

from src.storage import init_db
from src.tagging.processor import process_episodes
from src.cleaning import get_sample_episodes, clean_episode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wrap_text(text: str, width: int = 120) -> str:
    """Wrap text to specified width while preserving structure.
    
    Args:
        text: Text to wrap
        width: Maximum line width
        
    Returns:
        Wrapped text with preserved structure
    """
    # For JSON-like content, pretty print it first
    if text.strip().startswith('{'):
        try:
            data = json.loads(text)
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            pass
    
    # Split into paragraphs
    paragraphs = text.split('\n\n')
    wrapped = []
    
    for p in paragraphs:
        # Handle lines separately within each paragraph
        lines = p.split('\n')
        wrapped_lines = []
        
        for line in lines:
            # Skip wrapping for separator lines
            if all(c == '=' for c in line) or all(c == '-' for c in line):
                wrapped_lines.append(line)
                continue
                
            # For normal lines, wrap if they exceed width
            if len(line) > width:
                # Preserve any leading whitespace
                leading_space = len(line) - len(line.lstrip())
                indent = ' ' * leading_space
                
                # Wrap the line content
                wrapped_content = textwrap.fill(
                    line.lstrip(),
                    width=width - leading_space,
                    subsequent_indent=indent
                )
                wrapped_lines.append(wrapped_content)
            else:
                wrapped_lines.append(line)
                
        wrapped.append('\n'.join(wrapped_lines))
    
    return '\n\n'.join(wrapped)

def cleanup_old_results():
    """Remove old tagging results files."""
    for f in glob.glob("tagging_results_*.txt"):
        try:
            os.remove(f)
            logger.info("Removed old results file: %s", f)
        except OSError as e:
            logger.warning("Failed to remove %s: %s", f, e)

def main():
    """Test episode tagging functionality."""
    try:
        # Clean up old results files
        cleanup_old_results()
        
        # Ensure OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        # Initialize database with new columns if needed
        logger.info("Initializing database with tagging columns")
        init_db()
        
        # Set up paths and files
        taxonomy_path = Path("Tagging-Episodes-Framework.md")
        if not taxonomy_path.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {taxonomy_path}")
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"tagging_results_{timestamp}.txt"
        
        # Process a small batch with dry run first
        logger.info("Performing dry run...")
        process_episodes(
            taxonomy_path=taxonomy_path,
            batch_size=20,
            dry_run=True
        )
        
        # Process actual batch
        logger.info("Processing episodes...")
        process_episodes(
            taxonomy_path=taxonomy_path,
            batch_size=20,
            dry_run=False,
            results_file=results_file
        )
        
        logger.info("Results saved to %s", results_file)
                
    except Exception as e:
        logger.error("Error in tagging test: %s", str(e))
        raise

if __name__ == "__main__":
    main() 