"""Tests for validate command."""
import json
import pytest
from datetime import datetime, timezone

from src.cli.commands.validate import ValidateCommand
from src.storage import get_episode, store_episode
from src.models import Episode

def test_validate_command_validation(test_db):
    """Test validate command validation."""
    # Valid command
    cmd = ValidateCommand(
        env="test",
        dry_run=False,
        debug=False
    )
    assert cmd.validate()
    
    # Valid with guid
    cmd = ValidateCommand(
        env="test",
        guid="test-123"
    )
    assert cmd.validate()
    
    # Valid with limit
    cmd = ValidateCommand(
        env="test",
        limit=5
    )
    assert cmd.validate()

def test_validate_command_single_episode(test_db):
    """Test validating a single episode."""
    # Store test episode with valid tags
    episode = Episode(
        guid="test-validate-123",
        title="The Fall of Rome (Ep 1)",
        description="A detailed look at the fall of the Roman Empire",
        published_date=datetime.now(timezone.utc),
        tags=json.dumps({
            "Format": ["Series Episodes"],
            "Theme": ["Ancient & Classical Civilizations"],
            "Track": ["Roman Track"],
            "episode_number": 1
        })
    )
    store_episode(episode)
    
    # Validate episode
    cmd = ValidateCommand(
        env="test",
        guid=episode.guid
    )
    
    assert cmd.validate()
    assert cmd.execute()
    assert cmd.verify()

def test_validate_command_invalid_tags(test_db):
    """Test validating episode with invalid tags."""
    # Store test episode with invalid tags
    episode = Episode(
        guid="test-validate-456",
        title="The Fall of Rome (Ep 2)",
        description="More about the fall of the Roman Empire",
        published_date=datetime.now(timezone.utc),
        tags=json.dumps({
            "Format": ["Invalid Format"],
            "Theme": ["Invalid Theme"],
            "Track": ["Invalid Track"],
            "episode_number": "invalid"  # wrong type
        })
    )
    store_episode(episode)
    
    # Validate episode
    cmd = ValidateCommand(
        env="test",
        guid=episode.guid
    )
    
    assert cmd.validate()
    assert not cmd.execute()  # Should fail due to invalid tags
    assert not cmd.verify()

def test_validate_command_no_tags(test_db):
    """Test validating episode with no tags."""
    # Store test episode with no tags
    episode = Episode(
        guid="test-validate-789",
        title="The Fall of Rome (Ep 3)",
        description="Even more about the fall of the Roman Empire",
        published_date=datetime.now(timezone.utc)
    )
    store_episode(episode)
    
    # Validate episode
    cmd = ValidateCommand(
        env="test",
        guid=episode.guid
    )
    
    assert cmd.validate()
    assert cmd.execute()  # Should pass with warning
    assert cmd.verify()

def test_validate_command_batch(test_db):
    """Test validating multiple episodes."""
    # Store test episodes with valid tags
    episodes = [
        Episode(
            guid="test-batch-1",
            title="The Fall of Rome (Ep 1)",
            description="Part 1 of the series",
            published_date=datetime.now(timezone.utc),
            tags=json.dumps({
                "Format": ["Series Episodes"],
                "Theme": ["Ancient & Classical Civilizations"],
                "Track": ["Roman Track"],
                "episode_number": 1
            })
        ),
        Episode(
            guid="test-batch-2",
            title="The Fall of Rome (Ep 2)",
            description="Part 2 of the series",
            published_date=datetime.now(timezone.utc),
            tags=json.dumps({
                "Format": ["Series Episodes"],
                "Theme": ["Ancient & Classical Civilizations"],
                "Track": ["Roman Track"],
                "episode_number": 2
            })
        )
    ]
    
    for episode in episodes:
        store_episode(episode)
    
    # Validate episodes
    cmd = ValidateCommand(
        env="test",
        limit=2
    )
    
    assert cmd.validate()
    assert cmd.execute()
    assert cmd.verify()

def test_validate_command_dry_run(test_db):
    """Test validate command in dry run mode."""
    cmd = ValidateCommand(
        env="test",
        dry_run=True
    )
    
    assert cmd.validate()
    assert cmd.execute()
    assert cmd.verify()

def test_validate_command_invalid_guid(test_db):
    """Test validate command with invalid GUID."""
    cmd = ValidateCommand(
        env="test",
        guid="nonexistent-guid"
    )
    
    assert cmd.validate()
    assert not cmd.execute()  # Should fail gracefully
    assert not cmd.verify()

def test_validate_command_cli(test_db):
    """Test validate command through CLI interface."""
    from src.cli.main import main
    
    # Test with single episode
    result = main([
        "--env", "test",
        "validate",
        "--guid", "test-validate-123"
    ])
    assert result == 0
    
    # Test with limit
    result = main([
        "--env", "test",
        "validate",
        "--limit", "2"
    ])
    assert result == 0
    
    # Test dry run
    result = main([
        "--env", "test",
        "--dry-run",
        "validate"
    ])
    assert result == 0 