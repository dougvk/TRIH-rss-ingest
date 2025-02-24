"""Taxonomy management for episode tagging.

This module handles:
- Taxonomy data structure
- Tag validation
- Category management
"""
from typing import Dict, List, Set, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type alias for tag sets
TagSet = Dict[str, Union[List[str], Optional[int]]]

class Taxonomy:
    """Taxonomy for episode tagging."""
    
    def __init__(self):
        """Initialize taxonomy with predefined categories and tags."""
        self._data = {
            "Format": [
                "Series Episodes",
                "Standalone Episodes",
                "RIHC Series"
            ],
            "Theme": [
                "Ancient & Classical Civilizations",
                "Medieval & Renaissance Europe",
                "Empire, Colonialism & Exploration",
                "Modern History",
                "Military History & Battles",
                "Social & Cultural History",
                "Economic History",
                "Political History",
                "Religious History",
                "Scientific & Technological History"
            ],
            "Track": [
                "Roman Track",
                "Medieval & Renaissance Track",
                "Modern Track",
                "Military & Battles Track",
                "Social Track",
                "Economic Track",
                "Political Track",
                "Religious Track",
                "Scientific Track",
                "The RIHC Bonus Track"
            ]
        }
        
    @property
    def categories(self) -> Set[str]:
        """Get all category names.
        
        Returns:
            Set of category names
        """
        return set(self._data.keys())
        
    def __getitem__(self, category: str) -> List[str]:
        """Get tags for a category.
        
        Args:
            category: Category name
            
        Returns:
            List of tags in the category
            
        Raises:
            KeyError: If category doesn't exist
        """
        return self._data[category]
        
    def validate_tags(self, tags: TagSet) -> bool:
        """Validate that tags conform to the taxonomy.
        
        Args:
            tags: Dictionary of assigned tags by category
            
        Returns:
            True if tags are valid, False otherwise
        """
        try:
            print("\n=== Starting Taxonomy validation ===")
            print(f"Input tags type: {type(tags)}")
            print(f"Input tags: {tags}")
            print(f"Input tags keys: {list(tags.keys())}")
            
            # Basic type check
            if not isinstance(tags, dict):
                print("Failed: tags must be a dictionary")
                return False
                
            # Check required fields
            required_fields = {"Format", "Theme", "Track", "episode_number"}
            missing_fields = required_fields - set(tags.keys())
            print(f"\n=== Required Fields Check ===")
            print(f"Required fields: {required_fields}")
            print(f"Tag keys: {set(tags.keys())}")
            print(f"Missing fields: {missing_fields}")
            print(f"Missing fields type: {type(missing_fields)}")
            print(f"Missing fields length: {len(missing_fields)}")
            print(f"Missing fields bool: {bool(missing_fields)}")
            
            if missing_fields:
                print(f"Validation failed: Missing required fields: {missing_fields}")
                return False
                
            # Validate each category is a list
            for category in ["Format", "Theme", "Track"]:
                print(f"\n=== Validating {category} type ===")
                print(f"{category} value: {tags[category]}")
                print(f"{category} type: {type(tags[category])}")
                if not isinstance(tags[category], list):
                    print(f"Failed: {category} must be a list")
                    return False
                    
            # Format rules must be checked first
            print("\n=== Checking Format rules ===")
            print(f"Format tags: {tags['Format']}")
            print(f"Format tags length: {len(tags['Format'])}")
            # Must have exactly one format tag
            if len(tags["Format"]) != 1:
                print("Failed: Must have exactly one Format tag")
                return False
                
            # RIHC series rules
            if "RIHC Series" in tags["Format"]:
                print("\n=== Checking RIHC Series rules ===")
                print(f"Found RIHC Series in Format tags")
                if "Series Episodes" not in tags["Format"]:
                    print("Failed: RIHC Series must also have Series Episodes")
                    return False
                    
            # Validate each category's tags exist in taxonomy
            for category in ["Format", "Theme", "Track"]:
                print(f"\n=== Validating {category} values ===")
                print(f"Valid tags for {category}: {self._data[category]}")
                print(f"Provided tags: {tags[category]}")
                invalid_tags = set(tags[category]) - set(self._data[category])
                print(f"Invalid tags found: {invalid_tags}")
                print(f"Invalid tags type: {type(invalid_tags)}")
                print(f"Invalid tags length: {len(invalid_tags)}")
                
                if invalid_tags:
                    print(f"Failed: Invalid tags for {category}: {invalid_tags}")
                    return False
                    
            # Validate episode_number
            print("\n=== Validating episode_number ===")
            print(f"episode_number key exists: {'episode_number' in tags}")
            print(f"episode_number value: {tags.get('episode_number')}")
            print(f"episode_number type: {type(tags.get('episode_number'))}")
            
            if tags["episode_number"] is not None and not isinstance(tags["episode_number"], int):
                print("Failed: episode_number must be int or None")
                return False
                        
            print("\n=== Validation successful! ===")
            return True
            
        except Exception as e:
            print(f"\n=== Validation failed with exception ===")
            print(f"Exception type: {type(e)}")
            print(f"Exception message: {str(e)}")
            print(f"Input tags at time of exception: {tags}")
            return False

# Create singleton instance
taxonomy = Taxonomy() 