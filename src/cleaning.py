"""Episode content cleaning functionality.

This module handles cleaning episode descriptions through a two-step process:
1. Regex-based Cleaning:
   - Removes common promotional content using predefined patterns
   - Cleans social media handles and links
   - Removes production credits and show notes
   - Handles various promotional formats (live shows, tours, etc.)

2. AI-based Cleaning (OpenAI):
   - Intelligent content analysis using GPT models
   - Preserves historical content while removing promotions
   - Maintains original writing style and tone
   - Context-aware cleaning using episode titles

Data Tracking:
- Cleaning status stored in database
- Timestamps for cleaning operations
- Modification tracking (is_modified flag)
- Original and cleaned descriptions preserved

Safety Features:
- Dry run mode for testing
- Batch size limits
- Single episode processing
- Error handling and logging
- Database transaction safety

Regex Patterns:
- 40+ patterns for common promotional content
- Pattern categories:
  - Social media and contact info
  - Live show announcements
  - Tour dates and tickets
  - Production credits
  - Website links
  - Membership promotions

Usage Examples:
    # Clean single episode
    result = clean_episode("episode-guid", dry_run=True)
    
    # Batch clean with limit
    results = process_episodes(limit=10)
    
    # Get random sample for testing
    guids = get_sample_episodes(sample_size=5)
"""
import re
from datetime import datetime, timezone
from typing import List, Optional
import logging
import openai
import os
from dataclasses import dataclass

from src import config
from src.storage import get_connection, get_episode, get_episodes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CleaningResult:
    """Result of cleaning an episode description."""
    episode_guid: str
    original_description: str
    cleaned_description: str
    is_modified: bool
    cleaning_timestamp: datetime

# Regex patterns for common promotional content
PROMO_PATTERNS = [
    r'\n*(?:Twitter:|A Goalhanger Films|Producer:|Executive Producer|Produced by|Exec Producer|Assistant|Editor:).*?$',
    r'\n*See acast\.com/privacy.*?$',
    r'\n*Email:.*?$',
    r'\n+_+\n*$',  # Remove underscores at the end
    r'\n*LIVE SHOWS.*?Tickets.*?$',  # Remove live show announcements
    r'\n*\*The Rest Is History LIVE.*?$',  # Remove show promos
    r'\n*\*The Rest Is History Live Tour \d{4}\*:.*?$',  # Remove tour announcements
    r'\n*Buy your tickets here:.*?$',  # Remove ticket links
    r'\n*Tickets on sale now at.*?$',  # Remove ticket sale announcements
    r'(?:^|\n)Tom and Dominic are (?:going on|back on) (?:a |an )?(?:U\.?S\.|international )?tour.*?$',
    r'\n*Tom and Dominic are back onstage.*?$',
    r'\n*TRIH LIVE SHOW TICKETS.*?$',
    r'\n*We\'re giving you, our members,.*?tickets.*?$',
    r'(?s)\n*If you live in the States.*?Tickets on sale now.*?$',
    r'book tickets now.*?$',
    r'\n*Description: \*The Rest Is History Live Tour.*?$',
    r'.*?live show on Wagner and Tchaikovsky at The Royal Albert Hall.*?$',
    r'.*?Royal Albert Show on Mozart and Beethoven.*?$',
    r'.*?their recent Athelstan party and live shows.*?$',
    r'.*?last night\'s live show in audio form.*?$',
    r'.*?live show recorded in Leicester Square.*?$',
    r'.*?live show on cinema and history.*?$',
    r'.*?our first overseas live show.*?$',
    r'.*?pre-match nerves before a podcast, a live show.*?$',
    r'.*?Catch up on last night\'s live show.*?$',
    r'.*?our live show.*?$',
    r'.*?their first overseas live show.*?$',
    r'.*?our recent Dublin trip.*?$',
    r'.*?their U\.?S\. tour.*?$',
    r'.*?Tom\'s tour of Britain.*?$',
    r'.*?upcoming series.*?$',
    r'.*?EXCLUSIVE NordVPN.*?$',
    r'\n*\*The Rest Is History Live Tour.*?$',
    r'.*?robomagiclive\.com.*?$',
    r'.*?RESTISHISTORY22.*?$',
    r'.*?link\.dice\.fm.*?$',
    r'.*?Join The Rest Is History Club.*?$',
    r'.*?www\.restishistorypod\.com.*?$',
    r'.*?restishistorypod\.com.*?$',
    r'.*?Please check your welcome email.*?Discord.*?$',
    r'Description: Tom and Dominic are going on.*?$',
    r'.*?live streamed shows.*?$',
    r'.*?exclusive chatroom community.*?$',
]

