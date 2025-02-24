"""Integration tests for the RSS feed processor."""
from datetime import datetime, timezone
import pytest

from src.models import Episode
from src.cleaning import clean_episode
from src.tagging.tagger import tag_episode
from src.tagging.taxonomy import taxonomy
from src.storage import get_connection, store_episode

@pytest.fixture
def mock_episode():
    """Create a mock episode for testing."""
    return Episode(
        guid="test-123",
        title="Test Episode",
        description="This is a test episode about ancient Rome.",
        published_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        link="https://example.com/test",
        duration="3600",
        audio_url="https://example.com/test.mp3"
    )

def test_api_cleaning_integration(mock_episode):
    """Test cleaning content with live OpenAI API."""
    # Store the test episode using the storage module
    store_episode(mock_episode)
        
    # Clean the episode
    result = clean_episode(mock_episode.guid, dry_run=False)
    assert result is not None
    assert result.is_modified
    assert result.cleaned_description is not None

def test_api_tagging_integration(mock_episode):
    """Test tagging content with live OpenAI API."""
    # Tag the episode
    tags = tag_episode(mock_episode)

    assert tags is not None
    assert taxonomy.validate_tags(tags)
    assert "Format" in tags
    assert "Theme" in tags
    assert "Track" in tags
    assert "episode_number" in tags 