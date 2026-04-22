"""Tests for FileSorter class"""

import pytest
from pathlib import Path
from unittest.mock import patch


class TestFileSorter:
    """Test cases for FileSorter"""

    def test_init(self, mock_config):
        """Test FileSorter initialization"""
        from modules.file_commander.sorter import FileSorter

        sorter = FileSorter()
        assert sorter is not None

    def test_get_destination(self, mock_config, temp_dir):
        """Test getting destination folder for a category"""
        from modules.file_commander.sorter import FileSorter

        organized_root = temp_dir / "organized"
        with patch.object(mock_config, "ORGANIZED_ROOT", str(organized_root)):
            sorter = FileSorter()
            dest = sorter.get_destination("invoice")

            assert "Finance" in dest
            assert "Invoices" in dest

    def test_get_destination_creates_folder(self, mock_config, temp_dir):
        """Test that destination folder is created"""
        from modules.file_commander.sorter import FileSorter

        organized_root = temp_dir / "organized"
        with patch.object(mock_config, "ORGANIZED_ROOT", str(organized_root)):
            sorter = FileSorter()
            dest = sorter.get_destination("receipt")

            assert Path(dest).exists()

    def test_get_destination_unknown_category(self, mock_config, temp_dir):
        """Test destination for unknown category"""
        from modules.file_commander.sorter import FileSorter

        organized_root = temp_dir / "organized"
        with patch.object(mock_config, "ORGANIZED_ROOT", str(organized_root)):
            sorter = FileSorter()
            dest = sorter.get_destination("unknown_category")

            assert "Other" in dest

    def test_move_file(self, mock_config, temp_dir):
        """Test moving a file"""
        from modules.file_commander.sorter import FileSorter

        organized_root = temp_dir / "organized"
        with patch.object(mock_config, "ORGANIZED_ROOT", str(organized_root)):
            sorter = FileSorter()

            # Create source file
            source = temp_dir / "source.txt"
            source.write_text("test content")

            # Get destination
            dest_folder = sorter.get_destination("report")

            # Move file
            new_path = sorter.move_file(str(source), dest_folder)

            assert Path(new_path).exists()
            assert not source.exists()

    def test_move_file_with_rename(self, mock_config, temp_dir):
        """Test moving a file with new name"""
        from modules.file_commander.sorter import FileSorter

        organized_root = temp_dir / "organized"
        with patch.object(mock_config, "ORGANIZED_ROOT", str(organized_root)):
            sorter = FileSorter()

            source = temp_dir / "source.txt"
            source.write_text("test content")

            dest_folder = sorter.get_destination("report")

            new_path = sorter.move_file(str(source), dest_folder, "renamed_file.txt")

            assert Path(new_path).name == "renamed_file.txt"

    def test_move_file_handles_duplicates(self, mock_config, temp_dir):
        """Test handling of duplicate filenames"""
        from modules.file_commander.sorter import FileSorter

        organized_root = temp_dir / "organized"
        with patch.object(mock_config, "ORGANIZED_ROOT", str(organized_root)):
            sorter = FileSorter()

            # Create source and destination
            source = temp_dir / "file.txt"
            source.write_text("test content")

            dest_folder = sorter.get_destination("report")
            Path(dest_folder).mkdir(parents=True, exist_ok=True)
            (Path(dest_folder) / "file.txt").write_text("existing")

            # Move - should add counter
            new_path = sorter.move_file(str(source), dest_folder)

            assert Path(new_path).name.startswith("file_")
            assert "_1" in Path(new_path).name or "_2" in Path(new_path).name

    def test_rename_file(self, mock_config, temp_dir):
        """Test renaming a file in place"""
        from modules.file_commander.sorter import FileSorter

        sorter = FileSorter()

        # Create test file
        original = temp_dir / "original.txt"
        original.write_text("content")

        new_path = sorter.rename_file(str(original), "renamed.txt")

        assert Path(new_path).name == "renamed.txt"
        assert not original.exists()

    def test_move_file_creates_destination(self, mock_config, temp_dir):
        """Test that destination directory is created if missing"""
        from modules.file_commander.sorter import FileSorter

        sorter = FileSorter()

        source = temp_dir / "source.txt"
        source.write_text("content")

        new_dest = temp_dir / "new" / "nested" / "folder"

        new_path = sorter.move_file(str(source), str(new_dest))

        assert Path(new_path).exists()
        assert Path(new_dest).exists()
