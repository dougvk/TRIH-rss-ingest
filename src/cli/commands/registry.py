"""Command registry and registration decorator."""
from typing import Dict, Type, Callable
from .base import Command

# Registry of available commands
commands: Dict[str, Type[Command]] = {}

def register(name: str) -> Callable:
    """Decorator to register a command.
    
    Args:
        name: Name of the command
        
    Returns:
        Decorator function
    """
    def decorator(command_class: Type[Command]) -> Type[Command]:
        commands[name] = command_class
        return command_class
    return decorator 