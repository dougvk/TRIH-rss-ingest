"""Test tagging functionality."""
import json
from datetime import datetime, timezone
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from src.models import Episode
from src.tagging.prompt import load_taxonomy, construct_prompt, validate_tags
from src.tagging.tagger import tag_episode, get_untagged_episodes
from src.tagging.processor import process_episodes

@pytest.fixture
def sample_taxonomy():
    """Create a sample taxonomy for testing."""
    return {
        "Format": ["Series Episodes", "Standalone Episodes", "RIHC Series"],
        "Theme": ["Ancient & Classical Civilizations", "Medieval & Renaissance Europe"],
        "Track": ["Roman Track", "Medieval & Renaissance Track"]
    }

@pytest.fixture
def sample_episode():
    """Create a sample episode for testing."""
    return Episode(
        guid="test-123",
        title="The Fall of Rome",
        description="A detailed look at the fall of the Roman Empire...",
        published_date=datetime(2024, 1, 1, tzinfo=timezone.utc)
    )

def test_load_taxonomy(tmp_path):
    """Test loading taxonomy from markdown file."""
    # Create a test markdown file
    taxonomy_file = tmp_path / "test_taxonomy.md"
    taxonomy_content = """## Format
- Series Episodes
- Standalone Episodes
- RIHC Series

## Theme
- Ancient & Classical Civilizations
- Medieval & Renaissance Europe
- Empire, Colonialism & Exploration
- Modern Political History & Leadership
- Military History & Battles
- Cultural, Social & Intellectual History
- Science, Technology & Economic History
- Religious, Ideological & Philosophical History
- Historical Mysteries, Conspiracies & Scandals
- Regional & National Histories

## Track
- Roman Track
- Medieval & Renaissance Track
- Colonialism & Exploration Track
- American History Track
- Military & Battles Track
- Modern Political History Track
- Cultural & Social History Track
- Science, Technology & Economic History Track
- Religious & Ideological History Track
- Historical Mysteries & Conspiracies Track
- British History Track
- Global Empires Track
- World Wars Track
- Ancient Civilizations Track
- Regional Spotlight: Latin America Track
- Regional Spotlight: Asia & the Middle East Track
- Regional Spotlight: Europe Track
- Regional Spotlight: Africa Track
- Historical Figures Track
- The RIHC Bonus Track
- Archive Editions Track
- Contemporary Issues Through History Track
"""
    taxonomy_file.write_text(taxonomy_content)
    
    # Load and verify taxonomy
    taxonomy = load_taxonomy(taxonomy_file)
    assert "Format" in taxonomy
    assert "Theme" in taxonomy
    assert "Track" in taxonomy
    assert taxonomy["Format"] == ["Series Episodes", "Standalone Episodes", "RIHC Series"]
    assert taxonomy["Theme"] == [
        "Ancient & Classical Civilizations",
        "Medieval & Renaissance Europe",
        "Empire, Colonialism & Exploration",
        "Modern Political History & Leadership",
        "Military History & Battles",
        "Cultural, Social & Intellectual History",
        "Science, Technology & Economic History",
        "Religious, Ideological & Philosophical History",
        "Historical Mysteries, Conspiracies & Scandals",
        "Regional & National Histories"
    ]
    assert taxonomy["Track"] == [
        "Roman Track",
        "Medieval & Renaissance Track",
        "Colonialism & Exploration Track",
        "American History Track",
        "Military & Battles Track",
        "Modern Political History Track",
        "Cultural & Social History Track",
        "Science, Technology & Economic History Track",
        "Religious & Ideological History Track",
        "Historical Mysteries & Conspiracies Track",
        "British History Track",
        "Global Empires Track",
        "World Wars Track",
        "Ancient Civilizations Track",
        "Regional Spotlight: Latin America Track",
        "Regional Spotlight: Asia & the Middle East Track",
        "Regional Spotlight: Europe Track",
        "Regional Spotlight: Africa Track",
        "Historical Figures Track",
        "The RIHC Bonus Track",
        "Archive Editions Track",
        "Contemporary Issues Through History Track"
    ]

