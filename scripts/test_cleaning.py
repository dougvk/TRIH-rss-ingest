"""Test script for episode content cleaning."""
import os
import logging
import glob
import textwrap
from datetime import datetime
from src.cleaning import get_sample_episodes, clean_episode
from src.storage import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wrap_text(text: str, width: int = 120) -> str:
    """Wrap text to specified width while preserving paragraphs."""
    paragraphs = text.split('\n\n')
    wrapped = []
    for p in paragraphs:
        # Preserve existing line breaks within paragraphs
        lines = p.split('\n')
        wrapped_lines = []
        for line in lines:
            # Only wrap if line exceeds width
            if len(line) > width:
                wrapped_lines.extend(textwrap.wrap(line, width=width))
            else:
                wrapped_lines.append(line)
        wrapped.append('\n'.join(wrapped_lines))
    return '\n\n'.join(wrapped)

def cleanup_old_results():
    """Remove old cleaning results files."""
    for f in glob.glob("cleaning_results_*.txt"):
        try:
            os.remove(f)
            logger.info("Removed old results file: %s", f)
        except OSError as e:
            logger.warning("Failed to remove %s: %s", f, e)

def main():
    """Test cleaning functionality with a sample of episodes."""
    try:
        # Cleanup old results
        cleanup_old_results()

        # Ensure OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        # Initialize database with new schema
        logger.info("Initializing database with cleaning columns")
        init_db()
        
        # Get sample episodes
        sample_size = 10  # Increased to 10 episodes
        logger.info("Getting sample of %d episodes", sample_size)
        guids = get_sample_episodes(sample_size)
        
        if not guids:
            logger.info("No pending episodes found for cleaning")
            return
            
        logger.info("Found %d episodes to clean", len(guids))
        
        # Open results file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"cleaning_results_{timestamp}.txt"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(wrap_text(f"Cleaning Test Results - {datetime.now().isoformat()}") + "\n")
            f.write("=" * 120 + "\n\n")
            
            # Try cleaning each episode
            for i, guid in enumerate(guids, 1):
                f.write(wrap_text(f"Episode {i} (GUID: {guid})") + "\n")
                f.write("-" * 120 + "\n")
                
                logger.info("Cleaning episode %s", guid)
                
                # First do a dry run
                logger.info("Performing dry run...")
                result = clean_episode(guid, dry_run=True)
                if result:
                    f.write("Dry run successful\n\n")
                
                # Then do the actual cleaning
                logger.info("Performing actual cleaning...")
                result = clean_episode(guid)
                
                if result:
                    logger.info("Cleaning successful")
                    
                    # Write results to file
                    f.write("CLEANING RESULTS:\n")
                    f.write(wrap_text(f"Original length: {len(result.original_description)}") + "\n")
                    f.write(wrap_text(f"Cleaned length: {len(result.cleaned_description)}") + "\n")
                    f.write(wrap_text(f"Modified: {result.is_modified}") + "\n")
                    f.write(wrap_text(f"Timestamp: {result.cleaning_timestamp}") + "\n\n")
                    
                    f.write("ORIGINAL DESCRIPTION:\n")
                    f.write(wrap_text(result.original_description) + "\n\n")
                    
                    f.write("CLEANED DESCRIPTION:\n")
                    f.write(wrap_text(result.cleaned_description) + "\n\n")
                    
                    f.write("=" * 120 + "\n\n")
                else:
                    error_msg = f"Failed to clean episode {guid}"
                    logger.error(error_msg)
                    f.write(wrap_text(f"ERROR: {error_msg}") + "\n\n")
                    
        logger.info("Results saved to %s", results_file)
                
    except Exception as e:
        logger.error("Error in cleaning test: %s", str(e))
        raise

if __name__ == "__main__":
    main() 