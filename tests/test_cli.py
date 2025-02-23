"""Test CLI functionality."""
import os
import json
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from argparse import ArgumentParser, Namespace
from datetime import datetime

from src.cli import main, setup_parser
from src.models import Episode

@pytest.fixture
def mock_feed_content():
    """Sample RSS feed content for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <title>Test Episode</title>
                <description>Test Description</description>
                <guid>test-123</guid>
                <pubDate>Mon, 01 Jan 2024 12:00:00 +0000</pubDate>
            </item>
        </channel>
    </rss>'''

@pytest.fixture
def mock_taxonomy(tmp_path):
    """Create a mock taxonomy file."""
    taxonomy_file = tmp_path / "test_taxonomy.md"
    taxonomy_content = """## Format
- Series Episodes
- Standalone Episodes

## Theme
- Ancient History
- Modern History

## Track
- History Track
"""
    taxonomy_file.write_text(taxonomy_content)
    return taxonomy_file

def test_setup_parser():
    """Test argument parser setup."""
    parser = setup_parser()
    
    # Test ingest command
    args = parser.parse_args(["--env", "test", "ingest", "--dry-run"])
    assert args.env == "test"
    assert args.command == "ingest"
    assert args.dry_run is True
    
    # Test clean command
    args = parser.parse_args(["clean", "--limit", "10", "--guid", "test-123"])
    assert args.command == "clean"
    assert args.limit == 10
    assert args.guid == "test-123"
    
    # Test tag command
    args = parser.parse_args(["tag", "--dry-run", "--limit", "5"])
    assert args.command == "tag"
    assert args.dry_run is True
    assert args.limit == 5
    
    # Test export command
    args = parser.parse_args(["export", "--output", "test.json"])
    assert args.command == "export"
    assert args.output == Path("test.json")

def test_ingest_command(mock_feed_content):
    """Test feed ingestion command."""
    with patch("src.cli.fetch_rss_feed") as mock_fetch, \
         patch("src.cli.store_episodes") as mock_store, \
         patch("src.cli.init_db") as mock_init:
        
        # Setup mocks
        mock_fetch.return_value = mock_feed_content
        
        # Test dry run
        assert main(["--env", "test", "ingest", "--dry-run"]) == 0
        mock_init.assert_not_called()
        mock_store.assert_not_called()
        
        # Test actual ingestion
        assert main(["--env", "test", "ingest"]) == 0
        mock_init.assert_called_once()
        mock_store.assert_called_once()

def test_clean_command():
    """Test content cleaning command."""
    with patch("src.cli.clean_episode") as mock_clean_single, \
         patch("src.cli.clean_episodes") as mock_clean_batch:
        
        # Setup mocks
        mock_result = MagicMock()
        mock_result.is_modified = True
        mock_clean_single.return_value = mock_result
        mock_clean_batch.return_value = [mock_result, mock_result]
        
        # Test single episode
        assert main(["--env", "test", "clean", "--guid", "test-123"]) == 0
        mock_clean_single.assert_called_once_with("test-123", False)
        
        # Test batch cleaning
        assert main(["--env", "test", "clean", "--limit", "2"]) == 0
        mock_clean_batch.assert_called_once_with(limit=2, dry_run=False)

def test_tag_command(mock_taxonomy):
    """Test episode tagging command."""
    with patch("src.cli.tag_episode") as mock_tag_single, \
         patch("src.cli.tag_episodes") as mock_tag_batch, \
         patch("src.storage.get_episode") as mock_get_episode:
        
        # Setup mocks
        mock_tag_single.return_value = {"Format": ["Series Episodes"]}
        mock_tag_batch.return_value = [{"Format": ["Series Episodes"]}]
        mock_get_episode.return_value = Episode(
            guid="test-123",
            title="Test Episode",
            description="Test Description",
            published_date=datetime(2024, 1, 1, 12, 0)
        )
        
        # Test single episode
        assert main([
            "--env", "test",
            "tag",
            "--guid", "test-123",
            "--taxonomy", str(mock_taxonomy)
        ]) == 0
        
        # Test batch tagging
        assert main([
            "--env", "test",
            "tag",
            "--limit", "2",
            "--taxonomy", str(mock_taxonomy)
        ]) == 0

def test_export_command(tmp_path):
    """Test data export command."""
    output_file = tmp_path / "export.json"
    
    with patch("src.storage.get_episodes") as mock_get:
        # Setup mock
        mock_get.return_value = [
            Episode(
                guid="test-123",
                title="Test Episode",
                description="Test Description",
                published_date=datetime(2024, 1, 1, 12, 0)
            )
        ]
        
        # Test export
        assert main([
            "--env", "test",
            "export",
            "--output", str(output_file)
        ]) == 0
        
        # Verify output
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert len(data) == 1
        assert data[0]["guid"] == "test-123"

def test_invalid_command():
    """Test invalid command handling."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--env", "test", "invalid"])
    assert exc_info.value.code == 2

def test_config_validation():
    """Test configuration validation."""
    with patch("src.cli.config.validate_config") as mock_validate:
        mock_validate.side_effect = ValueError("Test error")
        assert main(["--env", "test", "ingest"]) == 1 