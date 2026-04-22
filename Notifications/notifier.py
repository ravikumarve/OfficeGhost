"""
AI Office Pilot - Desktop Notifications
"""

import time
from datetime import datetime, timedelta
from collections import deque
from typing import Optional

from core.config import Config


class Notifier:
    """Cross-platform desktop notifications with throttling"""

    NORMAL_TIMEOUT = 10
    URGENT_TIMEOUT = 30
    THROTTLE_WINDOW_SECONDS = 60
    MAX_NOTIFICATIONS_PER_WINDOW = 10

    def __init__(self) -> None:
        self.enabled = Config.ENABLE_NOTIFICATIONS
        self.sound_enabled = Config.ENABLE_SOUND
        self._notification_history: deque[datetime] = deque(maxlen=100)

    def notify(
        self, title: str, message: str, urgency: str = "normal", icon: Optional[str] = None
    ) -> None:
        """Send desktop notification with throttling"""
        if not self.enabled:
            return

        if not self._check_throttle():
            return

        self._notification_history.append(datetime.now())

        try:
            from plyer import notification

            notification.notify(
                title=f"AI Office Pilot: {title}",
                message=message,
                app_name="AI Office Pilot",
                timeout=self.URGENT_TIMEOUT if urgency == "urgent" else self.NORMAL_TIMEOUT,
            )
        except Exception:
            fallback_icon = icon or ("🔴" if urgency == "urgent" else "🔔")
            print(f"\n{fallback_icon} {title}: {message}")

        if self.sound_enabled and urgency == "urgent":
            self._play_notification_sound()

    def _check_throttle(self) -> bool:
        """Check if we should throttle notifications"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.THROTTLE_WINDOW_SECONDS)
        recent_count = sum(1 for dt in self._notification_history if dt > cutoff)
        return recent_count < self.MAX_NOTIFICATIONS_PER_WINDOW

    def _play_notification_sound(self) -> None:
        """Play notification sound (platform-dependent)"""
        try:
            import sys

            if sys.platform == "darwin":
                import os

                os.system("afplay /System/Library/Sounds/Glass.aiff")
            elif sys.platform == "win32":
                import winsound

                winsound.MessageBeep()
        except Exception:
            pass

    def urgent(self, title: str, message: str) -> None:
        """Send urgent notification"""
        self.notify(title, message, "urgent", "🔴")

    def info(self, title: str, message: str) -> None:
        """Send info notification"""
        self.notify(title, message, "normal", "🔔")

    def success(self, title: str, message: str) -> None:
        """Send success notification"""
        self.notify(title, message, "normal", "✅")

    def warning(self, title: str, message: str) -> None:
        """Send warning notification"""
        self.notify(title, message, "urgent", "⚠️")

    def email_sent(self, recipient: str) -> None:
        """Notify about sent email"""
        self.success("Email Sent", f"To: {recipient}")

    def email_received(self, sender: str, subject: str) -> None:
        """Notify about received email"""
        self.info("New Email", f"From: {sender}\n{subject[:50]}")
