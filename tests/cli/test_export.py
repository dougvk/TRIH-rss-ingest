"""Tests for export command."""
import json
import csv
from pathlib import Path
import pytest

from src.cli.commands.export import ExportCommand

def test_export_command_validation(test_db, tmp_path):
    """Test export command validation."""
    # Valid command
    cmd = ExportCommand(
        env="test",
        output=tmp_path / "output.json",
        format="json",
        fields=["guid", "title"],
        dry_run=False,
        debug=False
    )
    assert cmd.validate()

    # Invalid format
    with pytest.raises(ValueError, match="Invalid format"):
        cmd = ExportCommand(
            env="test",
            output=tmp_path / "output.xyz",
            format="xyz"
        )
        cmd.validate()

    # Invalid fields
    with pytest.raises(ValueError, match="Invalid fields"):
        cmd = ExportCommand(
            env="test",
            output=tmp_path / "output.json",
            fields=["invalid_field"]
        )
        cmd.validate()

    # Non-existent output directory
    with pytest.raises(ValueError, match="Output directory does not exist"):
        cmd = ExportCommand(
            env="test",
            output=tmp_path / "nonexistent" / "output.json"
        )
        cmd.validate()

def test_export_command_json(test_db, tmp_path):
    """Test export command with JSON output."""
    output_file = tmp_path / "output.json"
    cmd = ExportCommand(
        env="test",
        output=output_file,
        format="json",
        fields=["guid", "title", "tags"],
        dry_run=False
    )
    
    assert cmd.validate()
    assert cmd.execute()
    assert cmd.verify()
    
    # Check output file
    assert output_file.exists()
    assert output_file.stat().st_size > 0
    
    # Validate JSON content
    with open(output_file) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) > 0  # Should have real episodes
    
    # Check fields
    for item in data:
        assert set(item.keys()) == {"guid", "title", "tags"}
        assert isinstance(item["guid"], str)
        assert isinstance(item["title"], str)
        assert isinstance(item["tags"], (dict, type(None)))

def test_export_command_csv(test_db, tmp_path):
    """Test export command with CSV output."""
    output_file = tmp_path / "output.csv"
    cmd = ExportCommand(
        env="test",
        output=output_file,
        format="csv",
        fields=["guid", "title", "published_date"],
        dry_run=False
    )
    
    assert cmd.validate()
    assert cmd.execute()
    assert cmd.verify()
    
    # Check output file
    assert output_file.exists()
    assert output_file.stat().st_size > 0
    
    # Validate CSV content
    with open(output_file, newline="") as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    assert len(data) > 0  # Should have real episodes
    
    # Check fields
    for row in data:
        assert set(row.keys()) == {"guid", "title", "published_date"}
        assert row["guid"]
        assert row["title"]
        assert row["published_date"]

def test_export_command_dry_run(test_db, tmp_path):
    """Test export command in dry run mode."""
    output_file = tmp_path / "output.json"
    cmd = ExportCommand(
        env="test",
        output=output_file,
        dry_run=True
    )
    
    assert cmd.validate()
    assert cmd.execute()
    assert cmd.verify()
    
    # File should not be created in dry run mode
    assert not output_file.exists()

def test_export_command_cli(test_db, tmp_path):
    """Test export command via CLI."""
    from src.cli.main import main
    
    output_file = tmp_path / "output.json"
    args = [
        "--env", "test",
        "export",
        "--output", str(output_file),
        "--format", "json",
        "--fields", "guid", "title"
    ]
    
    assert main(args) == 0
    assert output_file.exists()
    assert output_file.stat().st_size > 0 