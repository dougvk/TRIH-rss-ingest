"""Process episodes for tagging.

This module handles:
- Batch processing of episodes
- Logging and error handling
- Results file management
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from src.models import Episode
from src.tagging.tagger import tag_episode, get_untagged_episodes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_episodes(
    limit: Optional[int] = None,
    dry_run: bool = False,
    results_file: Optional[str] = None
) -> List[Dict]:
    """Process episodes for tagging.
    
    Args:
        limit: Maximum number of episodes to process
        dry_run: If True, don't save changes
        results_file: Path to save results
        
    Returns:
        List of tag dictionaries for processed episodes
    """
    # Get untagged episodes
    episodes = get_untagged_episodes(limit)
    if not episodes:
        logger.info("No untagged episodes found")
        return []
        
    logger.info("Processing %d episodes", len(episodes))
    results = []
    
    # Process each episode
    for episode in episodes:
        try:
            tags = tag_episode(episode, dry_run=dry_run)
            if tags:
                results.append(tags)
                
                # Log results if file specified
                if results_file and not dry_run:
                    with open(results_file, 'a', encoding='utf-8') as f:
                        f.write(f"\nEpisode: {episode.title}\n")
                        f.write(f"GUID: {episode.guid}\n")
                        f.write("Tags:\n")
                        f.write(json.dumps(tags, indent=2))
                        f.write("\n" + "-" * 80 + "\n")
                        
        except Exception as e:
            logger.error("Error processing episode %s: %s", episode.guid, str(e))
            
    logger.info("Successfully processed %d episodes", len(results))
    return results 