"""OpenAI integration for episode tagging.

This module provides AI-powered episode tagging with:
- Taxonomy-based categorization
- Episode number detection
- Multi-category tagging
- Validation and error handling

Tagging Process:
1. Load taxonomy from markdown file
2. Construct prompts using episode content
3. Call OpenAI API for tag generation
4. Validate returned tags against taxonomy
5. Store results in database

Tag Categories:
- Format: Series vs. Standalone episodes
- Theme: Historical periods and topics
- Track: Curated content tracks
- Episode Number: Extracted or inferred

Safety Features:
- Dry run mode for testing
- Batch size limits
- Single episode processing
- Tag validation before storage
- Database transaction safety

OpenAI Integration:
- Uses GPT models for intelligent tagging
- Deterministic output (temperature=0)
- Configurable timeouts
- Error handling and retries
- Context-aware prompts

Usage Examples:
    # Tag single episode
    tags = tag_episode(episode, dry_run=True)
    
    # Batch tag with limit
    results = process_episodes(limit=10)
    
    # Get untagged episodes
    episodes = get_untagged_episodes(limit=5)
"""
import json
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional
import openai

from src import config
from src.models import Episode
from src.storage import get_connection, get_episodes
from src.openai_client import get_completion
from .prompt import construct_prompt
from .taxonomy import taxonomy, TagSet

# Get module logger
logger = logging.getLogger(__name__)

def get_untagged_episodes(limit: Optional[int] = None) -> List[Episode]:
    """Get episodes that haven't been tagged yet.
    
    Args:
        limit: Maximum number of episodes to return
        
    Returns:
        List of untagged episodes
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

def extract_episode_number(title: str) -> Optional[int]:
    """Extract episode number from title.
    
    Args:
        title: Episode title
        
    Returns:
        Episode number if found, None otherwise
        
    Examples:
        >>> extract_episode_number("The French Revolution (Part 3)")
        3
        >>> extract_episode_number("Young Churchill (Ep 2)")
        2
        >>> extract_episode_number("The Fall of Rome Part 4")
        4
    """
    patterns = [
        r'\(Ep\s*(\d+)\)',
        r'\(Part\s*(\d+)\)',
        r'Part\s*(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return int(match.group(1))
    return None

def tag_episode(episode: Episode, dry_run: bool = False) -> Optional[Dict]:
    """Tag a single episode using OpenAI.
    
    Args:
        episode: Episode to tag
        dry_run: If True, don't save changes
        
    Returns:
        Dictionary of tags if successful, None if failed or dry run
    """
    try:
        # Use cleaned description if available
        description = episode.cleaned_description or episode.description
        
        # Get tags from OpenAI
        prompt = construct_prompt(episode.title, description)
        
        if dry_run:
            logger.info("Dry run - would call OpenAI API with prompt: %s", prompt[:100])
            return None
            
        response = get_completion(prompt)
        
        try:
            tags = json.loads(response)
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from OpenAI: %s", response)
            return None
            
        # Validate tags
        try:
            taxonomy.validate_tags(tags)
        except Exception as e:
            logger.error("Invalid tags returned from OpenAI: %s - %s", tags, str(e))
            return None
            
        # Store tags if not dry run
        if not dry_run:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE episodes SET tags = ? WHERE guid = ?",
                    (json.dumps(tags), episode.guid)
                )
                
        return tags
        
    except Exception as e:
        logger.error("Error tagging episode %s: %s", episode.guid, str(e))
        return None

def process_episodes(
    limit: Optional[int] = config.DEFAULT_LIMIT,
    dry_run: bool = False
) -> List[TagSet]:
    """Process multiple episodes for tagging.
    
    Args:
        limit: Maximum number of episodes to process
        dry_run: If True, don't save changes to database
        
    Returns:
        List of successful tagging results
    """
    episodes = get_episodes(limit=limit)
    if not episodes:
        logger.info("No episodes found for tagging")
        return []
        
    results = []
    for episode in episodes:
        tags = tag_episode(episode, dry_run)
        if tags:
            results.append(tags)
            
    return results

def get_all_episodes(limit: Optional[int] = None) -> List[Episode]:
    """Get all episodes for tagging.
    
    Args:
        limit: Maximum number of episodes to return
        
    Returns:
        List of episodes
    """
    return get_episodes(limit=limit) 