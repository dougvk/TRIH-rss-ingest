"""Taxonomy package for managing episode tags."""
from .structure import (
    TaxonomyStructure,
    TaxonomyValidationError,
    InvalidCategoryError,
    InvalidTagError,
    MissingRequiredFieldError,
    InvalidFormatError
)
from .schema import TagSet, InvalidTagSetError
from .taxonomy import Taxonomy

# Create singleton instance
taxonomy = Taxonomy()

__all__ = [
    'TaxonomyStructure',
    'TaxonomyValidationError',
    'InvalidCategoryError',
    'InvalidTagError',
    'MissingRequiredFieldError',
    'InvalidFormatError',
    'TagSet',
    'InvalidTagSetError',
    'taxonomy'
] 