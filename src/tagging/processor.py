"""Batch processing for episode tagging.

This module handles:
- Processing episodes in batches
- Progress tracking and logging
- Error handling and recovery
"""
import logging
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import textwrap

from src.models import Episode
from src.storage import get_connection
from .prompt import load_taxonomy
from .tagger import tag_episode

# Configure logging
logging.basicConfig(level=logging.INFO)
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

def get_untagged_episodes(limit: Optional[int] = None) -> List[Episode]:
    """Get episodes that haven't been tagged yet.
    
    Args:
        limit: Maximum number of episodes to return
        
    Returns:
        List of untagged episodes
        
    Example:
        >>> episodes = get_untagged_episodes(limit=10)
    """
    with get_connection() as conn:
        query = '''
            SELECT guid, title, description, link, published_date,
                   duration, audio_url, cleaned_description
            FROM episodes 
            WHERE tags IS NULL
            ORDER BY RANDOM()
        '''
        
        if limit is not None:
            query += f' LIMIT {limit}'
            
        rows = conn.execute(query).fetchall()
        
        return [
            Episode(
                guid=row['guid'],
                title=row['title'],
                description=row['description'],
                link=row['link'],
                published_date=row['published_date'],
                duration=row['duration'],
                audio_url=row['audio_url'],
                cleaned_description=row['cleaned_description']
            )
            for row in rows
        ]

def process_episodes(
    taxonomy_path: Path,
    limit: Optional[int] = None,
    dry_run: bool = False,
    results_file: Optional[str] = None
) -> List[Dict[str, List[str]]]:
    """Process episodes for tagging.
    
    Args:
        taxonomy_path: Path to taxonomy markdown file
        limit: Maximum number of episodes to process
        dry_run: If True, don't save changes to database
        results_file: Optional path to save results
        
    Returns:
        List of successful tagging results
    """
    try:
        # Load taxonomy
        logger.info("Loading taxonomy from %s", taxonomy_path)
        taxonomy = load_taxonomy(taxonomy_path)
        
        # Get episodes to process
        episodes = get_untagged_episodes(limit=limit)
        if not episodes:
            logger.info("No episodes found for tagging")
            return []
            
        logger.info("Processing %d episodes", len(episodes))
        
        # Open results file if specified
        results_fh = None
        if results_file:
            results_fh = open(results_file, 'w', encoding='utf-8')
            results_fh.write(f"Tagging Results - {datetime.now().isoformat()}\n")
            results_fh.write("=" * 80 + "\n\n")
        
        try:
            # Process each episode
            results = []
            for i, episode in enumerate(episodes, 1):
                logger.info(
                    "Processing episode %d/%d: %s",
                    i, len(episodes), episode.title
                )
                
                # First do a dry run if requested
                if dry_run:
                    logger.info("Performing dry run for %s", episode.guid)
                    tag_episode(episode, taxonomy, dry_run=True)
                    continue
                
                # Tag the episode
                start_time = time.time()
                tags = tag_episode(episode, taxonomy)
                duration = time.time() - start_time
                
                # Log results
                if tags:
                    logger.info(
                        "Successfully tagged episode in %.2f seconds",
                        duration
                    )
                    results.append(tags)
                    
                    if results_fh:
                        results_fh.write(f"Episode: {episode.title}\n")
                        results_fh.write(f"GUID: {episode.guid}\n")
                        results_fh.write(f"Tags: {json.dumps(tags, indent=2)}\n")
                        results_fh.write(f"Duration: {duration:.2f}s\n")
                        results_fh.write("-" * 80 + "\n\n")
                else:
                    logger.error("Failed to tag episode %s", episode.guid)
                    
                    if results_fh:
                        results_fh.write(f"ERROR: Failed to tag {episode.guid}\n\n")
                
            return results
                
        finally:
            # Clean up results file
            if results_fh:
                results_fh.close()
                
    except Exception as e:
        logger.error("Error in batch processing: %s", str(e))
        raise 