"""Script to tag a single episode."""
import sys
import logging
import json
from pathlib import Path
from src.tagging.tagger import tag_episode
from src.storage import get_episode
from src.tagging.prompt import load_taxonomy, validate_tags as validate_tags_base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Tag a single episode by GUID."""
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.tag_single <guid>")
        sys.exit(1)
        
    guid = sys.argv[1]
    logger.info("Tagging episode: %s", guid)
    
    # Load taxonomy
    taxonomy_path = Path("src/tagging/Tagging-Episodes-Framework.md")
    if not taxonomy_path.exists():
        logger.error("Taxonomy file not found: %s", taxonomy_path)
        sys.exit(1)
    
    taxonomy = load_taxonomy(taxonomy_path)
    episode = get_episode(guid)
    
    if not episode:
        logger.error("Episode not found: %s", guid)
        sys.exit(1)
    
    # First do a dry run
    logger.info("Performing dry run...")
    tags = tag_episode(episode, taxonomy, dry_run=True)
    if tags:
        logger.info("Dry run successful")
    
    # Then do the actual tagging
    logger.info("Performing actual tagging...")
    tags = tag_episode(episode, taxonomy)
    
    if tags:
        logger.info("Tagging successful")
        print("\nAssigned tags:")
        print("-" * 80)
        print(json.dumps(tags, indent=2))
    else:
        logger.error("Failed to tag episode")
        sys.exit(1)

if __name__ == "__main__":
    main() 