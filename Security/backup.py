"""
AI Office Pilot - Encrypted Backup System
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

from core.config import Config
from security.encryption import EncryptionEngine


class BackupManager:
    """
    Encrypted backup and restore for learning data

    - Auto-backup on schedule
    - Encrypted backup files
    - Restore with verification
    - Backup rotation (keep last N)
    """

    def __init__(self, crypto: EncryptionEngine):
        self.crypto = crypto
        self.max_backups = 10
        Config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    def create_backup(self):
        """Create encrypted backup of all important data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_dir = Config.BACKUP_DIR / backup_name

        backup_dir.mkdir(parents=True, exist_ok=True)

        # Files to backup
        files_to_backup = []

        if Config.MEMORY_DB.exists():
            files_to_backup.append(Config.MEMORY_DB)

        # Copy files to backup directory
        for file_path in files_to_backup:
            dest = backup_dir / file_path.name
            shutil.copy2(file_path, dest)

        # Create backup manifest
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "files": [str(f.name) for f in files_to_backup],
            "version": "3.0.0",
        }

        manifest_path = backup_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

        # Encrypt entire backup directory
        encrypted_path = Config.BACKUP_DIR / f"{backup_name}.enc"
        self._encrypt_directory(backup_dir, encrypted_path)

        # Clean up unencrypted backup
        shutil.rmtree(backup_dir)

        # Rotate old backups
        self._rotate_backups()

        return str(encrypted_path)

    def restore_backup(self, backup_file):
        """Restore from encrypted backup"""
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_file}")

        # Decrypt backup
        temp_dir = Config.TEMP_DIR / "restore_temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        self._decrypt_directory(backup_path, temp_dir)

        # Read manifest
        manifest_path = temp_dir / "manifest.json"
        if not manifest_path.exists():
            raise ValueError("Invalid backup — no manifest found")

        manifest = json.loads(manifest_path.read_text())

        # Restore files
        for filename in manifest["files"]:
            src = temp_dir / filename
            if src.exists():
                dest = Config.DATA_DIR / filename
                shutil.copy2(src, dest)

        # Cleanup temp
        shutil.rmtree(temp_dir)

        return manifest

    def list_backups(self):
        """List available backups"""
        backups = []
        for f in sorted(Config.BACKUP_DIR.glob("backup_*.enc")):
            backups.append(
                {
                    "file": str(f),
                    "name": f.stem,
                    "size_mb": f.stat().st_size / (1024 * 1024),
                    "created": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                }
            )
        return backups

    def _encrypt_directory(self, dir_path, output_path):
        """Encrypt directory contents into single file"""
        # Pack directory into JSON
        packed = {}
        for file_path in Path(dir_path).rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(dir_path))
                packed[rel_path] = file_path.read_bytes().hex()

        # Encrypt packed data
        packed_json = json.dumps(packed)
        encrypted = self.crypto.encrypt(packed_json)
        Path(output_path).write_text(encrypted)

    def _decrypt_directory(self, encrypted_path, output_dir):
        """Decrypt single file back to directory"""
        encrypted = Path(encrypted_path).read_text()
        packed_json = self.crypto.decrypt(encrypted)
        packed = json.loads(packed_json)

        for rel_path, hex_data in packed.items():
            file_path = Path(output_dir) / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(bytes.fromhex(hex_data))

    def _rotate_backups(self):
        """Keep only last N backups"""
        backups = sorted(Config.BACKUP_DIR.glob("backup_*.enc"), key=lambda f: f.stat().st_mtime)

        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
