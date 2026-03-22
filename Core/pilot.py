"""
GhostOffice - Main Orchestrator
The brain that connects everything
"""

import time
import json
import logging
from datetime import datetime
from typing import Optional

from core.config import Config

logger = logging.getLogger(__name__)
from core.ollama_brain import OllamaBrain
from core.queue_manager import QueueManager, Priority
from core.health_monitor import HealthMonitor
from core.error_recovery import RecoveryManager

from security.encryption import EncryptionEngine
from security.auth import AccessControl, AuthError
from security.audit import AuditLogger
from security.threats import ThreatDetector
from security.lifecycle import DataLifecycle
from security.compliance import ComplianceEngine
from security.backup import BackupManager

from learning.memory import MemoryEngine

from modules.email_brain.reader import EmailReader
from modules.email_brain.sender import EmailSender
from modules.file_commander.watcher import FileWatcher
from modules.file_commander.analyzer import FileAnalyzer
from modules.file_commander.sorter import FileSorter
from modules.data_engine.extractor import DataExtractor
from modules.data_engine.sheet_writer import SheetWriter

from notifications.notifier import Notifier


class AIOfficePilot:
    """
    AI Office Pilot v3.0

    The complete AI office assistant that:
    ✅ Handles emails, files, and data
    ✅ Learns your preferences over time
    ✅ Keeps everything encrypted and local
    ✅ Complies with GDPR/HIPAA
    ✅ Runs on 8GB RAM
    """

    def __init__(self):
        # ─── Security (initialized FIRST) ───
        self.crypto = EncryptionEngine()
        self.auth = AccessControl(self.crypto)
        self.audit = AuditLogger()
        self.threats = ThreatDetector(self.audit)
        self.lifecycle = DataLifecycle(self.crypto)
        self.compliance = ComplianceEngine(self.audit, self.lifecycle, self.crypto)
        self.backup = BackupManager(self.crypto)

        # ─── Infrastructure ───
        self.queue = QueueManager()
        self.health = HealthMonitor()
        self.recovery = RecoveryManager()
        self.notifier = Notifier()

        # ─── Core (loaded after auth) ───
        self.brain = None
        self.memory = None
        self.email_readers = []
        self.email_senders = []
        self.file_watcher = None
        self.file_analyzer = None
        self.file_sorter = None
        self.data_extractor = None
        self.sheet_writer = None

        self.is_running = False
        self.cycle_count = 0

    # ═══════════════════════════════════════
    # SETUP & AUTH
    # ═══════════════════════════════════════

    def first_time_setup(self, master_password):
        """First-time setup"""
        Config.create_directories()

        # Setup encryption
        self.crypto.setup(master_password)

        # Setup compliance
        if Config.ENABLE_GDPR:
            self.compliance.enable_gdpr()
        if Config.ENABLE_HIPAA:
            self.compliance.enable_hipaa()

        self.audit.log("SETUP_COMPLETE", "system", "First-time setup completed", "critical")

        return True

    def login(self, password, totp_token: Optional[str] = None):
        """Authenticate and load all modules"""
        self.auth.login(password, totp_token)
        self._load_modules()

        self.audit.log("LOGIN", "security", "User authenticated", "normal")

        return True

    def _load_modules(self):
        """Load all modules after authentication"""
        # AI Brain
        self.brain = OllamaBrain()

        # Learning Memory
        self.memory = MemoryEngine()

        # Email accounts
        Config.load_email_accounts()
        for account in Config.EMAIL_ACCOUNTS:
            self.email_readers.append(EmailReader(account))
            self.email_senders.append(EmailSender(account))

        # File system
        self.file_watcher = FileWatcher()
        self.file_analyzer = FileAnalyzer()
        self.file_sorter = FileSorter()

        # Data processing
        self.data_extractor = DataExtractor(self.brain)
        self.sheet_writer = SheetWriter()

    # ═══════════════════════════════════════
    # MAIN CYCLE
    # ═══════════════════════════════════════

    def run_cycle(self):
        """Run one complete office cycle"""
        try:
            self.auth.check_session()
        except AuthError as e:
            return {"error": str(e), "needs_auth": True}

        self.cycle_count += 1
        cycle_start = datetime.now()
        results = {
            "cycle": self.cycle_count,
            "started": cycle_start.isoformat(),
            "emails_processed": 0,
            "files_organized": 0,
            "data_entries": 0,
            "predictions": [],
            "errors": [],
        }

        # ─── Check predictions ───
        predictions = self.memory.predict()
        results["predictions"] = predictions

        # ─── Process Emails ───
        for i, reader in enumerate(self.email_readers):
            try:
                emails = reader.fetch_unread()

                for email_data in emails:
                    try:
                        self._process_email(email_data, i)
                        results["emails_processed"] += 1
                    except Exception as e:
                        results["errors"].append(f"Email error: {e}")

            except Exception as e:
                results["errors"].append(f"Email reader error: {e}")

        # ─── Process Files ───
        try:
            new_files = self.file_watcher.scan_new()

            for file_info in new_files:
                try:
                    self._process_file(file_info)
                    results["files_organized"] += 1
                except Exception as e:
                    results["errors"].append(f"File error: {e}")

        except Exception as e:
            results["errors"].append(f"File watcher error: {e}")

        # ─── Finalize ───
        cycle_end = datetime.now()
        duration = (cycle_end - cycle_start).total_seconds()
        results["duration_seconds"] = round(duration, 2)
        results["completed"] = cycle_end.isoformat()

        self.audit.log(
            "CYCLE_COMPLETE",
            "system",
            f"Cycle #{self.cycle_count}: "
            f"{results['emails_processed']} emails, "
            f"{results['files_organized']} files, "
            f"{results['data_entries']} data entries "
            f"in {duration:.1f}s",
        )

        return results

    # ═══════════════════════════════════════
    # EMAIL PROCESSING
    # ═══════════════════════════════════════

    def _handle_draft_send(
        self, result: dict, email_data: dict, account_idx: int, contact: Optional[dict]
    ) -> dict:
        """Handle draft email sending logic"""
        if Config.DRY_RUN:
            result["send_status"] = "dry_run_skipped"
            return result

        sender = self.email_senders[account_idx]
        sender_email = email_data["from"]

        # Check if we should auto-send
        if Config.AUTO_SEND_DRAFTS:
            if Config.AUTO_SEND_TRUSTED_ONLY:
                if self.memory.is_trusted_contact(sender_email):
                    try:
                        sender.send_reply(sender_email, email_data["subject"], result["draft"])
                        result["send_status"] = "auto_sent_trusted"
                        self.notifier.info(
                            "Email Sent",
                            f"Auto-sent to {contact.get('name', sender_email) if contact else sender_email}",
                        )
                    except Exception as e:
                        result["send_status"] = f"send_failed: {e}"
            else:
                try:
                    sender.send_reply(sender_email, email_data["subject"], result["draft"])
                    result["send_status"] = "auto_sent"
                except Exception as e:
                    result["send_status"] = f"send_failed: {e}"
        else:
            # Save draft for confirmation
            self._save_pending_draft(email_data, result["draft"])
            result["send_status"] = "pending_confirmation"
            self.notifier.info(
                "Draft Ready",
                f"Review reply to {contact.get('name', sender_email) if contact else sender_email}",
            )

        return result

    def _save_pending_draft(self, email_data: dict, draft: str) -> None:
        """Save draft for user confirmation"""
        import json
        from pathlib import Path

        pending_dir = Config.PENDING_DIR / "drafts"
        pending_dir.mkdir(parents=True, exist_ok=True)

        draft_file = pending_dir / f"{email_data['id']}.json"
        draft_data = {
            "original_email": email_data,
            "draft": draft,
            "created_at": datetime.now().isoformat(),
        }
        draft_file.write_text(json.dumps(draft_data, indent=2))

    def confirm_and_send(self, draft_filename: str) -> bool:
        """Confirm and send a pending draft"""
        draft_file = Config.PENDING_DIR / "drafts" / draft_filename
        if not draft_file.exists():
            return False

        draft_data = json.loads(draft_file.read_text())
        email_data = draft_data["original_email"]
        draft = draft_data["draft"]

        # Find the right sender
        for sender in self.email_senders:
            if sender.account.get("address"):
                try:
                    sender.send_reply(email_data["from"], email_data["subject"], draft)
                    draft_file.unlink()
                    return True
                except Exception:
                    continue

        return False

    def _process_meeting(self, email_data: dict) -> dict:
        """Process meeting request"""
        meeting_info = {
            "type": None,
            "title": None,
            "datetime": None,
            "attendees": [],
            "action": "needs_review",
        }

        # Extract meeting details from email body
        body = email_data.get("body", "")

        # Look for ICS content or meeting patterns
        if "BEGIN:VCALENDAR" in body or "BEGIN:VEVENT" in body:
            meeting_info["type"] = "ics_calendar"
            parsed = self._parse_ics(body)
            meeting_info.update(parsed)
        else:
            # Try to extract meeting info using AI or patterns
            meeting_info["type"] = "text_email"
            meeting_info["title"] = email_data.get("subject", "")

            # Save for calendar
            if Config.AUTO_PROCESS_MEETINGS:
                self._save_pending_meeting(email_data, meeting_info)
            else:
                self.notifier.info(
                    "Meeting Request", f"Review: {email_data.get('subject', 'New meeting')}"
                )

        return meeting_info

    def _parse_ics(self, ics_content: str) -> dict:
        """Parse ICS calendar content"""
        info = {
            "title": None,
            "datetime": None,
            "location": None,
            "attendees": [],
            "description": None,
        }

        lines = ics_content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("SUMMARY:"):
                info["title"] = line[8:].strip()
            elif line.startswith("DTSTART"):
                # Extract datetime
                info["datetime"] = self._extract_ics_datetime(lines, i)
            elif line.startswith("LOCATION:"):
                info["location"] = line[9:].strip()
            elif line.startswith("ATTENDEE"):
                email = line.split(":")[-1].strip()
                if email:
                    info["attendees"].append(email)
            elif line.startswith("DESCRIPTION:"):
                info["description"] = line[12:].strip()

        return info

    def _extract_ics_datetime(self, lines: list, start_idx: int) -> Optional[str]:
        """Extract datetime from ICS format"""
        line = lines[start_idx]
        if "T" in line:
            dt_part = line.split(":")[-1].strip()[:15]
            try:
                return f"{dt_part[:4]}-{dt_part[4:6]}-{dt_part[6:11]}:{dt_part[11:]}"
            except Exception:
                return dt_part
        return None

    def _save_pending_meeting(self, email_data: dict, meeting_info: dict) -> None:
        """Save meeting for user review"""
        import json

        pending_dir = Config.CALENDAR_PENDING_DIR
        pending_dir.mkdir(parents=True, exist_ok=True)

        meeting_file = pending_dir / f"{email_data['id']}_meeting.json"
        meeting_data = {
            "original_email": email_data,
            "meeting_info": meeting_info,
            "created_at": datetime.now().isoformat(),
        }
        meeting_file.write_text(json.dumps(meeting_data, indent=2))

    def _process_email(self, email_data, account_idx):
        """Process a single email with learning"""

        # Security check
        allowed, reason = self.threats.check("email_access")
        if not allowed:
            raise RuntimeError(f"Blocked: {reason}")

        # Audit
        self.audit.log_email(email_data["from"], email_data["subject"], "read")

        # Get contact memory
        contact = self.memory.get_contact(email_data["from"])

        # Classify email
        classification = self.brain.classify_email(
            email_data["subject"], email_data["from"], email_data["body"][:500]
        )

        self.audit.log_ai("email_classification", classification, 85, Config.OLLAMA_MODEL)

        # Get style prompt from learning
        style = self.memory.get_style_prompt()

        result = {"email": email_data["subject"], "classification": classification, "action": None}

        if classification == "SPAM":
            result["action"] = "archived"

        elif classification == "URGENT":
            self.notifier.urgent(
                "Urgent Email", f"From: {email_data['from']}\nSubject: {email_data['subject']}"
            )
            result["action"] = "flagged_urgent"

        elif classification == "MEETING":
            # Handle meeting requests
            meeting_info = self._process_meeting(email_data)
            result["action"] = "meeting_processed"
            result["meeting"] = meeting_info

        elif classification == "ROUTINE":
            # Draft reply
            reply = self.brain.draft_reply(
                email_data["subject"],
                email_data["from"],
                email_data["body"],
                contact_info=contact,
                style_prompt=style,
            )
            result["action"] = "reply_drafted"
            result["draft"] = reply

            # Handle sending
            result = self._handle_draft_send(result, email_data, account_idx, contact)

        elif classification in ("HAS_ATTACHMENT", "INVOICE"):
            # Process attachments
            if email_data["has_attachments"]:
                reader = self.email_readers[account_idx]
                for att in email_data["attachments"]:
                    saved = reader.download_attachment(email_data["id"], att["filename"])
                    if saved:
                        file_info = {
                            "path": saved,
                            "name": att["filename"],
                            "extension": "." + att["filename"].rsplit(".", 1)[-1].lower()
                            if "." in att["filename"]
                            else "",
                            "size": att["size"],
                            "source_folder": "email_attachment",
                        }
                        self._process_file(file_info)

            result["action"] = "attachments_processed"

        # Update contact memory
        self.memory.learn_contact(email_data["from"], name=email_data["from"].split("<")[0].strip())

        # Log action for pattern learning
        self.memory.log_action(
            "email_process",
            email_data["subject"],
            {"from": email_data["from"], "classification": classification},
        )

        return result

    # ═══════════════════════════════════════
    # FILE PROCESSING
    # ═══════════════════════════════════════

    def _process_file(self, file_info):
        """Process a single file with learning"""

        # Security check
        allowed, reason = self.threats.check("file_access")
        if not allowed:
            raise RuntimeError(f"Blocked: {reason}")

        # Start recovery-tracked operation
        op_id = self.recovery.begin_operation(
            "file_organize", {"file": file_info["name"], "path": file_info["path"]}
        )

        try:
            # Audit
            self.audit.log_file(file_info["path"], "process")

            # Analyze content
            content = self.file_analyzer.analyze(file_info)

            # Check learned preference first
            learned_cat = self.memory.get_preference("file_category", file_info["extension"])

            if learned_cat:
                category = learned_cat
            else:
                category = self.brain.categorize_file(file_info["name"], content)

            # Generate smart name
            naming_pref = self.memory.get_preference("file_naming", "convention")
            smart_name = self.brain.generate_filename(content, file_info["name"], naming_pref)

            # Get destination
            destination = self.file_sorter.get_destination(category)

            # Move file
            new_path = self.file_sorter.move_file(file_info["path"], destination, smart_name)

            # If invoice/receipt, extract data
            if category in ("invoice", "receipt"):
                self._process_data(content, file_info, category)

            # Record feedback for learning
            self.memory.record_feedback("file_categorize", file_info["name"], category, "positive")

            # Log action for patterns
            self.memory.log_action("file_organize", file_info["name"], {"category": category})

            # Complete recovery operation
            self.recovery.complete_operation(op_id)

            self.audit.log_file(new_path, "organized")

            return {
                "file": file_info["name"],
                "category": category,
                "new_name": smart_name,
                "destination": new_path,
            }

        except Exception as e:
            self.recovery.fail_operation(op_id, e)
            raise

    # ═══════════════════════════════════════
    # DATA PROCESSING
    # ═══════════════════════════════════════

    def _process_data(self, content, file_info, category):
        """Extract data from document and enter into spreadsheet"""

        extracted = self.data_extractor.extract_invoice(content)
        validation = self.data_extractor.validate(extracted)

        # Check learned vendor category
        if extracted.get("vendor"):
            predicted = self.memory.predict_category(extracted["vendor"])
            if predicted["confidence"] > 0.7:
                extracted["category"] = predicted["category"]

        if validation["confidence"] > 0.7:
            # Auto-enter
            row = self.sheet_writer.write_row(extracted)

            # Learn vendor→category mapping
            if extracted.get("vendor") and extracted.get("category"):
                self.memory.learn_vendor_category(extracted["vendor"], extracted["category"])

            # Audit
            self.audit.log_data(
                file_info["name"], list(extracted.keys()), str(Config.LOCAL_SPREADSHEET)
            )

            self.memory.record_feedback(
                "data_extract", file_info["name"], json.dumps(extracted), "positive"
            )

            return {"status": "auto_entered", "row": row}

        else:
            # Flag for review
            self.notifier.info(
                "Review Needed",
                f"Low confidence extraction: "
                f"{file_info['name']} "
                f"({validation['confidence'] * 100:.0f}%)",
            )

            return {"status": "needs_review", "confidence": validation["confidence"]}

    # ═══════════════════════════════════════
    # CONTINUOUS OPERATION
    # ═══════════════════════════════════════

    def run_continuous(self):
        """Run continuously with interval"""
        self.is_running = True
        interval = Config.CYCLE_INTERVAL_MINUTES

        logger.info(f"Starting continuous mode - cycle every {interval} minutes")
        print(f"\n🤖 GhostOffice running continuously")
        print(f"   Cycle every {interval} minutes")
        print(f"   Press Ctrl+C to stop\n")

        while self.is_running:
            try:
                # Health check
                health = self.health.check_all()
                if health["ram"]["warning"]:
                    logger.warning(f"RAM usage high: {health['ram']['percent']}%")
                    print(f"   ⚠️ RAM usage high: {health['ram']['percent']}%")

                # Run cycle
                result = self.run_cycle()

                if result.get("needs_auth"):
                    logger.error(f"Authentication required: {result['error']}")
                    print(f"   🔒 {result['error']}")
                    break

                # Log cycle summary
                logger.info(
                    f"Cycle #{result['cycle']}: {result['emails_processed']} emails, "
                    f"{result['files_organized']} files, {result['data_entries']} data "
                    f"({result['duration_seconds']}s)"
                )

                # Print summary
                print(
                    f"   ✅ Cycle #{result['cycle']}: "
                    f"{result['emails_processed']} emails, "
                    f"{result['files_organized']} files, "
                    f"{result['data_entries']} data "
                    f"({result['duration_seconds']}s)"
                )

                if result["predictions"]:
                    for p in result["predictions"][:2]:
                        logger.debug(f"Prediction: {p['message']}")
                        print(f"   🔮 {p['message']}")

                if result["errors"]:
                    for e in result["errors"]:
                        logger.warning(f"Cycle error: {e}")
                        print(f"   ⚠️ {e}")

                # Sleep until next cycle
                time.sleep(interval * 60)

            except KeyboardInterrupt:
                logger.info("Continuous mode stopped by user")
                break
            except Exception as e:
                logger.error(f"Continuous mode error: {e}")
                print(f"   ❌ Error: {e}")
                time.sleep(30)  # Wait before retry

        self.shutdown()

    # ═══════════════════════════════════════
    # SHUTDOWN
    # ═══════════════════════════════════════

    def shutdown(self):
        """Secure shutdown"""
        self.is_running = False

        # Disconnect email
        for reader in self.email_readers:
            reader.disconnect()

        # Create backup
        try:
            if self.crypto.is_unlocked:
                self.backup.create_backup()
        except Exception:
            pass

        # Cleanup
        self.lifecycle.run_cleanup()

        # Audit
        self.audit.log("SHUTDOWN", "system", "Clean shutdown", "normal")

        # Verify audit
        self.audit.verify_integrity()

        # Lock encryption
        self.auth.logout()

        logger.info("GhostOffice shutdown complete")
        print("\n🔒 GhostOffice shut down securely")

    # ═══════════════════════════════════════
    # STATUS & REPORTS
    # ═══════════════════════════════════════

    def get_status(self):
        """Complete system status"""
        return {
            "health": self.health.check_all(),
            "security": self.threats.get_status(),
            "learning": self.memory.get_learning_report() if self.memory else {},
            "compliance": self.compliance.check_compliance(),
            "queue": self.queue.stats(),
            "cycles_completed": self.cycle_count,
            "encryption": self.crypto.get_status(),
            "auth": self.auth.get_status(),
        }
