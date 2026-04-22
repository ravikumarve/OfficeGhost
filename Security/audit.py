"""
AI Office Pilot - Tamper-Proof Audit Logger
Hash-chain logging for compliance
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

from core.config import Config


class AuditLogger:
    """
    Immutable, tamper-proof audit trail

    Every entry is hash-chained to the previous one.
    Any modification breaks the chain and is detectable.
    """

    def __init__(self):
        Config.AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        self.previous_hash = self._get_last_hash()

    def log(self, action, category, detail, sensitivity="normal", data_accessed=None):
        """
        Log an action

        Args:
            action: What happened (e.g., "EMAIL_READ")
            category: email/file/data/security/system
            detail: Human-readable description
            sensitivity: normal/sensitive/critical
            data_accessed: Dict of what data was touched
        """
        entry = {
            "id": self._gen_id(),
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "category": category,
            "detail": detail,
            "sensitivity": sensitivity,
            "data_accessed": data_accessed,
            "previous_hash": self.previous_hash,
        }

        # Hash this entry (tamper-proof chain)
        entry_json = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(entry_json.encode()).hexdigest()
        entry["hash"] = entry_hash

        # Write to daily log file
        log_file = self._get_log_file()
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        self.previous_hash = entry_hash

        return entry

    def log_email(self, from_addr, subject, action):
        """Shortcut for email audit entries"""
        return self.log(
            action=f"EMAIL_{action.upper()}",
            category="email",
            detail=f"From: {from_addr} | Subject: {subject}",
            sensitivity="sensitive",
            data_accessed={
                "type": "email",
                "from": from_addr,
                "subject": subject,
                "action": action,
            },
        )

    def log_file(self, file_path, action):
        """Shortcut for file audit entries"""
        return self.log(
            action=f"FILE_{action.upper()}",
            category="file",
            detail=f"File: {file_path}",
            sensitivity="normal",
            data_accessed={"type": "file", "path": str(file_path), "action": action},
        )

    def log_data(self, source, fields, destination):
        """Shortcut for data extraction audit"""
        return self.log(
            action="DATA_EXTRACTED",
            category="data",
            detail=f"From: {source} | Fields: {', '.join(fields)} | To: {destination}",
            sensitivity="sensitive",
            data_accessed={
                "type": "extraction",
                "source": source,
                "fields": fields,
                "destination": destination,
            },
        )

    def log_ai(self, input_type, decision, confidence, model):
        """Shortcut for AI decision audit"""
        return self.log(
            action="AI_DECISION",
            category="ai",
            detail=f"Input: {input_type} | Decision: {decision} | Confidence: {confidence}% | Model: {model}",
            sensitivity="normal",
            data_accessed={"type": "ai", "model": model, "decision": decision},
        )

    def log_security(self, event_type, detail, severity="high"):
        """Shortcut for security events"""
        return self.log(
            action=f"SECURITY_{event_type}",
            category="security",
            detail=detail,
            sensitivity="critical",
        )

    def verify_integrity(self):
        """Verify the entire audit chain hasn't been tampered with"""
        entries = self._read_all()

        if not entries:
            return {"verified": True, "count": 0, "status": "empty"}

        previous_hash = "genesis"
        for i, entry in enumerate(entries):
            # Reconstruct hash
            entry_copy = dict(entry)
            stored_hash = entry_copy.pop("hash")
            entry_copy["previous_hash"] = previous_hash

            computed = hashlib.sha256(json.dumps(entry_copy, sort_keys=True).encode()).hexdigest()

            if computed != stored_hash:
                return {
                    "verified": False,
                    "count": len(entries),
                    "tampered_at": i,
                    "status": "TAMPERED",
                }

            previous_hash = stored_hash

        return {"verified": True, "count": len(entries), "status": "verified"}

    def export_report(self, start_date=None, end_date=None):
        """Export compliance report"""
        entries = self._read_all()

        if start_date:
            entries = [e for e in entries if e["timestamp"] >= start_date]
        if end_date:
            entries = [e for e in entries if e["timestamp"] <= end_date]

        report = {
            "type": "compliance_audit_report",
            "generated": datetime.now().isoformat(),
            "period": {"start": start_date, "end": end_date},
            "integrity": self.verify_integrity(),
            "total_entries": len(entries),
            "summary": {
                "by_category": {},
                "by_sensitivity": {},
            },
            "entries": entries,
        }

        # Summarize
        for entry in entries:
            cat = entry.get("category", "unknown")
            sen = entry.get("sensitivity", "unknown")
            report["summary"]["by_category"][cat] = report["summary"]["by_category"].get(cat, 0) + 1
            report["summary"]["by_sensitivity"][sen] = (
                report["summary"]["by_sensitivity"].get(sen, 0) + 1
            )

        # Save
        report_file = Config.REPORT_DIR / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, indent=2))

        return str(report_file)

    def get_recent(self, count=50):
        """Get most recent audit entries"""
        entries = self._read_all()
        return entries[-count:]

    def _gen_id(self):
        return hashlib.md5(
            f"{datetime.now().isoformat()}-{os.urandom(8).hex()}".encode()
        ).hexdigest()[:12]

    def _get_log_file(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        return Config.AUDIT_DIR / f"audit_{date_str}.jsonl"

    def _get_last_hash(self):
        entries = self._read_all()
        if entries:
            return entries[-1].get("hash", "genesis")
        return "genesis"

    def _read_all(self):
        entries = []
        if Config.AUDIT_DIR.exists():
            for f in sorted(Config.AUDIT_DIR.glob("audit_*.jsonl")):
                for line in f.read_text().strip().split("\n"):
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return entries
