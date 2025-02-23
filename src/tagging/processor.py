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
from .prompt import load_taxonomy
from .tagger import tag_episode, get_all_episodes

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

def process_episodes(
    taxonomy_path: Path,
    batch_size: Optional[int] = None,
    dry_run: bool = False,
    results_file: Optional[str] = None
) -> None:
    """Process episodes for tagging.
    
    Args:
        taxonomy_path: Path to taxonomy markdown file
        batch_size: Optional number of episodes to process (None for all)
        dry_run: If True, don't save changes to database
        results_file: Optional path to save results
    """
    try:
        # Load taxonomy
        logger.info("Loading taxonomy from %s", taxonomy_path)
        taxonomy = load_taxonomy(taxonomy_path)
        
        # Get all episodes
        episodes = get_all_episodes(limit=batch_size)
        if not episodes:
            logger.info("No episodes found")
            return
            
        logger.info("Processing %d episodes", len(episodes))
        
        # Open results file if specified
        results_fh = None
        if results_file:
            results_fh = open(results_file, 'w', encoding='utf-8')
            results_fh.write(wrap_text(f"Tagging Results - {datetime.now().isoformat()}") + "\n")
            results_fh.write("=" * 80 + "\n\n")
        
        try:
            # Process each episode
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
                    
                    if results_fh:
                        results_fh.write(wrap_text(f"Episode: {episode.title}") + "\n")
                        results_fh.write(wrap_text(f"GUID: {episode.guid}") + "\n")
                        results_fh.write(wrap_text(f"Tags: {json.dumps(tags, indent=2)}") + "\n")
                        results_fh.write(wrap_text(f"Duration: {duration:.2f}s") + "\n")
                        results_fh.write("-" * 80 + "\n\n")
                else:
                    logger.error("Failed to tag episode %s", episode.guid)
                    
                    if results_fh:
                        results_fh.write(wrap_text(f"ERROR: Failed to tag {episode.guid}") + "\n\n")
                
        finally:
            # Clean up results file
            if results_fh:
                results_fh.close()
                
    except Exception as e:
        logger.error("Error in batch processing: %s", str(e))
        raise 