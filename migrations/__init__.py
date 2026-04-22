"""
AI Office Pilot - Database Migration System
Manages schema migrations for memory.db
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime

from core.config import Config


class Migration:
    """Represents a single database migration"""

    def __init__(self, version: int, name: str, up: Callable, down: Optional[Callable] = None):
        self.version = version
        self.name = name
        self.up = up
        self.down = down

    def __repr__(self) -> str:
        return f"Migration({self.version}, '{self.name}')"


class MigrationManager:
    """Manages database schema migrations"""

    CURRENT_VERSION = 2

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.MEMORY_DB
        self.migrations = self._get_migrations()

    def _get_migrations(self) -> list[Migration]:
        """Define all migrations"""
        return [
            Migration(1, "initial_schema", self._migrate_1),
            Migration(2, "add_trusted_contacts", self._migrate_2),
        ]

    def _get_current_version(self) -> int:
        """Get current schema version from database"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        # Check if schema_version table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
        if not c.fetchone():
            # Check for legacy tables
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in c.fetchall()]
            if tables:
                # Has legacy schema, version is 0
                conn.close()
                return 0
            conn.close()
            return 0

        # Get version
        c.execute("SELECT version FROM schema_version ORDER BY applied DESC LIMIT 1")
        row = c.fetchone()
        conn.close()

        return row[0] if row else 0

    def _record_migration(self, version: int, name: str) -> None:
        """Record that a migration was applied"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        # Ensure table exists
        c.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL,
                name TEXT NOT NULL,
                applied TEXT NOT NULL
            )
        """)

        c.execute(
            "INSERT INTO schema_version (version, name, applied) VALUES (?, ?, ?)",
            (version, name, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    def upgrade(self) -> list[str]:
        """Run all pending migrations"""
        current = self._get_current_version()
        applied = []

        for migration in self.migrations:
            if migration.version > current:
                print(f"Applying migration {migration.version}: {migration.name}")
                conn = sqlite3.connect(str(self.db_path))
                try:
                    migration.up(conn)
                    self._record_migration(migration.version, migration.name)
                    applied.append(migration.name)
                    print(f"  ✓ Applied {migration.name}")
                except Exception as e:
                    conn.rollback()
                    print(f"  ✗ Failed: {e}")
                    raise
                finally:
                    conn.close()

        return applied

    def current_version(self) -> int:
        """Get current schema version"""
        return self._get_current_version()

    # ═══ MIGRATION DEFINITIONS ═══

    def _migrate_1(self, conn: sqlite3.Connection) -> None:
        """Initial schema creation"""
        c = conn.cursor()

        # Feedback
        c.execute("""CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action_type TEXT NOT NULL,
            action_detail TEXT NOT NULL,
            ai_output TEXT NOT NULL,
            user_feedback TEXT NOT NULL,
            user_correction TEXT,
            context TEXT
        )""")

        # Preferences
        c.execute("""CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            times_confirmed INTEGER DEFAULT 1,
            last_updated TEXT NOT NULL,
            UNIQUE(category, key)
        )""")

        # Writing Samples
        c.execute("""CREATE TABLE IF NOT EXISTS writing_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            content TEXT NOT NULL,
            recipient TEXT,
            word_count INTEGER
        )""")

        # Style DNA
        c.execute("""CREATE TABLE IF NOT EXISTS style_dna (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trait TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            sample_count INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL
        )""")

        # Action Log
        c.execute("""CREATE TABLE IF NOT EXISTS action_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            day_of_week TEXT NOT NULL,
            hour INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            action_detail TEXT NOT NULL,
            context TEXT,
            sequence_id TEXT
        )""")

        # Discovered Patterns
        c.execute("""CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            description TEXT NOT NULL,
            trigger_cond TEXT NOT NULL,
            expected_actions TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            times_observed INTEGER DEFAULT 1,
            last_seen TEXT NOT NULL,
            active INTEGER DEFAULT 1
        )""")

        # Contacts (initial)
        c.execute("""CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            greeting TEXT,
            tone TEXT,
            priority TEXT DEFAULT 'normal',
            forward_to TEXT,
            always_cc TEXT,
            interaction_count INTEGER DEFAULT 0,
            last_interaction TEXT
        )""")

        # Category Rules
        c.execute("""CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT NOT NULL,
            category TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            times_used INTEGER DEFAULT 1,
            last_used TEXT NOT NULL,
            UNIQUE(vendor, category)
        )""")

        conn.commit()

    def _migrate_2(self, conn: sqlite3.Connection) -> None:
        """Add trusted contacts support"""
        c = conn.cursor()

        # Check if contacts table exists and add trusted column
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
        if c.fetchone():
            # Check if column already exists
            c.execute("PRAGMA table_info(contacts)")
            columns = [row[1] for row in c.fetchall()]
            if "trusted" not in columns:
                c.execute("ALTER TABLE contacts ADD COLUMN trusted INTEGER DEFAULT 0")
                conn.commit()


def run_migrations(db_path: Optional[Path] = None) -> list[str]:
    """Run all pending migrations"""
    manager = MigrationManager(db_path)
    return manager.upgrade()


def get_schema_version(db_path: Optional[Path] = None) -> int:
    """Get current schema version"""
    manager = MigrationManager(db_path)
    return manager.current_version()
