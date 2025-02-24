"""OpenAI API client.

This module handles:
- OpenAI API configuration
- API calls with proper error handling
- Response validation
"""
import logging
import openai
from src import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_completion(prompt: str) -> str:
    """Get completion from OpenAI API.
    
    Args:
        prompt: Prompt to send to API
        
    Returns:
        API response text
        
    Raises:
        Exception: If API call fails
    """
    try:
        client = openai.OpenAI(api_key=config.get_openai_api_key())
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a history podcast episode tagger."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Use deterministic output
            timeout=config.API_TIMEOUT
        )
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error("OpenAI API error: %s", str(e))
        raise 