def test_construct_prompt(sample_taxonomy, sample_episode):
    """Test prompt construction."""
    prompt = construct_prompt(
        sample_episode.title,
        sample_episode.description,
        sample_taxonomy
    )
    
    # Verify prompt contains key elements
    assert sample_episode.title in prompt
    assert sample_episode.description in prompt
    for category, tags in sample_taxonomy.items():
        assert category in prompt
        for tag in tags:
            assert tag in prompt
    assert "JSON format" in prompt

def test_validate_tags_valid(sample_taxonomy):
    """Test tag validation with valid tags."""
    tags = {
        "Format": ["Series Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": 1
    }
    assert validate_tags(tags, sample_taxonomy)

    # Test with null episode number
    tags_null = {
        "Format": ["Series Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": None
    }
    assert validate_tags(tags_null, sample_taxonomy)

def test_validate_tags_invalid(sample_taxonomy):
    """Test tag validation with invalid tags."""
    # Invalid category
    tags1 = {"InvalidCategory": ["Series Episodes"]}
    assert not validate_tags(tags1, sample_taxonomy)
    
    # Invalid tag
    tags2 = {"Format": ["InvalidTag"]}
    assert not validate_tags(tags2, sample_taxonomy)

    # Missing episode_number
    tags3 = {
        "Format": ["Series Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"]
    }
    assert not validate_tags(tags3, sample_taxonomy)

    # Invalid episode_number type
    tags4 = {
        "Format": ["Series Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": "1"  # String instead of int/None
    }
    assert not validate_tags(tags4, sample_taxonomy)

@pytest.mark.skip("OpenAI API calls are tested in integration tests")
def test_tag_episode(sample_taxonomy, sample_episode):
    """Test episode tagging with mocked OpenAI API."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps({
                    "Format": ["Standalone"],
                    "Theme": ["Ancient & Classical"],
                    "Region": ["Europe"]
                })
            )
        )
    ]
    
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test tagging
        tags = tag_episode(sample_episode, sample_taxonomy, dry_run=True)
        assert tags is None  # dry run should return None
        
        # Test actual tagging
        with patch('src.tagging.tagger.get_connection'):
            tags = tag_episode(sample_episode, sample_taxonomy)
            assert "Format" in tags
            assert "Theme" in tags
            assert "Region" in tags

def test_get_untagged_episodes():
    """Test retrieving untagged episodes."""
    mock_row = MagicMock()
    mock_row.__getitem__.side_effect = lambda x: {
        'guid': 'test-123',
        'title': 'Test Episode',
        'description': 'Test Description',
        'link': '',
        'published_date': datetime.now(timezone.utc),
        'duration': None,
        'audio_url': None,
        'cleaned_description': None
    }[x]
    
    with patch('src.tagging.tagger.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [mock_row]
        mock_conn.return_value.__enter__.return_value = mock_cursor
        
        episodes = get_untagged_episodes(limit=1)
        assert len(episodes) == 1
        assert episodes[0].guid == 'test-123'
        assert episodes[0].title == 'Test Episode'

def test_process_episodes(tmp_path, sample_taxonomy):
    """Test batch processing of episodes."""
    # Create test taxonomy file
    taxonomy_file = tmp_path / "test_taxonomy.md"
    taxonomy_content = """## Format
- Series Episodes
- Standalone Episodes
"""
    taxonomy_file.write_text(taxonomy_content)
    
    # Mock dependencies
    with patch('src.tagging.processor.get_untagged_episodes') as mock_get_episodes, \
         patch('src.tagging.processor.tag_episode') as mock_tag_episode:
        
        # Setup mocks
        mock_get_episodes.return_value = [
            Episode(
                guid=f"test-{i}",
                title=f"Test Episode {i}",
                description="Test Description",
                published_date=datetime.now(timezone.utc)
            )
            for i in range(2)
        ]
        mock_tag_episode.return_value = {"Format": ["Standalone"]}
        
        # Test processing
        results_file = tmp_path / "results.txt"
        process_episodes(
            taxonomy_path=taxonomy_file,
            batch_size=2,
            results_file=str(results_file)
        )
        
        # Verify results file was created
        assert results_file.exists()
        content = results_file.read_text()
        assert "Test Episode 0" in content
        assert "Test Episode 1" in content 