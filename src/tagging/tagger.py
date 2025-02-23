"""OpenAI integration for episode tagging.

This module handles:
- OpenAI API calls for tagging
- Tag processing and validation
- Error handling and retries
"""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import openai

from src import config
from src.models import Episode
from src.storage import get_connection, get_episodes
from .prompt import construct_prompt, validate_tags, load_taxonomy

# Get module logger
logger = logging.getLogger(__name__)

def tag_episode(
    episode: Episode,
    taxonomy: Dict[str, List[str]],
    dry_run: bool = False,
    limit: Optional[int] = None  # Not used for single episode
) -> Optional[Dict[str, List[str]]]:
    """Tag a single episode using OpenAI.
    
    Args:
        episode: Episode to tag
        taxonomy: Dictionary of valid tags by category
        dry_run: If True, don't save changes to database
        limit: Not used for single episode tagging
        
    Returns:
        Dictionary of assigned tags by category, or None if tagging fails
        
    Example:
        >>> taxonomy = load_taxonomy(Path("taxonomy.md"))
        >>> episode = get_episode("guid-123")
        >>> tags = tag_episode(episode, taxonomy)
    """
    try:
        # Use cleaned description if available
        description = episode.cleaned_description or episode.description
        
        # Construct the prompt
        prompt = construct_prompt(episode.title, description, taxonomy)
        
        if dry_run:
            logger.info("Dry run - would call OpenAI API with prompt: %s", prompt[:100])
            return None
            
        # Call OpenAI API
        client = openai.OpenAI(api_key=config.get_openai_api_key())
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a history podcast episode tagger."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Use deterministic output
            timeout=config.API_TIMEOUT,
            max_retries=config.API_MAX_RETRIES
        )
        
        # Parse and validate tags
        try:
            tags = json.loads(response.choices[0].message.content)
            if not validate_tags(tags, taxonomy):
                logger.error("Invalid tags returned from API: %s", tags)
                return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse API response: %s", e)
            return None
            
        # Update database if not dry run
        if not dry_run:
            with get_connection() as conn:
                conn.execute('''
                    UPDATE episodes 
                    SET tags = ?,
                        tagging_timestamp = ?,
                        episode_number = ?
                    WHERE guid = ?
                ''', (
                    json.dumps(tags),
                    datetime.now(timezone.utc),
                    tags.get('episode_number'),
                    episode.guid
                ))
                
        return tags
        
    except Exception as e:
        logger.error("Error tagging episode %s: %s", episode.guid, str(e))
        return None

def process_episodes(
    taxonomy: Dict[str, List[str]],
    limit: Optional[int] = config.DEFAULT_LIMIT,
    dry_run: bool = False
) -> List[Dict[str, List[str]]]:
    """Process multiple episodes for tagging.
    
    Args:
        taxonomy: Dictionary of valid tags by category
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
        tags = tag_episode(episode, taxonomy, dry_run)
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