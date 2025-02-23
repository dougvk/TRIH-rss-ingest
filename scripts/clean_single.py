"""Script to clean a single episode."""
import sys
import logging
from src.cleaning import clean_episode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Clean a single episode by GUID."""
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.clean_single <guid>")
        sys.exit(1)
        
    guid = sys.argv[1]
    logger.info("Cleaning episode: %s", guid)
    
    # First do a dry run
    logger.info("Performing dry run...")
    result = clean_episode(guid, dry_run=True)
    if result:
        logger.info("Dry run successful")
    
    # Then do the actual cleaning
    logger.info("Performing actual cleaning...")
    result = clean_episode(guid)
    
    if result:
        logger.info("Cleaning successful")
        logger.info("Original length: %d", len(result.original_description))
        logger.info("Cleaned length: %d", len(result.cleaned_description))
        logger.info("Modified: %s", result.is_modified)
        logger.info("Timestamp: %s", result.cleaning_timestamp)
        
        print("\nOriginal description:")
        print("-" * 80)
        print(result.original_description)
        print("\nCleaned description:")
        print("-" * 80)
        print(result.cleaned_description)
    else:
        logger.error("Failed to clean episode")
        sys.exit(1)

if __name__ == "__main__":
    main() 