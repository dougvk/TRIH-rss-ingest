"""Tests for tag command."""
import json
import pytest
from datetime import datetime, timezone

from src.cli.commands.tag import TagCommand
from src.storage import get_episode, store_episode, get_episodes
from src.models import Episode
from src.tagging.taxonomy import taxonomy

def test_tag_command_validation(test_db):
    """Test tag command validation."""
    # Valid command
    cmd = TagCommand(
        env="test",
        dry_run=False,
        debug=False
    )
    assert cmd.validate()
    
    # Valid with guid
    cmd = TagCommand(
        env="test",
        guid="test-123"
    )
    assert cmd.validate()
    
    # Valid with limit
    cmd = TagCommand(
        env="test",
        limit=5
    )
    assert cmd.validate()

def test_tag_command_single_episode(test_db):
    """Test tagging a single episode."""
    # Store test episode
    episode = Episode(
        guid="test-tag-123",
        title="The Fall of Rome (Ep 1)",
        description="A detailed look at the fall of the Roman Empire",
        published_date=datetime.now(timezone.utc)
    )
    store_episode(episode)
    
    # Tag episode
    cmd = TagCommand(
        env="test",
        guid=episode.guid
    )
    
    assert cmd.validate()
    assert cmd.execute()
    assert cmd.verify()
    
    # Check episode was tagged
    tagged = get_episode(episode.guid)
    assert tagged.tags is not None
    tags = json.loads(tagged.tags)
    assert taxonomy.validate_tags(tags)

def test_tag_command_batch(test_db):
    """Test tagging multiple episodes."""
    cmd = TagCommand(
        env="test",
        limit=2
    )
    
    assert cmd.validate()
    assert cmd.execute()
    assert cmd.verify()

def test_tag_command_dry_run(test_db):
    """Test tag command in dry run mode."""
    # Store test episode
    episode = Episode(
        guid="test-tag-456",
        title="The Fall of Rome (Ep 2)",
        description="More about the fall of the Roman Empire",
        published_date=datetime.now(timezone.utc)
    )
    store_episode(episode)
    
    # Tag in dry run mode
    cmd = TagCommand(
        env="test",
        guid=episode.guid,
        dry_run=True
    )
    
    assert cmd.validate()
    assert cmd.execute()
    assert cmd.verify()
    
    # Check episode was not actually tagged
    unchanged = get_episode(episode.guid)
    assert unchanged.tags is None

def test_tag_command_invalid_guid(test_db):
    """Test tag command with invalid GUID."""
    cmd = TagCommand(
        env="test",
        guid="nonexistent-guid"
    )
    
    assert cmd.validate()
    assert not cmd.execute()  # Should fail gracefully
    assert not cmd.verify()

def test_tag_command_cli(test_db):
    """Test tag command through CLI interface."""
    # First get a real episode GUID from the database
    episodes = get_episodes(limit=1)
    assert episodes, "No episodes found in test database"
    real_guid = episodes[0].guid

    from src.cli.main import main
    
    # Test with single episode
    result = main([
        "--env", "test",
        "tag",
        "--guid", real_guid
    ])
    assert result == 0
    
    # Test with limit
    result = main([
        "--env", "test",
        "tag",
        "--limit", "2"
    ])
    assert result == 0
    
    # Test dry run
    result = main([
        "--env", "test",
        "tag",
        "--dry-run",
        "--guid", real_guid
    ])
    assert result == 0 