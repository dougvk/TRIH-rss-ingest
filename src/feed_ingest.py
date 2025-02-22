"""RSS feed ingestion functionality."""
import requests
from . import config

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