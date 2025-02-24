"""Tests for feed ingestion command."""
import os
import pytest
from pathlib import Path
from datetime import datetime, timezone

from src.cli.commands.ingest import IngestCommand
from src.cli.main import main

def test_ingest_command_validation(monkeypatch):
    """Test ingest command validation."""
    # Test with no URL configured
    monkeypatch.delenv("RSS_FEED_URL", raising=False)
    cmd = IngestCommand("test", dry_run=True)
    with pytest.raises(ValueError, match="RSS feed URL not configured"):
        cmd.validate()
    
    # Test with valid URL
    monkeypatch.setenv("RSS_FEED_URL", "tests/rss_feed.xml")
    cmd = IngestCommand("test", dry_run=True)
    assert cmd.validate()

def test_ingest_command_dry_run(monkeypatch):
    """Test ingest command in dry run mode."""
    monkeypatch.setenv("RSS_FEED_URL", "tests/rss_feed.xml")
    
    # Run command in dry run mode
    cmd = IngestCommand("test", dry_run=True)
    assert cmd.run()

def test_ingest_command_with_limit(monkeypatch):
    """Test ingest command with episode limit."""
    monkeypatch.setenv("RSS_FEED_URL", "tests/rss_feed.xml")
    
    # Run command with limit
    cmd = IngestCommand("test", limit=5)
    assert cmd.run()

def test_ingest_command_cli(monkeypatch):
    """Test ingest command through CLI interface."""
    monkeypatch.setenv("RSS_FEED_URL", "tests/rss_feed.xml")
    
    # Run through CLI
    result = main(["--env", "test", "ingest", "--limit", "5"])
    assert result == 0

def test_ingest_command_verification(monkeypatch):
    """Test ingest command verification."""
    monkeypatch.setenv("RSS_FEED_URL", "tests/rss_feed.xml")
    
    # Test successful verification
    cmd = IngestCommand("test")
    assert cmd.run() 