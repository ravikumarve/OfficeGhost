"""
AI Office Pilot - Error Recovery
Transaction-safe operations with rollback
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from core.config import Config


class RecoveryManager:
    """
    Ensures operations are atomic and recoverable

    If power goes out mid-file-move:
    -> Recovery journal knows what was happening
    -> On restart, completes or rolls back the operation
    """

    def __init__(self) -> None:
        self.journal: dict[str, dict[str, Any]] = self._load_journal()
        self._recover_incomplete()

    def begin_operation(self, op_type: str, details: dict[str, Any]) -> str:
        """Start a tracked operation"""
        op_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        entry: dict[str, Any] = {
            "id": op_id,
            "type": op_type,
            "details": details,
            "status": "in_progress",
            "started": datetime.now().isoformat(),
            "rollback_actions": [],
        }
        self.journal[op_id] = entry
        self._save_journal()
        return op_id

    def add_rollback(self, op_id: str, action: dict[str, Any]) -> None:
        """Add rollback action for an operation"""
        if op_id in self.journal:
            self.journal[op_id]["rollback_actions"].append(action)
            self._save_journal()

    def complete_operation(self, op_id: str) -> None:
        """Mark operation as complete"""
        if op_id in self.journal:
            self.journal[op_id]["status"] = "completed"
            self.journal[op_id]["completed"] = datetime.now().isoformat()
            self._save_journal()

    def fail_operation(self, op_id: str, error: Exception) -> None:
        """Mark operation as failed and rollback"""
        if op_id in self.journal:
            self.journal[op_id]["status"] = "failed"
            self.journal[op_id]["error"] = str(error)
            self._rollback(op_id)
            self._save_journal()

    def _rollback(self, op_id: str) -> None:
        """Execute rollback actions in reverse order"""
        entry = self.journal.get(op_id)
        if not entry:
            return

        for action in reversed(entry.get("rollback_actions", [])):
            try:
                if action["type"] == "restore_file":
                    if Path(action["backup"]).exists():
                        shutil.copy2(action["backup"], action["original"])
                elif action["type"] == "delete_file":
                    if Path(action["path"]).exists():
                        Path(action["path"]).unlink()
            except Exception:
                pass

    def _recover_incomplete(self) -> None:
        """On startup, handle any incomplete operations"""
        for op_id, entry in list(self.journal.items()):
            if entry["status"] == "in_progress":
                self._rollback(op_id)
                entry["status"] = "rolled_back"
        self._save_journal()

    def _load_journal(self) -> dict[str, dict[str, Any]]:
        """Load recovery journal"""
        journal_file = Config.DATA_DIR / "recovery_journal.json"
        if journal_file.exists():
            try:
                return json.loads(journal_file.read_text())
            except Exception:
                return {}
        return {}

    def _save_journal(self) -> None:
        """Save recovery journal"""
        journal_file = Config.DATA_DIR / "recovery_journal.json"
        journal_file.parent.mkdir(parents=True, exist_ok=True)
        journal_file.write_text(json.dumps(self.journal, indent=2))
