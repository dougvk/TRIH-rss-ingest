"""Testing utilities for the taxonomy module."""
from typing import List, Optional
from .constants import TAXONOMY
from .schema import TaxonomyDict

def create_test_taxonomy(categories: Optional[List[str]] = None) -> TaxonomyDict:
    """Create a subset of the taxonomy for testing.
    
    Args:
        categories: List of categories to include, or None for all
        
    Returns:
        Dictionary with requested categories and their tags
    """
    if categories is None:
        return TAXONOMY.copy()
    return {k: TAXONOMY[k] for k in categories if k in TAXONOMY}

def create_minimal_taxonomy() -> TaxonomyDict:
    """Create a minimal taxonomy for basic testing.
    
    Returns:
        Dictionary with minimal set of tags
    """
    return {
        "Format": [
            "Series Episodes",
            "Standalone Episodes"
        ],
        "Theme": [
            "Ancient & Classical Civilizations",
            "Modern Political History & Leadership"
        ],
        "Track": [
            "Roman Track",
            "Modern Political History Track"
        ]
    } 