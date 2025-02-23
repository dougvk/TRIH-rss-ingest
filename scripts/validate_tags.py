"""Script to validate all episode tags against taxonomy rules."""
import logging
import json
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from src.storage import get_episodes
from src.tagging.prompt import load_taxonomy, validate_tags as validate_tags_base

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_series_name(title: str) -> str:
    """Extract series name from episode title.
    
    Examples:
        "The French Revolution (Part 3)" -> "The French Revolution"
        "Young Churchill (Ep 2)" -> "Young Churchill"
        "The Fall of Rome Part 4" -> "The Fall of Rome"
    """
    # Remove common episode/part indicators
    patterns = [
        r'\s*\(Ep\s*\d+\)\s*$',
        r'\s*\(Part\s*\d+\)\s*$',
        r'\s+Part\s*\d+\s*$'
    ]
    
    series_name = title
    for pattern in patterns:
        series_name = re.sub(pattern, '', series_name)
    return series_name.strip()

def validate_series_numbers(episodes: List[Dict]) -> List[Dict]:
    """Validate episode numbers within each series."""
    errors = []
    series_episodes = defaultdict(list)
    
    # Group episodes by series
    for episode in episodes:
        if not episode.tags:
            continue
            
        try:
            tags = json.loads(episode.tags) if isinstance(episode.tags, str) else episode.tags
        except json.JSONDecodeError:
            continue
            
        if "Format" in tags and "Series Episodes" in tags["Format"] and "RIHC Series" not in tags["Format"]:
            series_name = extract_series_name(episode.title)
            if series_name and "episode_number" in tags and tags["episode_number"] is not None:
                series_episodes[series_name].append({
                    "guid": episode.guid,
                    "title": episode.title,
                    "number": tags["episode_number"]
                })
    
    # Check each series for sequence issues
    for series_name, episodes in series_episodes.items():
        if len(episodes) <= 1:
            continue
            
        # Sort by episode number
        episodes.sort(key=lambda x: x["number"])
        
        # Check for gaps and duplicates
        expected_number = episodes[0]["number"]
        for episode in episodes:
            if episode["number"] != expected_number:
                errors.append({
                    "guid": episode["guid"],
                    "title": episode["title"],
                    "errors": [f"Episode number {episode['number']} in series '{series_name}' breaks sequence - expected {expected_number}"]
                })
            expected_number += 1
    
    return errors

def get_validation_errors(tags: Dict, taxonomy: Dict, episode_title: str) -> List[str]:
    """Get validation errors for episode tags."""
    errors = []
    
    # Basic validation using the base validator
    if not validate_tags_base(tags, taxonomy):
        # Add specific error messages based on what failed
        required_fields = {"Format", "Theme", "Track"}
        missing_fields = required_fields - set(tags.keys())
        if missing_fields:
            errors.append(f"Missing required fields: {missing_fields}")
            
        for category in ["Format", "Theme", "Track"]:
            if category in tags:
                valid_tags = set(taxonomy[category])
                invalid_tags = set(tags[category]) - valid_tags
                if invalid_tags:
                    errors.append(f"Invalid {category} tags: {invalid_tags}")
                    
        if "episode_number" in tags:
            if tags["episode_number"] is not None and not isinstance(tags["episode_number"], (int, float)):
                errors.append("episode_number must be an integer or null")
                
        # Additional format-specific validations
        if "Format" in tags:
            if len(tags["Format"]) != 1:
                errors.append("Episode must have exactly one Format tag")
                
            # Check RIHC series rules
            if episode_title.startswith("RIHC:"):
                required_format = {"RIHC Series", "Series Episodes"}
                if not all(fmt in tags["Format"] for fmt in required_format):
                    errors.append("RIHC episodes must have both 'RIHC Series' and 'Series Episodes' format tags")
            
            # Check series episode rules
            if "Series Episodes" in tags["Format"] and "RIHC Series" not in tags["Format"]:
                if "episode_number" not in tags or tags["episode_number"] is None:
                    errors.append("Non-RIHC series episodes must have an episode number")
    
    return errors

def main():
    """Validate tags for all episodes."""
    # Load taxonomy
    taxonomy_path = Path("src/tagging/Tagging-Episodes-Framework.md")
    if not taxonomy_path.exists():
        logger.error("Taxonomy file not found: %s", taxonomy_path)
        return
    
    taxonomy = load_taxonomy(taxonomy_path)
    episodes = get_episodes()
    
    logger.info("Starting tag validation for %d episodes", len(episodes))
    
    episodes_with_errors = []
    
    # First validate individual episode tags
    for episode in episodes:
        if not episode.tags:
            episodes_with_errors.append({
                "guid": episode.guid,
                "title": episode.title,
                "errors": ["No tags found"]
            })
            continue
            
        try:
            tags = json.loads(episode.tags) if isinstance(episode.tags, str) else episode.tags
        except json.JSONDecodeError:
            episodes_with_errors.append({
                "guid": episode.guid,
                "title": episode.title,
                "errors": ["Invalid JSON in tags"]
            })
            continue
            
        errors = get_validation_errors(tags, taxonomy, episode.title)
        if errors:
            episodes_with_errors.append({
                "guid": episode.guid,
                "title": episode.title,
                "errors": errors
            })
    
    # Then validate series episode numbers
    series_errors = validate_series_numbers(episodes)
    episodes_with_errors.extend(series_errors)
    
    # Print results
    if episodes_with_errors:
        print("\nFound tag validation errors:")
        print("-" * 80)
        for episode in episodes_with_errors:
            print(f"\nEpisode: {episode['title']}")
            print(f"GUID: {episode['guid']}")
            print("Errors:")
            for error in episode['errors']:
                print(f"  - {error}")
        print(f"\nTotal episodes with errors: {len(episodes_with_errors)}")
    else:
        print("\nAll episode tags are valid!")
    
    logger.info("Validation complete")

if __name__ == "__main__":
    main() 