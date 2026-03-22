"""
AI Office Pilot - Data Lifecycle Management
Auto-purge, export, delete
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from core.config import Config
from security.encryption import EncryptionEngine


class DataLifecycle:
    """
    Manages data retention, export, and deletion

    GDPR compliance:
    - Right to access (export)
    - Right to deletion (secure wipe)
    - Data minimization (auto-purge)
    """

    def __init__(self, crypto: EncryptionEngine):
        self.crypto = crypto

    def run_cleanup(self):
        """Run scheduled cleanup based on retention policies"""
        results = {
            "files_deleted": 0,
            "space_freed_bytes": 0,
            "timestamp": datetime.now().isoformat(),
        }

        for data_type, max_days in Config.RETENTION.items():
            if max_days is None:
                continue

            cutoff = datetime.now() - timedelta(days=max_days)
            cleaned = self._purge_type(data_type, cutoff)
            results["files_deleted"] += cleaned["count"]
            results["space_freed_bytes"] += cleaned["bytes"]

        return results

    def export_all_data(self, output_path):
        """
        GDPR Right to Access
        Export all user data in readable JSON
        """
        output_path = Path(output_path)
        export = {
            "export_date": datetime.now().isoformat(),
            "product": "AI Office Pilot v3.0",
            "data": {},
        }

        # Export database data
        if Config.MEMORY_DB.exists():
            import sqlite3

            conn = sqlite3.connect(Config.MEMORY_DB)
            conn.row_factory = sqlite3.Row

            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

            for table in tables:
                name = table["name"]
                rows = conn.execute(f"SELECT * FROM {name}").fetchall()
                export["data"][name] = [dict(row) for row in rows]

            conn.close()

        output_path.write_text(json.dumps(export, indent=2))
        return str(output_path)

    def delete_all_data(self, confirmation):
        """
        GDPR Right to Erasure
        Permanently delete ALL user data
        """
        if confirmation != "DELETE ALL MY DATA":
            raise ValueError('Must type exactly: "DELETE ALL MY DATA"')

        # Securely delete database
        if Config.MEMORY_DB.exists():
            self.crypto.secure_delete(Config.MEMORY_DB)

        if Config.ENCRYPTED_DB.exists():
            self.crypto.secure_delete(Config.ENCRYPTED_DB)

        # Delete data directories
        for dir_name in ["processed", "pending", "attachments", "temp", "reports"]:
            dir_path = Config.DATA_DIR / dir_name
            if dir_path.exists():
                for f in dir_path.rglob("*"):
                    if f.is_file():
                        self.crypto.secure_delete(f)
                shutil.rmtree(dir_path, ignore_errors=True)

        # Delete encryption keys
        for key_file in [Config.KEYSTORE_FILE, Config.SALT_FILE, Config.PEPPER_FILE]:
            if key_file.exists():
                self.crypto.secure_delete(key_file)

        return True

    def _purge_type(self, data_type, cutoff):
        """Purge specific data type older than cutoff"""
        result = {"count": 0, "bytes": 0}

        dir_map = {
            "temp_files": Config.TEMP_DIR,
            "attachments": Config.ATTACHMENTS_DIR,
        }

        target_dir = dir_map.get(data_type)
        if target_dir and target_dir.exists():
            for f in target_dir.iterdir():
                if f.is_file():
                    mod_time = datetime.fromtimestamp(f.stat().st_mtime)
                    if mod_time < cutoff:
                        size = f.stat().st_size
                        self.crypto.secure_delete(f)
                        result["count"] += 1
                        result["bytes"] += size

        return result
