"""Base command structure and registry for CLI commands."""
from typing import Dict, Type
import logging

# Import base command class
from .base import Command

# Import registry
from .registry import commands

# Import all commands to register them
from .export import ExportCommand
from .ingest import IngestCommand
from .clean import CleanCommand
from .tag import TagCommand

logger = logging.getLogger(__name__)

# Export the registry
__all__ = ['Command', 'commands'] 