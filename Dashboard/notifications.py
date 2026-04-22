"""
GhostOffice - Notification System
SQLite-backed notification storage
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from core.config import Config


@dataclass
class Notification:
    """Notification data model"""
    id: int
    category: str
    title: str
    message: str
    read: bool
    created_at: str
    metadata: Optional[dict] = None


class NotificationDB:
    """SQLite-backed notification storage"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.DATA_DIR / "notifications.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                read INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_read 
            ON notifications(read, created_at DESC)
        """)
        conn.commit()
        conn.close()
    
    def add(
        self, 
        category: str, 
        title: str, 
        message: str, 
        metadata: Optional[dict] = None
    ) -> int:
        """Add a new notification"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute(
            """INSERT INTO notifications (category, title, message, read, created_at, metadata)
               VALUES (?, ?, ?, 0, ?, ?)""",
            (category, title, message, datetime.utcnow().isoformat(), 
             json.dumps(metadata) if metadata else None)
        )
        conn.commit()
        notif_id = cursor.lastrowid
        conn.close()
        return notif_id
    
    def get_recent(self, limit: int = 20) -> List[Notification]:
        """Get recent notifications"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """SELECT id, category, title, message, read, created_at, metadata
               FROM notifications ORDER BY created_at DESC LIMIT ?""",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            Notification(
                id=row["id"],
                category=row["category"],
                title=row["title"],
                message=row["message"],
                read=bool(row["read"]),
                created_at=row["created_at"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else None
            )
            for row in rows
        ]
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute(
            "SELECT COUNT(*) FROM notifications WHERE read = 0"
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def mark_all_read(self):
        """Mark all notifications as read"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("UPDATE notifications SET read = 1 WHERE read = 0")
        conn.commit()
        conn.close()
    
    def mark_read(self, notification_id: int):
        """Mark a single notification as read"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "UPDATE notifications SET read = 1 WHERE id = ?",
            (notification_id,)
        )
        conn.commit()
        conn.close()
    
    def delete_old(self, days: int = 30):
        """Delete notifications older than specified days"""
        conn = sqlite3.connect(str(self.db_path))
        cutoff = datetime.utcnow().isoformat()
        conn.execute(
            "DELETE FROM notifications WHERE created_at < datetime(?, '-' || ? || ' days')",
            (cutoff, days)
        )
        conn.commit()
        conn.close()


_notification_db = None

def get_notification_db() -> NotificationDB:
    """Get or create notification database instance"""
    global _notification_db
    if _notification_db is None:
        _notification_db = NotificationDB()
    return _notification_db


def notify(category: str, title: str, message: str, metadata: Optional[dict] = None):
    """Add a notification"""
    db = get_notification_db()
    db.add(category, title, message, metadata)


def notify_error(title: str, message: str, metadata: Optional[dict] = None):
    """Add an error notification"""
    notify("error", title, message, metadata)


def notify_success(title: str, message: str, metadata: Optional[dict] = None):
    """Add a success notification"""
    notify("success", title, message, metadata)


def notify_security(title: str, message: str, metadata: Optional[dict] = None):
    """Add a security notification"""
    notify("security", title, message, metadata)


def notify_task(title: str, message: str, metadata: Optional[dict] = None):
    """Add a task notification"""
    notify("task", title, message, metadata)
