"""CLI utility functions for environment handling and logging."""
import os
import sys
import logging
from typing import Optional
from termcolor import colored

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_environment(env: Optional[str]) -> str:
    """Validate and normalize environment name.
    
    Args:
        env: Environment name from CLI args
        
    Returns:
        Normalized environment name
        
    Raises:
        ValueError: If environment is invalid
    """
    if not env:
        raise ValueError(
            "Environment (--env) is required.\n"
            "Use --env test for testing or --env prod for production."
        )
    
    env = env.lower().strip()
    if env not in {"test", "prod"}:
        raise ValueError(
            f"Invalid environment: {env}\n"
            "Must be either 'test' or 'prod'"
        )
    
    return env

def setup_environment(env: str) -> None:
    """Set up environment for CLI operation.
    
    Args:
        env: Validated environment name
    """
    os.environ["APP_ENV"] = env
    show_environment_banner(env)

def show_environment_banner(env: str) -> None:
    """Display a colored banner indicating the current environment.
    
    Args:
        env: Current environment name
    """
    color = "blue" if env == "test" else "red"
    env_text = colored(f" {env.upper()} ENVIRONMENT ", color, attrs=["reverse", "bold"])
    
    print("\n" + "=" * 80)
    print(f"Running in {env_text}")
    print("=" * 80 + "\n")

def confirm_production() -> bool:
    """Confirm before proceeding with production operation.
    
    Returns:
        True if confirmed, False otherwise
    """
    response = input(
        colored(
            "\nWARNING: You are about to modify production data.\n"
            "Are you sure you want to proceed? [y/N] ",
            "red",
            attrs=["bold"]
        )
    )
    return response.lower() == 'y' 