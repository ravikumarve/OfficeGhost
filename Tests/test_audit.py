"""Tests for AuditLogger class"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestAuditLogger:
    """Test cases for AuditLogger"""

    def test_init(self, mock_config):
        """Test AuditLogger initialization"""
        from security.audit import AuditLogger

        logger = AuditLogger()

        assert logger.previous_hash == "genesis"

    def test_log_creates_entry(self, mock_config):
        """Test that log creates an entry"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        entry = logger.log("TEST_ACTION", "test", "Test description")

        assert entry is not None
        assert entry["action"] == "TEST_ACTION"
        assert entry["category"] == "test"
        assert entry["detail"] == "Test description"
        assert "hash" in entry
        assert "timestamp" in entry

    def test_log_hash_chain(self, mock_config):
        """Test that hash chain is maintained"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        entry1 = logger.log("ACTION1", "test", "First")
        entry2 = logger.log("ACTION2", "test", "Second")

        assert entry1["hash"] != entry2["hash"]
        assert entry2["previous_hash"] == entry1["hash"]

    def test_log_email(self, mock_config):
        """Test email logging shortcut"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        entry = logger.log_email("sender@example.com", "Test Subject", "read")

        assert "EMAIL_READ" in entry["action"]
        assert entry["category"] == "email"
        assert entry["sensitivity"] == "sensitive"

    def test_log_file(self, mock_config):
        """Test file logging shortcut"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        entry = logger.log_file("/path/to/file.txt", "process")

        assert "FILE_PROCESS" in entry["action"]
        assert entry["category"] == "file"

    def test_log_data(self, mock_config):
        """Test data logging shortcut"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        entry = logger.log_data("invoice.pdf", ["amount", "date"], "sheet.xlsx")

        assert entry["action"] == "DATA_EXTRACTED"
        assert entry["category"] == "data"
        assert entry["sensitivity"] == "sensitive"

    def test_log_ai(self, mock_config):
        """Test AI decision logging shortcut"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        entry = logger.log_ai("email_classify", "SPAM", 95, "phi3:mini")

        assert entry["action"] == "AI_DECISION"
        assert entry["category"] == "ai"

    def test_verify_integrity_empty(self, mock_config):
        """Test verification with no entries"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        result = logger.verify_integrity()

        assert result["verified"] is True
        assert result["status"] == "empty"

    def test_verify_integrity_valid(self, mock_config):
        """Test verification with valid chain"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        logger.log("ACTION1", "test", "First")
        logger.log("ACTION2", "test", "Second")

        result = logger.verify_integrity()

        assert result["verified"] is True
        assert result["status"] == "verified"

    def test_verify_integrity_tampered(self, mock_config):
        """Test verification with tampered chain"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        logger.log("ACTION1", "test", "First")
        logger.log("ACTION2", "test", "Second")

        # Tamper with an entry
        entries = logger._read_all()
        if entries:
            entries[0]["detail"] = "TAMPERED"
            log_file = logger._get_log_file()
            log_file.write_text("\n".join(json.dumps(e) for e in entries))

        result = logger.verify_integrity()

        assert result["verified"] is False
        assert result["status"] == "TAMPERED"

    def test_get_recent(self, mock_config):
        """Test getting recent entries"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        for i in range(10):
            logger.log(f"ACTION{i}", "test", f"Entry {i}")

        recent = logger.get_recent(5)

        assert len(recent) <= 5

    def test_export_report(self, mock_config):
        """Test report export"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        logger.log("ACTION1", "test", "First")
        logger.log("ACTION2", "email", "Second")

        report_path = logger.export_report()

        assert Path(report_path).exists()

        report = json.loads(Path(report_path).read_text())
        assert "summary" in report
        assert "entries" in report
        assert report["total_entries"] >= 2

    def test_export_report_with_date_filter(self, mock_config):
        """Test report export with date filtering"""
        from security.audit import AuditLogger

        logger = AuditLogger()
        logger.log("ACTION1", "test", "First")

        # Note: This tests the filtering mechanism
        # Actual date filtering depends on entries in the log
        report_path = logger.export_report(
            start_date="2026-01-01T00:00:00", end_date="2026-12-31T23:59:59"
        )

        assert Path(report_path).exists()
