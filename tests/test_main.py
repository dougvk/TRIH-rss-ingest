"""Test main orchestration functionality."""
from datetime import datetime, timezone
import pytest
from unittest.mock import patch, MagicMock

from src.main import process_feed, store_feed_data, main
from src.models import Episode

@pytest.fixture
def sample_episodes():
    """Create sample episodes for testing."""
    return [
        Episode(
            guid=f"test-{i}",
            title=f"Test Episode {i}",
            description=f"Test Description {i}",
            link=f"https://example.com/test-{i}",
            published_date=datetime(2024, 1, i+1, 12, 0, tzinfo=timezone.utc),
            duration=f"{30+i}:00",
            audio_url=f"https://example.com/test-{i}.mp3"
        )
        for i in range(3)
    ]

def test_process_feed(sample_episodes):
    """Test feed processing with mocked dependencies."""
    with patch('src.main.fetch_rss_feed') as mock_fetch, \
         patch('src.main.parse_rss_feed') as mock_parse:
        
        # Setup mocks
        mock_fetch.return_value = "<rss>test content</rss>"
        mock_parse.return_value = sample_episodes
        
        # Process feed
        result = process_feed()
        
        # Verify mocks were called
        mock_fetch.assert_called_once()
        mock_parse.assert_called_once_with("<rss>test content</rss>")
        
        # Verify result
        assert result == sample_episodes
        assert len(result) == 3

def test_store_feed_data(sample_episodes):
    """Test episode storage with mocked dependencies."""
    with patch('src.main.store_episodes') as mock_store:
        # Store episodes
        store_feed_data(sample_episodes)
        
        # Verify mock was called with correct data
        mock_store.assert_called_once_with(sample_episodes)

def test_main_success(sample_episodes):
    """Test successful execution of main function."""
    with patch('src.main.config.validate_config') as mock_validate, \
         patch('src.main.init_db') as mock_init_db, \
         patch('src.main.process_feed') as mock_process, \
         patch('src.main.store_feed_data') as mock_store, \
         patch('src.main.get_episodes') as mock_get:
        
        # Setup mocks
        mock_process.return_value = sample_episodes
        mock_get.return_value = sample_episodes[:5]  # Return first 5 episodes
        
        # Run main function
        main()
        
        # Verify all steps were executed
        mock_validate.assert_called_once()
        mock_init_db.assert_called_once()
        mock_process.assert_called_once()
        mock_store.assert_called_once_with(sample_episodes)
        mock_get.assert_called_once_with(limit=5)

def test_main_config_error():
    """Test main function handles configuration error."""
    with patch('src.main.config.validate_config') as mock_validate, \
         pytest.raises(ValueError):
        
        # Setup mock to raise error
        mock_validate.side_effect = ValueError("Missing RSS_FEED_URL")
        
        # Run main function - should raise the error
        main()

def test_main_process_error():
    """Test main function handles processing error."""
    with patch('src.main.config.validate_config'), \
         patch('src.main.init_db'), \
         patch('src.main.process_feed') as mock_process, \
         pytest.raises(Exception):
        
        # Setup mock to raise error
        mock_process.side_effect = Exception("Network error")
        
        # Run main function - should raise the error
        main()

def test_main_storage_error(sample_episodes):
    """Test main function handles storage error."""
    with patch('src.main.config.validate_config'), \
         patch('src.main.init_db'), \
         patch('src.main.process_feed') as mock_process, \
         patch('src.main.store_feed_data') as mock_store, \
         pytest.raises(Exception):
        
        # Setup mocks
        mock_process.return_value = sample_episodes
        mock_store.side_effect = Exception("Database error")
        
        # Run main function - should raise the error
        main() 