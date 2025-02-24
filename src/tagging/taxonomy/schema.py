"""Type definitions and schema validation for taxonomy."""
from typing import Dict, List, Optional, TypedDict, Union
from typing_extensions import NotRequired

class TagSet(TypedDict):
    """Type definition for a set of tags."""
    Format: List[str]
    Theme: List[str]
    Track: List[str]
    episode_number: NotRequired[Optional[int]]

# Type aliases for clarity
CategoryName = str
TagName = str
TaxonomyDict = Dict[CategoryName, List[TagName]]

# Validation errors
class TaxonomyError(Exception):
    """Base class for taxonomy errors."""
    pass

class InvalidCategoryError(TaxonomyError):
    """Raised when a category is not in the taxonomy."""
    pass

class InvalidTagError(TaxonomyError):
    """Raised when a tag is not in the taxonomy."""
    pass

class InvalidTagSetError(TaxonomyError):
    """Raised when a tag set is invalid."""
    pass 