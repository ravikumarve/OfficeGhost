"""
AI Office Pilot - Email Sender
SMTP with rate limiting
"""

import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from collections import deque
from typing import Optional

from core.config import Config
from core.retry import retry_smtp

logger = logging.getLogger(__name__)


class EmailSender:
    """Send emails via SMTP with rate limiting"""

    def __init__(self, account: dict) -> None:
        self.account = account
        self.send_log: deque[datetime] = deque(maxlen=100)

    @retry_smtp(max_retries=3, base_delay=2.0)
    def send_reply(
        self, to_address: str, subject: str, body: str, in_reply_to: Optional[str] = None
    ) -> bool:
        """Send email reply"""
        if not self._check_rate_limit():
            raise RuntimeError(
                f"Rate limit reached ({Config.MAX_EMAILS_PER_HOUR}/hour). Try again later."
            )

        msg = MIMEMultipart()
        msg["From"] = self.account["address"]
        msg["To"] = to_address
        msg["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject

        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = in_reply_to

        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.account["smtp_host"], self.account["smtp_port"]) as server:
                server.starttls()
                server.login(self.account["address"], self.account["password"])
                server.send_message(msg)

            self.send_log.append(datetime.now())
            time.sleep(Config.EMAIL_SEND_DELAY_SECONDS)

            return True

        except smtplib.SMTPException as e:
            raise RuntimeError(f"Failed to send email: {e}")

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent = sum(1 for t in self.send_log if t > one_hour_ago)
        return recent < Config.MAX_EMAILS_PER_HOUR
