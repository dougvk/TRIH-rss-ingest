"""RSS feed ingestion functionality."""
from datetime import datetime
import requests
from typing import List
from lxml import etree

from . import config
from .models import Episode

def fetch_rss_feed() -> str:
    """Fetch RSS feed content from configured URL.
    
    Returns:
        str: Raw XML content of the feed
        
    Raises:
        requests.RequestException: If network request fails
        ValueError: If feed URL is not configured
    """
    url = config.get_feed_url()
    if not url:
        raise ValueError("RSS feed URL not configured")
        
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    return response.text

def parse_rss_feed(content: str) -> List[Episode]:
    """Parse RSS feed content into Episode objects.
    
    Args:
        content: Raw XML content of the feed
        
    Returns:
        List[Episode]: List of parsed episodes
        
    Raises:
        ValueError: If feed content is invalid or required fields are missing
        etree.ParseError: If XML content is malformed
    """
    try:
        # Parse XML content
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(content.encode('utf-8'), parser=parser)
        
        # Find all item elements (episodes)
        items = root.findall('.//item')
        if not items:
            raise ValueError("No episodes found in feed")
        
        episodes = []
        for item in items:
            # Helper function to safely get text content
            def get_text(element, default: str = '') -> str:
                return (element.text or default) if element is not None else default
            
            # Get required fields
            title = get_text(item.find('title'))
            description = get_text(item.find('description'))
            link = get_text(item.find('link'))
            guid = get_text(item.find('guid'))
            pub_date = get_text(item.find('pubDate'))
            
            # Optional fields - handle namespaces explicitly
            duration = None
            duration_elem = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')
            if duration_elem is not None:
                duration = duration_elem.text
            
            # Get audio URL from enclosure
            audio_url = None
            enclosure = item.find('enclosure')
            if enclosure is not None:
                audio_url = enclosure.get('url')
            
            # Parse the publication date
            try:
                published_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError as e:
                raise ValueError(f"Invalid date format in feed: {pub_date}") from e
            
            episode = Episode(
                title=title,
                description=description,
                link=link,
                published_date=published_date,
                guid=guid,
                duration=duration,
                audio_url=audio_url
            )
            episodes.append(episode)
        
        return episodes
        
    except etree.ParseError as e:
        raise ValueError(f"Invalid XML content: {str(e)}") 