"""Core taxonomy logic and singleton instance."""
import re
from typing import List, Optional, Set
import logging

from .constants import TAXONOMY
from .schema import (
    TagSet, TaxonomyDict, CategoryName, TagName,
    TaxonomyError, InvalidCategoryError, InvalidTagError, InvalidTagSetError
)

logger = logging.getLogger(__name__)

class Taxonomy:
    """Singleton class for managing the taxonomy."""
    
    _instance = None
    _taxonomy: TaxonomyDict = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._taxonomy = TAXONOMY.copy()
        return cls._instance
    
    @property
    def categories(self) -> List[CategoryName]:
        """Get list of all categories."""
        return list(self._taxonomy.keys())
    
    def get_tags(self, category: CategoryName) -> List[TagName]:
        """Get all tags for a category.
        
        Args:
            category: Name of the category
            
        Returns:
            List of tags in that category
            
        Raises:
            InvalidCategoryError: If category doesn't exist
        """
        if category not in self._taxonomy:
            raise InvalidCategoryError(f"Unknown category: {category}")
        return self._taxonomy[category].copy()
    
    def validate_tag(self, category: CategoryName, tag: TagName) -> bool:
        """Check if a tag is valid for a category.
        
        Args:
            category: Category to check
            tag: Tag to validate
            
        Returns:
            True if tag is valid
        """
        try:
            return tag in self.get_tags(category)
        except InvalidCategoryError:
            return False
    
    def validate_tags(self, tags: TagSet) -> bool:
        """Validate a complete set of tags.
        
        Args:
            tags: Dictionary of tags by category
            
        Returns:
            True if all tags are valid
            
        Raises:
            InvalidTagSetError: If tag set is invalid
            InvalidCategoryError: If category is unknown
            InvalidTagError: If tag is invalid
        """
        # Check required categories exist
        required = {"Format", "Theme", "Track"}
        if not all(category in tags for category in required):
            raise InvalidTagSetError("Missing required categories")
        
        # Check episode_number is valid
        if "episode_number" in tags:
            episode_number = tags["episode_number"]
            if episode_number is not None and not isinstance(episode_number, int):
                raise InvalidTagSetError("episode_number must be int or None")
        
        # Check Format tags
        format_tags = tags["Format"]
        if "RIHC Series" in format_tags:
            # For RIHC Series, must have exactly Series Episodes and RIHC Series
            if set(format_tags) != {"RIHC Series", "Series Episodes"}:
                raise InvalidTagSetError("RIHC Series must have exactly Series Episodes as its other tag")
        else:
            # For non-RIHC Series, must have exactly one tag
            if len(format_tags) != 1:
                raise InvalidTagSetError("Format must have exactly one tag")
        
        # Validate all tags
        for category, tag_list in tags.items():
            if category == "episode_number":
                continue
            if category not in self._taxonomy:
                raise InvalidCategoryError(f"Unknown category: {category}")
            valid_tags = set(self._taxonomy[category])
            invalid_tags = set(tag_list) - valid_tags
            if invalid_tags:
                raise InvalidTagError(
                    f"Invalid tags for {category}: {invalid_tags}"
                )
        
        return True
    
    def extract_episode_number(self, title: str) -> Optional[int]:
        """Extract episode number from title.
        
        Args:
            title: Episode title
            
        Returns:
            Episode number if found, None otherwise
        """
        patterns = [
            r'\(Ep\s*(\d+)\)',  # (Ep X)
            r'\(Part\s*(\d+)\)',  # (Part X)
            r'Part\s*(\d+)',  # Part X
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        return None
    
    def determine_format(self, title: str) -> Set[str]:
        """Determine format tags based on title.
        
        Args:
            title: Episode title
            
        Returns:
            Set of format tags
        """
        formats = set()
        
        # Check for series indicators
        is_series = any([
            self.extract_episode_number(title) is not None,
            "Part" in title and any(c.isdigit() for c in title),
            any(word in title for word in ["Series", "Season"])
        ])
        
        if is_series:
            formats.add("Series Episodes")
        
        # Check for RIHC series
        if title.startswith("RIHC:"):
            formats.add("RIHC Series")
            formats.add("Series Episodes")
        
        # Default to standalone if no other format
        if not formats:
            formats.add("Standalone Episodes")
        
        return formats
    
    def __getitem__(self, category: CategoryName) -> List[TagName]:
        """Get tags for a category using dictionary syntax."""
        return self.get_tags(category)

# Global singleton instance
taxonomy = Taxonomy() 