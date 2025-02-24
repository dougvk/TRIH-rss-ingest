"""Taxonomy structure and validation.

This module provides a structured representation of the taxonomy
while maintaining compatibility with the original dictionary format.
"""
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)

class TaxonomyValidationError(Exception):
    """Base class for validation errors."""
    pass

class InvalidCategoryError(TaxonomyValidationError):
    """Unknown category."""
    pass

class InvalidTagError(TaxonomyValidationError):
    """Invalid tag in category."""
    pass

class MissingRequiredFieldError(TaxonomyValidationError):
    """Required field missing."""
    pass

class InvalidFormatError(TaxonomyValidationError):
    """Format-specific validation error."""
    pass

class TaxonomyCategory:
    """A category in the taxonomy with its valid tags and rules."""
    
    def __init__(self, name: str, valid_tags: List[str], rules: Optional[Dict] = None):
        """Initialize a taxonomy category.
        
        Args:
            name: Category name
            valid_tags: List of valid tags for this category
            rules: Optional dictionary of validation rules
        """
        self.name = name
        self.valid_tags = valid_tags
        self.rules = rules or {}
        
    def validate_tags(self, tags: List[str]) -> None:
        """Validate tags for this category.
        
        Args:
            tags: List of tags to validate
            
        Raises:
            InvalidTagError: If any tag is invalid
            InvalidFormatError: If format-specific rules are violated
        """
        logger.debug("Validating tags for category %s: %s", self.name, tags)
        
        # Check all tags are valid
        invalid_tags = set(tags) - set(self.valid_tags)
        if invalid_tags:
            raise InvalidTagError(f"Invalid tags for {self.name}: {invalid_tags}")
            
        # Check max tags rule, with special case for RIHC Series
        if "max_tags" in self.rules:
            # RIHC Series is allowed to have 2 tags (RIHC Series + Series Episodes)
            if "RIHC Series" in tags:
                if len(tags) > 2:
                    raise InvalidFormatError(
                        f"{self.name} with RIHC Series can have at most 2 tags"
                    )
            else:
                if len(tags) > self.rules["max_tags"]:
                    raise InvalidFormatError(
                        f"{self.name} can have at most {self.rules['max_tags']} tags"
                    )
            
        # Check dependencies
        if "dependencies" in self.rules:
            for tag, required_tags in self.rules["dependencies"].items():
                if tag in tags:
                    missing = set(required_tags) - set(tags)
                    if missing:
                        raise InvalidFormatError(
                            f"{tag} requires tags: {missing}"
                        )

class TaxonomyStructure:
    """Structured representation of the taxonomy."""
    
    def __init__(self):
        """Initialize the taxonomy structure."""
        self.categories = {
            "Format": TaxonomyCategory(
                "Format",
                [
                    "Series Episodes",
                    "Standalone Episodes",
                    "RIHC Series"
                ],
                rules={
                    "max_tags": 1,
                    "dependencies": {
                        "RIHC Series": ["Series Episodes"]
                    }
                }
            ),
            "Theme": TaxonomyCategory(
                "Theme",
                [
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
                ]
            ),
            "Track": TaxonomyCategory(
                "Track",
                [
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
            )
        }
        
    def validate_tags(self, tags: Dict) -> None:
        """Validate a complete set of tags.
        
        Args:
            tags: Dictionary of tags by category
            
        Raises:
            MissingRequiredFieldError: If required fields are missing
            InvalidCategoryError: If category is unknown
            InvalidTagError: If tags are invalid
            InvalidFormatError: If format rules are violated
        """
        logger.debug("Starting validation of tags: %s", tags)
        
        # Check required fields
        required_fields = {"Format", "Theme", "Track", "episode_number"}
        missing_fields = required_fields - set(tags.keys())
        if missing_fields:
            raise MissingRequiredFieldError(f"Missing required fields: {missing_fields}")
            
        # Validate each category
        for category in ["Format", "Theme", "Track"]:
            if not isinstance(tags[category], list):
                raise InvalidTagError(f"{category} must be a list")
            self.categories[category].validate_tags(tags[category])
            
        # Validate episode_number
        if tags["episode_number"] is not None and not isinstance(tags["episode_number"], int):
            raise InvalidTagError("episode_number must be int or None")
            
    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to simple dictionary format.
        
        Returns:
            Dictionary mapping category names to lists of valid tags
        """
        return {
            name: category.valid_tags
            for name, category in self.categories.items()
        }
        
    def __getitem__(self, category: str) -> List[str]:
        """Get valid tags for a category.
        
        Args:
            category: Category name
            
        Returns:
            List of valid tags
            
        Raises:
            InvalidCategoryError: If category doesn't exist
        """
        if category not in self.categories:
            raise InvalidCategoryError(f"Unknown category: {category}")
        return self.categories[category].valid_tags 