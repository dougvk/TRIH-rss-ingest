"""Prompt management for episode tagging.

This module handles:
- Constructing prompts for the OpenAI API
- Validating tag formats and structures
"""
from typing import Dict, List, Union, Optional
from pathlib import Path

from .taxonomy import taxonomy

def construct_prompt(title: str, description: str) -> str:
    """Construct a prompt for the OpenAI API.
    
    Args:
        title: Episode title
        description: Episode description (cleaned)
    """
    # Build the taxonomy section of the prompt
    taxonomy_text = "\nValid tags by category (an episode can have multiple tags from each category):\n"
    for category in taxonomy.categories:
        taxonomy_text += f"\n{category}:\n"
        taxonomy_text += "\n".join(f"- {tag}" for tag in taxonomy[category]) + "\n"
    
    # Construct the full prompt
    prompt = f"""You are a history podcast episode tagger. Your task is to analyze this episode and assign ALL relevant tags from the taxonomy below.

Episode Title: {title}
Episode Description: {description}

IMPORTANT RULES:
1. An episode MUST be tagged as "Series Episodes" if ANY of these are true:
   - The title contains "(Ep X)" or "(Part X)" where X is any number
   - The title contains "Part" followed by a number
   - The episode is part of a named series (e.g. "Young Churchill", "The French Revolution")
2. An episode MUST be tagged as "RIHC Series" if the title starts with "RIHC:"
   - RIHC episodes should ALWAYS have both "RIHC Series" and "Series Episodes" in their Format tags
3. An episode can and should have multiple tags from each category if applicable
4. If none of the above rules apply, tag it as "Standalone Episodes"
5. For series episodes, you MUST extract the episode number:
   - Look for patterns like "(Ep X)", "(Part X)", "Part X", where X is a number
   - Include the number in your response as "episode_number"
   - If no explicit number is found, use null for episode_number

{taxonomy_text}

IMPORTANT:
1. You MUST ONLY use tags EXACTLY as they appear in the taxonomy above
2. You MUST include Format, Theme, Track, and episode_number in your response
3. Make sure themes and tracks are from their correct categories (don't use track names as themes)
4. For Theme and Track:
   - Apply ALL relevant themes and tracks that match the content
   - It's common for an episode to have 2-3 themes and 2-3 tracks
   - Make sure themes and tracks are from their correct categories (don't use track names as themes)

Example responses:

For a RIHC episode about ancient Rome and military history:
{{"Format": ["RIHC Series", "Series Episodes"], "Theme": ["Ancient & Classical Civilizations", "Military History & Battles"], "Track": ["Roman Track", "Military & Battles Track", "The RIHC Bonus Track"], "episode_number": null}}

For a standalone episode about British history:
{{"Format": ["Standalone Episodes"], "Theme": ["Regional & National Histories", "Modern Political History & Leadership"], "Track": ["British History Track", "Modern Political History Track"], "episode_number": null}}

For part 3 of a series about Napoleon:
{{"Format": ["Series Episodes"], "Theme": ["Modern Political History & Leadership", "Military History & Battles"], "Track": ["Modern Political History Track", "Military & Battles Track", "Historical Figures Track"], "episode_number": 3}}

Return tags in this exact JSON format:
{{"Format": ["tag1", "tag2"], "Theme": ["tag1", "tag2"], "Track": ["tag1", "tag2"], "episode_number": number_or_null}}
"""
    return prompt 