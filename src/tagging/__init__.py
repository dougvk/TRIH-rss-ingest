"""Tagging module for episode content analysis and categorization."""
from .tagger import tag_episode
from .taxonomy import taxonomy

__all__ = ['tag_episode', 'taxonomy'] 