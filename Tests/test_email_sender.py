"""Tests for EmailSender class"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


class TestEmailSender:
    """Test cases for EmailSender"""

    def test_init(self, mock_config):
        """Test EmailSender initialization"""
        from modules.email_brain.sender import EmailSender

        account = {"address": "test@example.com"}
        sender = EmailSender(account)

        assert sender.account == account
        assert sender.send_log.maxlen == 100

    def test_check_rate_limit_under(self, mock_config):
        """Test rate limit check when under limit"""
        from modules.email_brain.sender import EmailSender

        account = {"address": "test@example.com"}
        sender = EmailSender(account)

        # Add one recent send
        sender.send_log.append(datetime.now())

        assert sender._check_rate_limit() is True

    def test_check_rate_limit_at_limit(self, mock_config):
        """Test rate limit check when at limit"""
        from modules.email_brain.sender import EmailSender
        from core.config import Config

        account = {"address": "test@example.com"}
        sender = EmailSender(account)

        # Add max emails within the hour
        for _ in range(Config.MAX_EMAILS_PER_HOUR):
            sender.send_log.append(datetime.now())

        assert sender._check_rate_limit() is False

    def test_check_rate_limit_old_entries(self, mock_config):
        """Test rate limit ignores old entries"""
        from modules.email_brain.sender import EmailSender

        account = {"address": "test@example.com"}
        sender = EmailSender(account)

        # Add old entries (more than 1 hour ago)
        old_time = datetime.now() - timedelta(hours=2)
        for _ in range(50):
            sender.send_log.append(old_time)

        # Should still be under limit
        assert sender._check_rate_limit() is True

    @patch("modules.email_brain.sender.smtplib.SMTP")
    def test_send_reply_success(self, mock_smtp, mock_config):
        """Test successful email sending"""
        from modules.email_brain.sender import EmailSender

        mock_conn = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        account = {
            "address": "test@example.com",
            "password": "password",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
        }
        sender = EmailSender(account)

        result = sender.send_reply(
            to_address="recipient@example.com", subject="Test Subject", body="Test email body"
        )

        assert result is True
        mock_conn.starttls.assert_called_once()
        mock_conn.login.assert_called_once()
        mock_conn.send_message.assert_called_once()

    @patch("modules.email_brain.sender.smtplib.SMTP")
    def test_send_reply_adds_re_prefix(self, mock_smtp, mock_config):
        """Test that Re: prefix is added if not present"""
        from modules.email_brain.sender import EmailSender

        mock_conn = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        account = {
            "address": "test@example.com",
            "password": "password",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
        }
        sender = EmailSender(account)

        sender.send_reply(
            to_address="recipient@example.com", subject="Original Subject", body="Test body"
        )

        # Check that subject was prefixed with Re:
        call_args = mock_conn.send_message.call_args
        msg = call_args[0][0]
        assert msg["Subject"].startswith("Re:")

    @patch("modules.email_brain.sender.smtplib.SMTP")
    def test_send_reply_preserves_re_prefix(self, mock_smtp, mock_config):
        """Test that existing Re: prefix is preserved"""
        from modules.email_brain.sender import EmailSender

        mock_conn = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        account = {
            "address": "test@example.com",
            "password": "password",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
        }
        sender = EmailSender(account)

        sender.send_reply(
            to_address="recipient@example.com", subject="Re: Original Subject", body="Test body"
        )

        call_args = mock_conn.send_message.call_args
        msg = call_args[0][0]
        assert msg["Subject"] == "Re: Original Subject"

    @patch("modules.email_brain.sender.smtplib.SMTP")
    def test_send_reply_with_in_reply_to(self, mock_smtp, mock_config):
        """Test email with In-Reply-To header"""
        from modules.email_brain.sender import EmailSender

        mock_conn = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        account = {
            "address": "test@example.com",
            "password": "password",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
        }
        sender = EmailSender(account)

        in_reply_to = "<original-message-id@example.com>"
        sender.send_reply(
            to_address="recipient@example.com",
            subject="Test",
            body="Test body",
            in_reply_to=in_reply_to,
        )

        call_args = mock_conn.send_message.call_args
        msg = call_args[0][0]
        assert msg["In-Reply-To"] == in_reply_to
        assert msg["References"] == in_reply_to

    def test_send_reply_rate_limited(self, mock_config):
        """Test email sending when rate limited"""
        from modules.email_brain.sender import EmailSender
        from core.config import Config

        account = {"address": "test@example.com"}
        sender = EmailSender(account)

        # Fill up the rate limit
        for _ in range(Config.MAX_EMAILS_PER_HOUR):
            sender.send_log.append(datetime.now())

        with pytest.raises(RuntimeError) as exc_info:
            sender.send_reply(to_address="recipient@example.com", subject="Test", body="Test body")

        assert "Rate limit" in str(exc_info.value)

    @patch("modules.email_brain.sender.smtplib.SMTP")
    def test_send_reply_smtp_error(self, mock_smtp, mock_config):
        """Test handling of SMTP errors"""
        import smtplib
        from modules.email_brain.sender import EmailSender

        mock_smtp.return_value.__enter__ = MagicMock(
            side_effect=smtplib.SMTPException("Connection refused")
        )
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        account = {
            "address": "test@example.com",
            "password": "password",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
        }
        sender = EmailSender(account)

        with pytest.raises(RuntimeError) as exc_info:
            sender.send_reply(to_address="recipient@example.com", subject="Test", body="Test body")

        assert "Failed to send email" in str(exc_info.value)

    @patch("modules.email_brain.sender.smtplib.SMTP")
    def test_send_reply_delay(self, mock_smtp, mock_config):
        """Test that delay is applied after sending"""
        import time
        from modules.email_brain.sender import EmailSender
        from core.config import Config

        mock_conn = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        account = {
            "address": "test@example.com",
            "password": "password",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
        }
        sender = EmailSender(account)

        start = time.time()
        sender.send_reply(to_address="recipient@example.com", subject="Test", body="Test body")
        elapsed = time.time() - start

        # Should have delay (with some tolerance)
        assert elapsed >= Config.EMAIL_SEND_DELAY_SECONDS - 0.1
