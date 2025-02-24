"""Tests for base command functionality."""
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
import pytest
from concurrent.futures import ThreadPoolExecutor

from src.cli.commands.base import Command

class TestCommand(Command):
    """Test command implementation."""
    def validate(self) -> bool:
        return super().validate()
        
    def execute(self) -> bool:
        self.logger.info("Test execution")
        return True
        
    def verify(self) -> bool:
        return True

@pytest.fixture
def test_command(request):
    """Fixture to create a TestCommand instance."""
    cmd = TestCommand(
        env="test",
        dry_run=False,
        debug=False,
        setup_logs=False
    )
    cmd.guid = getattr(request, "param", None)  # Allow parameterizing the GUID
    return cmd

@pytest.fixture(autouse=True)
def cleanup_logs():
    """Clean up test logs after each test."""
    yield
    # Clean up log files
    log_dir = Path("data/logs/test")
    if log_dir.exists():
        shutil.rmtree(log_dir)
    # Clean up handlers
    for logger in logging.root.manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
    # Reset root logger level
    logging.getLogger().setLevel(logging.WARNING)

def test_command_logging(test_command):
    """Test operation-specific logging setup."""
    # Run the command
    test_command.run()

    # Check log directory creation
    log_dir = Path("data/logs/test/testcommand")
    assert log_dir.exists()
    assert log_dir.is_dir()
    
    # Check log file creation
    log_files = list(log_dir.glob("*.log"))
    assert len(log_files) == 1
    log_file = log_files[0]
    
    # Debug info
    print(f"\nLog file: {log_file}")
    print(f"File exists: {log_file.exists()}")
    print(f"File size: {log_file.stat().st_size}")
    print(f"File permissions: {oct(log_file.stat().st_mode)}")
    print(f"Current handlers: {logging.getLogger().handlers}")
    
    # Check log file naming
    timestamp = datetime.now().strftime("%Y%m%d")
    assert timestamp in log_file.name
    assert "batch" in log_file.name  # Default operation name
    
    # Check log content
    content = log_file.read_text()
    print(f"Log content: {content}")
    assert "Started TestCommand operation" in content
    assert "Test execution" in content

@pytest.mark.parametrize("test_command", ["test-123"], indirect=True)
def test_command_logging_with_guid(test_command):
    """Test logging with GUID."""
    test_command.run()
    
    log_dir = Path("data/logs/test/testcommand")
    log_files = list(log_dir.glob("*test-123.log"))
    assert len(log_files) == 1
    assert "test-123" in log_files[0].name

def test_dry_run_logging():
    """Test logging in dry run mode."""
    cmd = TestCommand("test", dry_run=True, debug=False)
    cmd.run()
    
    log_dir = Path("data/logs/test/testcommand")
    log_files = list(log_dir.glob("*.log"))
    assert len(log_files) == 1
    
    content = log_files[0].read_text()
    assert "DRY RUN MODE - No changes will be made" in content

def test_debug_logging():
    """Test logging in debug mode."""
    cmd = TestCommand("test", debug=True)
    
    # Check that root logger is set to DEBUG
    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG

def test_logging_permissions(tmp_path):
    """Test logging with restricted permissions."""
    # Create test directory with no write permissions
    test_dir = tmp_path / "data" / "logs" / "test"
    test_dir.mkdir(parents=True)
    test_dir.chmod(0o444)  # Read-only
    
    # Monkeypatch the data directory
    os.environ["DATA_DIR"] = str(tmp_path / "data")
    
    # Attempt to create command with restricted log directory
    with pytest.raises(PermissionError):
        cmd = TestCommand("test", dry_run=False)
        cmd.setup_logging()

def test_concurrent_logging():
    """Test logging from multiple commands."""
    # Clean up any existing log files
    log_dir = Path("data/logs/test/testcommand")
    if log_dir.exists():
        shutil.rmtree(log_dir)
    log_dir.parent.mkdir(parents=True, exist_ok=True)

    def run_command(i: int):
        cmd = TestCommand("test", dry_run=False)
        cmd.guid = f"test-{i}"
        print(f"\nCommand {i} GUID: {cmd.guid}")  # Debug print
        cmd.run()
        return cmd

    # Run multiple commands concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        commands = list(executor.map(run_command, range(3)))

    # Debug print all log files
    print("\nLog files found:")
    for f in log_dir.glob("*.log"):
        print(f"  {f.name}")

    # Check that each command has its own log file
    log_files = list(log_dir.glob("*.log"))
    assert len(log_files) == 3, f"Expected 3 log files, got {len(log_files)}: {[f.name for f in log_files]}"

    # Verify each log file contains the correct GUID
    for i in range(3):
        guid_files = list(log_dir.glob(f"*test-{i}.log"))
        assert len(guid_files) == 1, f"Expected 1 log file for GUID test-{i}, got {len(guid_files)}"
        log_content = guid_files[0].read_text()
        assert f"test-{i}" in log_content, f"Log file {guid_files[0]} does not contain GUID test-{i}"
        assert "Started TestCommand operation" in log_content
        assert "Test execution" in log_content 