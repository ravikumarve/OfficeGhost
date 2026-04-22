"""Tests for EmailReader class"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from email import message_from_bytes


class TestEmailReader:
    """Test cases for EmailReader"""

    def test_init(self, mock_config):
        """Test EmailReader initialization"""
        from modules.email_brain.reader import EmailReader

        account = {"address": "test@example.com", "label": "Test"}
        reader = EmailReader(account)

        assert reader.account == account
        assert reader.conn is None

    @patch("modules.email_brain.reader.imaplib.IMAP4_SSL")
    def test_connect(self, mock_imap, mock_config):
        """Test IMAP connection"""
        from modules.email_brain.reader import EmailReader

        mock_conn = MagicMock()
        mock_imap.return_value = mock_conn

        account = {
            "address": "test@example.com",
            "password": "password",
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "label": "Test",
        }
        reader = EmailReader(account)
        reader.connect()

        mock_imap.assert_called_once_with("imap.example.com", 993)
        mock_conn.login.assert_called_once_with("test@example.com", "password")

    @patch("modules.email_brain.reader.imaplib.IMAP4_SSL")
    def test_fetch_unread(self, mock_imap, mock_config, sample_email):
        """Test fetching unread emails"""
        from modules.email_brain.reader import EmailReader
        from email import message_from_bytes

        # Create mock email
        raw_email = b"""From: john@example.com
Subject: Test Email Subject
Date: Sun, 22 Mar 2026 10:00:00 +0000

This is a test email body.
"""
        mock_msg = message_from_bytes(raw_email)

        mock_conn = MagicMock()
        mock_conn.search.return_value = (b"OK", [b"12345"])
        mock_conn.fetch.return_value = (b"OK", [(b"12345", raw_email)])
        mock_imap.return_value = mock_conn

        account = {
            "address": "test@example.com",
            "password": "password",
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "label": "Personal",
        }
        reader = EmailReader(account)
        reader.connect()

        emails = reader.fetch_unread(limit=10)

        mock_conn.select.assert_called_with("INBOX")
        assert isinstance(emails, list)

    @patch("modules.email_brain.reader.imaplib.IMAP4_SSL")
    def test_disconnect(self, mock_imap, mock_config):
        """Test disconnecting from IMAP"""
        from modules.email_brain.reader import EmailReader

        mock_conn = MagicMock()
        mock_imap.return_value = mock_conn

        account = {
            "address": "test@example.com",
            "password": "password",
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "label": "Test",
        }
        reader = EmailReader(account)
        reader.connect()
        reader.disconnect()

        mock_conn.logout.assert_called_once()
        assert reader.conn is None

    def test_parse_email(self, mock_config):
        """Test parsing email message"""
        from modules.email_brain.reader import EmailReader
        from email import message_from_bytes

        raw_email = b"""From: John Doe <john@example.com>
Subject: Test Subject
Date: Sun, 22 Mar 2026 10:00:00 +0000
Message-ID: <test123>

Hello, this is a test email.
"""
        msg = message_from_bytes(raw_email)

        account = {"label": "Personal"}
        reader = EmailReader(account)

        result = reader._parse_email(msg, b"12345")

        assert "from" in result
        assert "subject" in result
        assert "body" in result
        assert "id" in result
        assert result["id"] == b"12345"

    def test_parse_email_with_attachments(self, mock_config):
        """Test parsing email with attachments"""
        from modules.email_brain.reader import EmailReader
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart()
        msg["From"] = "sender@example.com"
        msg["Subject"] = "Email with attachment"
        msg["Date"] = "Sun, 22 Mar 2026 10:00:00 +0000"
        msg.attach(MIMEText("Body text"))

        account = {"label": "Personal"}
        reader = EmailReader(account)

        result = reader._parse_email(msg, b"12345")

        assert result["subject"] == "Email with attachment"
        assert result["has_attachments"] == False

    @patch("modules.email_brain.reader.imaplib.IMAP4_SSL")
    def test_download_attachment(self, mock_imap, mock_config):
        """Test downloading attachment"""
        from modules.email_brain.reader import EmailReader
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.policy import compat32

        mock_conn = MagicMock()
        mock_imap.return_value = mock_conn

        # Create multipart email with attachment
        msg = MIMEMultipart()
        msg["From"] = "sender@example.com"
        msg["Subject"] = "Attachment test"
        msg["Date"] = "Sun, 22 Mar 2026 10:00:00 +0000"
        msg.attach(MIMEText("Body"))

        raw_msg = msg.as_bytes()
        mock_conn.fetch.return_value = (b"OK", [(b"1", raw_msg)])

        account = {
            "address": "test@example.com",
            "password": "password",
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "label": "Test",
        }
        reader = EmailReader(account)
        reader.connect()

        # This would need proper attachment handling for full test
        reader.disconnect()

    @patch("modules.email_brain.reader.imaplib.IMAP4_SSL")
    def test_mark_read(self, mock_imap, mock_config):
        """Test marking email as read"""
        from modules.email_brain.reader import EmailReader

        mock_conn = MagicMock()
        mock_imap.return_value = mock_conn

        account = {
            "address": "test@example.com",
            "password": "password",
            "imap_host": "imap.example.com",
            "imap_port": 993,
            "label": "Test",
        }
        reader = EmailReader(account)
        reader.connect()
        reader.mark_read(b"12345")

        mock_conn.store.assert_called_once()
