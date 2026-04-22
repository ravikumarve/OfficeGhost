"""Tests for FileAnalyzer class"""

import pytest
from pathlib import Path


class TestFileAnalyzer:
    """Test cases for FileAnalyzer"""

    def test_init(self, mock_config):
        """Test FileAnalyzer initialization"""
        from modules.file_commander.analyzer import FileAnalyzer

        analyzer = FileAnalyzer()

        assert analyzer.MAX_TEXT_LENGTH == 5000
        assert analyzer.MAX_PDF_PAGES == 10
        assert analyzer.IMAGE_EXTENSIONS == frozenset([".jpg", ".jpeg", ".png", ".gif", ".bmp"])

    def test_analyze_text_file(self, mock_config, temp_dir):
        """Test analyzing a text file"""
        from modules.file_commander.analyzer import FileAnalyzer

        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("This is test content for the analyzer.")

        analyzer = FileAnalyzer()
        file_info = {"path": str(test_file), "name": "test.txt", "extension": ".txt"}

        content = analyzer.analyze(file_info)

        assert "test content" in content.lower()

    def test_analyze_pdf_file_not_installed(self, mock_config, temp_dir):
        """Test analyzing PDF when PyPDF2 not installed"""
        from modules.file_commander.analyzer import FileAnalyzer

        # Create test file
        test_file = temp_dir / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake pdf content")

        analyzer = FileAnalyzer()
        file_info = {"path": str(test_file), "name": "test.pdf", "extension": ".pdf"}

        # When PyPDF2 is not available, returns fallback message
        content = analyzer.analyze(file_info)
        # Should not raise exception

    def test_analyze_image_file(self, mock_config, temp_dir):
        """Test analyzing an image file"""
        from modules.file_commander.analyzer import FileAnalyzer

        # Create test file (fake image)
        test_file = temp_dir / "test.jpg"
        test_file.write_bytes(b"fake image data")

        analyzer = FileAnalyzer()
        file_info = {"path": str(test_file), "name": "test.jpg", "extension": ".jpg"}

        content = analyzer.analyze(file_info)

        assert "Image file" in content
        assert "test.jpg" in content

    def test_analyze_unknown_extension(self, mock_config, temp_dir):
        """Test analyzing file with unknown extension"""
        from modules.file_commander.analyzer import FileAnalyzer

        test_file = temp_dir / "test.xyz"
        test_file.write_text("fallback content")

        analyzer = FileAnalyzer()
        file_info = {"path": str(test_file), "name": "test.xyz", "extension": ".xyz"}

        # Falls back to text reading
        content = analyzer.analyze(file_info)
        assert "fallback content" in content

    def test_analyze_handles_read_error(self, mock_config, temp_dir):
        """Test handling of read errors"""
        from modules.file_commander.analyzer import FileAnalyzer

        analyzer = FileAnalyzer()
        file_info = {"path": "/nonexistent/file.txt", "name": "file.txt", "extension": ".txt"}

        content = analyzer.analyze(file_info)

        # Should return error message, not raise
        assert "Could not read" in content or content == ""

    def test_constants_defined(self, mock_config):
        """Test that constants are properly defined"""
        from modules.file_commander.analyzer import FileAnalyzer

        assert hasattr(FileAnalyzer, "MAX_TEXT_LENGTH")
        assert hasattr(FileAnalyzer, "MAX_PDF_PAGES")
        assert hasattr(FileAnalyzer, "MAX_EXCEL_SHEETS")
        assert hasattr(FileAnalyzer, "MAX_EXCEL_ROWS")
        assert hasattr(FileAnalyzer, "IMAGE_EXTENSIONS")
        assert hasattr(FileAnalyzer, "TEXT_EXTENSIONS")
        assert hasattr(FileAnalyzer, "EXCEL_EXTENSIONS")
