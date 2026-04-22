"""
Pytest configuration and fixtures for AI Office Pilot tests
"""

import os
import sys
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def mock_config(temp_dir):
    """Mock Config class with test directory"""
    from core.config import Config

    original_data_dir = Config.DATA_DIR
    original_memory_db = Config.MEMORY_DB

    Config.DATA_DIR = temp_dir
    Config.MEMORY_DB = temp_dir / "test_memory.db"
    Config.SALT_FILE = temp_dir / ".salt"
    Config.KEYSTORE_FILE = temp_dir / ".keystore"
    Config.PEPPER_FILE = temp_dir / ".pepper"
    Config.AUDIT_DIR = temp_dir / "logs" / "audit"
    Config.BACKUP_DIR = temp_dir / "backups"
    Config.TEMP_DIR = temp_dir / "temp"
    Config.REPORT_DIR = temp_dir / "reports"
    Config.PENDING_DIR = temp_dir / "pending"
    Config.ATTACHMENTS_DIR = temp_dir / "attachments"
    Config.LOCAL_SPREADSHEET = temp_dir / "expenses.xlsx"
    Config.ORGANIZED_ROOT = temp_dir / "organized"
    Config.CALENDAR_DIR = temp_dir / "calendar"
    Config.CALENDAR_PENDING_DIR = temp_dir / "calendar_pending"

    # Create directories
    for d in [
        Config.AUDIT_DIR,
        Config.BACKUP_DIR,
        Config.TEMP_DIR,
        Config.REPORT_DIR,
        Config.PENDING_DIR,
        Config.ATTACHMENTS_DIR,
        Config.ORGANIZED_ROOT,
        Config.CALENDAR_DIR,
        Config.CALENDAR_PENDING_DIR,
    ]:
        d.mkdir(parents=True, exist_ok=True)

    yield Config

    # Restore original
    Config.DATA_DIR = original_data_dir
    Config.MEMORY_DB = original_memory_db


@pytest.fixture
def mock_ollama():
    """Mock Ollama API responses"""
    with patch("modules.email_brain.reader") as mock:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response from Ollama"}
        yield mock_response


@pytest.fixture
def sample_email():
    """Sample email data"""
    return {
        "id": b"12345",
        "from": "John Doe <john@example.com>",
        "subject": "Test Email Subject",
        "body": "This is a test email body.\nWith multiple lines.",
        "date": "Sun, 22 Mar 2026 10:00:00 +0000",
        "has_attachments": False,
        "attachments": [],
        "message_id": "<test123@example.com>",
        "account": "Personal",
    }


@pytest.fixture
def sample_email_with_attachments(sample_email):
    """Sample email with attachments"""
    sample_email["has_attachments"] = True
    sample_email["attachments"] = [
        {"filename": "document.pdf", "size": 1024, "content_type": "application/pdf"}
    ]
    return sample_email


@pytest.fixture
def sample_meeting_email():
    """Sample meeting request email"""
    return {
        "id": b"67890",
        "from": "Jane Smith <jane@example.com>",
        "subject": "Meeting Request: Team Sync",
        "body": """
        Hi,

        I'd like to schedule a meeting to discuss the project.

        Please let me know if 2pm works for you.

        Best,
        Jane

        BEGIN:VCALENDAR
        VERSION:2.0
        BEGIN:VEVENT
        SUMMARY:Team Sync
        DTSTART:20260322T140000Z
        LOCATION:Conference Room A
        END:VEVENT
        END:VCALENDAR
        """,
        "date": "Sun, 22 Mar 2026 09:00:00 +0000",
        "has_attachments": False,
        "attachments": [],
        "message_id": "<meeting123@example.com>",
        "account": "Personal",
    }


@pytest.fixture
def sample_file_info():
    """Sample file info dict"""
    return {
        "path": "/test/Downloads/invoice.pdf",
        "name": "invoice.pdf",
        "extension": ".pdf",
        "size": 1024,
        "modified": "2026-03-22T10:00:00",
        "source_folder": "/test/Downloads",
    }


@pytest.fixture
def sample_contact():
    """Sample contact data"""
    return {
        "email": "john@example.com",
        "name": "John Doe",
        "greeting": "Hey John",
        "tone": "casual",
        "priority": "normal",
        "trusted": 0,
        "interaction_count": 5,
    }


@pytest.fixture
def mock_imap_connection():
    """Mock IMAP connection"""
    mock_conn = MagicMock()
    mock_conn.login = MagicMock()
    mock_conn.select = MagicMock()
    mock_conn.search = MagicMock(return_value=(b"OK", [b"1 2 3"]))
    mock_conn.fetch = MagicMock(return_value=(b"OK", [(b"1", b"raw email data")]))
    mock_conn.store = MagicMock(return_value=(b"OK", [b"1"]))
    mock_conn.logout = MagicMock()
    return mock_conn


@pytest.fixture
def mock_smtp_connection():
    """Mock SMTP connection"""
    mock_conn = MagicMock()
    mock_conn.starttls = MagicMock()
    mock_conn.login = MagicMock()
    mock_conn.send_message = MagicMock()
    mock_conn.quit = MagicMock()
    return mock_conn


@pytest.fixture
def mock_email_message(sample_email):
    """Mock email.message.Message"""
    from email import message_from_bytes

    raw_email = b"""From: john@example.com
Subject: Test Email Subject
Date: Sun, 22 Mar 2026 10:00:00 +0000
Message-ID: <test123@example.com>

This is a test email body.
With multiple lines.
"""
    return message_from_bytes(raw_email)


@pytest.fixture
def mock_encryption():
    """Mock encryption engine"""
    mock = MagicMock()
    mock.is_setup = True
    mock.is_unlocked = True
    mock.setup = MagicMock()
    mock.unlock = MagicMock()
    mock.lock = MagicMock()
    mock.encrypt = MagicMock(return_value="encrypted_data")
    mock.decrypt = MagicMock(return_value="decrypted_data")
    return mock


@pytest.fixture
def memory_engine(mock_config):
    """Create a fresh MemoryEngine for testing"""
    from learning.memory import MemoryEngine

    # Reset database
    if mock_config.MEMORY_DB.exists():
        mock_config.MEMORY_DB.unlink()

    engine = MemoryEngine()
    yield engine

    # Cleanup
    if mock_config.MEMORY_DB.exists():
        mock_config.MEMORY_DB.unlink()
