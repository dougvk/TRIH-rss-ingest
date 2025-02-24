"""Test tagging functionality."""
import json
from datetime import datetime, timezone
import pytest
from unittest.mock import patch, MagicMock

from src.models import Episode
from src.tagging.prompt import construct_prompt
from src.tagging.tagger import tag_episode, get_untagged_episodes
from src.tagging.processor import process_episodes
from src.tagging.taxonomy import taxonomy
from src.tagging.taxonomy.schema import InvalidTagError, InvalidTagSetError

@pytest.fixture
def sample_episode():
    """Create a sample episode for testing."""
    return Episode(
        guid="test-123",
        title="The Fall of Rome",
        description="A detailed look at the fall of the Roman Empire, covering the political, economic, and social factors that led to its collapse. The episode explores key events from 235-285 AD during the Crisis of the Third Century, including the rapid succession of barracks emperors, economic collapse, and external pressures from Germanic tribes.",
        published_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        link="https://example.com/test",
        duration="3600",
        audio_url="https://example.com/test.mp3"
    )

def test_construct_prompt(sample_episode):
    """Test prompt construction."""
    prompt = construct_prompt(
        sample_episode.title,
        sample_episode.description
    )
    
    # Verify prompt contains key elements
    assert sample_episode.title in prompt
    assert sample_episode.description in prompt
    for category in taxonomy.categories:
        assert category in prompt
        for tag in taxonomy[category]:
            assert tag in prompt
    assert "JSON format" in prompt

def test_validate_tags_valid():
    """Test tag validation with valid tags."""
    tags = {
        "Format": ["Series Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": 1
    }
    assert taxonomy.validate_tags(tags)

    # Test with null episode number
    tags_null = {
        "Format": ["Series Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": None
    }
    assert taxonomy.validate_tags(tags_null)

def test_validate_tags_invalid():
    """Test tag validation with invalid tags."""
    # Invalid category
    tags1 = {"InvalidCategory": ["Series Episodes"]}
    with pytest.raises(InvalidTagSetError):
        taxonomy.validate_tags(tags1)

    # Invalid tag
    tags2 = {
        "Format": ["InvalidTag"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": None
    }
    with pytest.raises(InvalidTagError):
        taxonomy.validate_tags(tags2)

    # Missing episode_number is valid since it's optional
    tags3 = {
        "Format": ["Series Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"]
    }
    assert taxonomy.validate_tags(tags3) == True

    # Invalid episode_number type
    tags4 = {
        "Format": ["Series Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": "1"  # string instead of int
    }
    with pytest.raises(InvalidTagSetError):
        taxonomy.validate_tags(tags4)
    
    # Multiple format tags
    tags5 = {
        "Format": ["Series Episodes", "Standalone Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": None
    }
    with pytest.raises(InvalidTagSetError):
        taxonomy.validate_tags(tags5)
    
    # RIHC series without Series Episodes
    tags6 = {
        "Format": ["RIHC Series"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": None
    }
    with pytest.raises(InvalidTagSetError):
        taxonomy.validate_tags(tags6)

def test_tag_episode(sample_episode):
    """Test episode tagging with live OpenAI API."""
    # Test dry run
    tags = tag_episode(sample_episode, dry_run=True)
    assert tags is None  # dry run should return None
    
    # Test actual tagging
    tags = tag_episode(sample_episode)
    assert tags is not None
    assert taxonomy.validate_tags(tags)
    assert "Format" in tags
    assert "Theme" in tags
    assert "Track" in tags
    assert "episode_number" in tags
    
    # Verify tag values make sense for the episode
    assert any("Ancient" in tag for tag in tags["Theme"])
    assert any("Roman" in tag for tag in tags["Track"])

def test_get_untagged_episodes():
    """Test retrieving untagged episodes."""
    episodes = get_untagged_episodes(limit=1)
    assert isinstance(episodes, list)
    if len(episodes) > 0:
        assert isinstance(episodes[0], Episode)
        assert episodes[0].tags is None

def test_process_episodes():
    """Test batch processing of episodes."""
    # Process a small batch
    results = process_episodes(
        limit=2,
        dry_run=True
    )
    assert isinstance(results, list)
    
    # Test actual processing
    results = process_episodes(
        limit=2
    )
    assert isinstance(results, list)
    for tags in results:
        assert taxonomy.validate_tags(tags) 