"""Test clean command."""
import pytest
from pathlib import Path

from src.cli.commands.clean import CleanCommand

def test_clean_command_validation():
    """Test clean command validation."""
    cmd = CleanCommand(
        env="test",
        dry_run=True,
        debug=True,
        guid="test-clean-123"
    )
    
    assert cmd.validate()
    assert not cmd.execute()  # Should fail gracefully
    assert not cmd.verify()

def test_clean_command_cli(test_db):
    """Test clean command through CLI interface."""
    # First get a real episode GUID from the database
    from src.storage import get_episodes
    episodes = get_episodes(limit=1)
    assert episodes, "No episodes found in test database"
    real_guid = episodes[0].guid

    from src.cli.main import main

    # Test with single episode
    result = main([
        "--env", "test",
        "clean",
        "--guid", real_guid
    ])
    assert result == 0

    # Test with limit
    result = main([
        "--env", "test",
        "clean",
        "--limit", "10"
    ])
    assert result == 0