def apply_regex_cleaning(text: str) -> str:
    """Apply regex-based cleaning to remove common promotional content.
    
    Args:
        text: Original text to clean
        
    Returns:
        Cleaned text with promotional content removed
    """
    cleaned = text
    for pattern in PROMO_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.MULTILINE)
    
    # Clean up Twitter handles
    cleaned = re.sub(r'@\w+', '', cleaned)
    
    # Clean up extra newlines and whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned)
    
    return cleaned.strip()

def clean_with_openai(text: str, title: str, dry_run: bool = False) -> Optional[str]:
    """Clean text using OpenAI's API to remove promotional content.
    
    Args:
        text: Text to clean
        title: Episode title for context
        dry_run: If True, only simulate the API call
        
    Returns:
        Cleaned text or None if API call fails
    """
    if dry_run:
        logger.info("Dry run - would call OpenAI API with text: %s", text[:100])
        return None
        
    try:
        client = openai.OpenAI(api_key=config.get_openai_api_key())
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": """You are a content cleaner for podcast episode descriptions. 
                Remove all promotional content, advertisements, social media links, and production credits.
                Keep only the historical content and episode summary.
                Preserve the original writing style and tone.
                Do not add any new content or modify the historical information.
                Pay special attention to content that matches or relates to the episode title."""},
                {"role": "user", "content": f"Clean this episode description for episode titled '{title}':\n\n{text}"}
            ],
            temperature=0.0,  # Use deterministic output
            timeout=config.API_TIMEOUT
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("OpenAI API error: %s", str(e))
        return None

def clean_episode(
    guid: str,
    dry_run: bool = False,
    limit: Optional[int] = None
) -> Optional[CleaningResult]:
    """Clean a single episode's description.
    
    Args:
        guid: Episode GUID to clean
        dry_run: If True, don't save changes to database
        limit: Not used for single episode cleaning
        
    Returns:
        CleaningResult if successful, None if failed
    """
    episode = get_episode(guid)
    if not episode:
        logger.error("Episode not found: %s", guid)
        return None
        
    # First apply regex cleaning
    regex_cleaned = apply_regex_cleaning(episode.description)
    
    # Then use OpenAI for additional cleaning
    final_cleaned = clean_with_openai(regex_cleaned, episode.title, dry_run)
    if not final_cleaned:
        return None
        
    result = CleaningResult(
        episode_guid=guid,
        original_description=episode.description,
        cleaned_description=final_cleaned,
        is_modified=final_cleaned != episode.description,
        cleaning_timestamp=datetime.now(timezone.utc)
    )
    
    if not dry_run:
        with get_connection() as conn:
            conn.execute('''
                UPDATE episodes 
                SET cleaned_description = ?,
                    cleaning_timestamp = ?,
                    cleaning_status = ?
                WHERE guid = ?
            ''', (
                result.cleaned_description,
                result.cleaning_timestamp,
                'cleaned' if result.is_modified else 'no_changes_needed',
                result.episode_guid
            ))
            
    return result

def process_episodes(
    limit: Optional[int] = config.DEFAULT_LIMIT,
    dry_run: bool = False
) -> List[CleaningResult]:
    """Process multiple episodes for cleaning.
    
    Args:
        limit: Maximum number of episodes to process
        dry_run: If True, don't save changes to database
        
    Returns:
        List of successful cleaning results
    """
    episodes = get_episodes(limit=limit)
    if not episodes:
        logger.info("No episodes found for cleaning")
        return []
        
    results = []
    for episode in episodes:
        result = clean_episode(episode.guid, dry_run)
        if result:
            results.append(result)
            
    return results

def get_sample_episodes(sample_size: int | None = 10) -> List[str]:
    """Get a random sample of episode GUIDs for cleaning.
    
    Args:
        sample_size: Number of episodes to sample, or None for all episodes
        
    Returns:
        List of episode GUIDs
    """
    with get_connection() as conn:
        query = '''
            SELECT guid FROM episodes 
            ORDER BY RANDOM()
        '''
        
        if sample_size is not None:
            query += f' LIMIT {sample_size}'
            
        rows = conn.execute(query).fetchall()
        
    return [row['guid'] for row in rows] 