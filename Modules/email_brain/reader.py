"""
AI Office Pilot - Email Reader
IMAP email fetching
"""

import email
import imaplib
import logging
from email.header import decode_header
from email.message import Message
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass

from core.config import Config
from core.retry import retry_imap

logger = logging.getLogger(__name__)


@dataclass
class ProcessedEmail:
    """Processed email record"""
    msg_id: str
    sender: str
    sender_name: str
    subject: str
    classification: str
    timestamp: str


# Global storage for processed emails
_processed_emails: List[ProcessedEmail] = []


class EmailReader:
    """Read emails via IMAP - all processing LOCAL"""

    def __init__(self, account: dict) -> None:
        self.account = account
        self.conn: Optional[imaplib.IMAP4_SSL] = None

    @staticmethod
    def add_processed_email(
        msg_id: str,
        sender: str,
        sender_name: str,
        subject: str,
        classification: str
    ):
        """Track a processed email"""
        global _processed_emails
        email_record = ProcessedEmail(
            msg_id=msg_id,
            sender=sender,
            sender_name=sender_name,
            subject=subject[:50] + "..." if len(subject) > 50 else subject,
            classification=classification,
            timestamp=datetime.now().isoformat()
        )
        _processed_emails.insert(0, email_record)
        # Keep only last 50
        _processed_emails = _processed_emails[:50]

    @staticmethod
    def get_processed_emails(limit: int = 5) -> List[dict]:
        """Get recent processed emails"""
        global _processed_emails
        return [
            {
                "msg_id": e.msg_id,
                "sender": e.sender,
                "sender_name": e.sender_name,
                "subject": e.subject,
                "classification": e.classification,
                "timestamp": e.timestamp
            }
            for e in _processed_emails[:limit]
        ]

    @retry_imap(max_retries=3, base_delay=2.0)
    def connect(self) -> None:
        """Connect to IMAP server"""
        logger.info(f"Connecting to IMAP: {self.account['imap_host']}")
        self.conn = imaplib.IMAP4_SSL(self.account["imap_host"], self.account["imap_port"])
        self.conn.login(self.account["address"], self.account["password"])

    def fetch_unread(self, limit: Optional[int] = None) -> list[dict]:
        """Fetch unread emails"""
        if not self.conn:
            self.connect()

        fetch_limit = limit or Config.MAX_EMAILS_PER_CYCLE

        self.conn.select("INBOX")
        _, message_ids = self.conn.search(None, "UNSEEN")

        emails: list[dict] = []
        ids = message_ids[0].split()
        ids = ids[:fetch_limit]

        for mid in ids:
            try:
                _, msg_data = self.conn.fetch(mid, "(RFC822)")
                raw = msg_data[0][1]
                msg: Message = email.message_from_bytes(raw)
                parsed = self._parse_email(msg, mid)
                if parsed:
                    emails.append(parsed)
            except Exception as e:
                logger.warning(f"Failed to fetch email: {e}")
                continue

        return emails

    def _parse_email(self, msg: Message, mid: bytes) -> dict:
        """Parse email message into dict"""
        subject = ""
        raw_subject = msg.get("Subject", "")
        if raw_subject:
            decoded = decode_header(raw_subject)
            for part, enc in decoded:
                if isinstance(part, bytes):
                    subject += part.decode(enc or "utf-8", errors="replace")
                else:
                    subject += str(part)

        sender = msg.get("From", "")

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(errors="replace")
                    except Exception as e:
                        logger.warning(f"Failed to decode email body: {e}")
                    break
        else:
            try:
                body = msg.get_payload(decode=True).decode(errors="replace")
            except Exception as e:
                logger.warning(f"Failed to decode email payload: {e}")
                body = str(msg.get_payload())

        has_attachments = False
        attachments: list[dict] = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == "attachment":
                    has_attachments = True
                    filename = part.get_filename() or "unnamed"
                    attachments.append(
                        {
                            "filename": filename,
                            "size": len(part.get_payload(decode=True) or b""),
                            "content_type": part.get_content_type(),
                        }
                    )

        return {
            "id": mid,
            "from": sender,
            "subject": subject,
            "body": body,
            "date": msg.get("Date", ""),
            "has_attachments": has_attachments,
            "attachments": attachments,
            "message_id": msg.get("Message-ID", ""),
            "account": self.account["label"],
        }

    def download_attachment(self, email_id: bytes, filename: str) -> Optional[str]:
        """Download specific attachment"""
        if not self.conn:
            self.connect()

        _, msg_data = self.conn.fetch(email_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                part_filename = part.get_filename()
                if part_filename == filename:
                    data = part.get_payload(decode=True)
                    save_path = Config.ATTACHMENTS_DIR / filename
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    save_path.write_bytes(data)
                    return str(save_path)

        return None

    def mark_read(self, email_id: bytes) -> None:
        """Mark email as read"""
        if self.conn:
            self.conn.store(email_id, "+FLAGS", "\\Seen")

    def disconnect(self) -> None:
        """Close IMAP connection"""
        if self.conn:
            try:
                self.conn.logout()
            except imaplib.IMAP4.error:
                pass
            self.conn = None
