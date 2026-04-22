"""
AI Office Pilot - Configuration Manager
Loads settings from .env file and provides defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Load .env file
load_dotenv()


class Config:
    """Central configuration for AI Office Pilot"""

    # ─── Paths ───
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = DATA_DIR / "logs"
    AUDIT_DIR = LOG_DIR / "audit"
    BACKUP_DIR = DATA_DIR / "backups"
    TEMP_DIR = DATA_DIR / "temp"
    REPORT_DIR = DATA_DIR / "reports"
    PROCESSED_DIR = DATA_DIR / "processed"
    PENDING_DIR = DATA_DIR / "pending"
    ATTACHMENTS_DIR = DATA_DIR / "attachments"

    # Security key files
    KEYSTORE_FILE = DATA_DIR / ".keystore"
    SALT_FILE = DATA_DIR / ".salt"
    PEPPER_FILE = DATA_DIR / ".pepper"

    # Database
    MEMORY_DB = DATA_DIR / "memory.db"
    ENCRYPTED_DB = DATA_DIR / "memory.db.enc"

    # ─── Ollama ───
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
    OLLAMA_BACKUP_MODEL = os.getenv("OLLAMA_BACKUP_MODEL", "llama3.2:3b")
    OLLAMA_TIMEOUT = 120  # seconds

    # ─── Email ───
    EMAIL_ACCOUNTS = []

    # ─── File Watching ───
    WATCH_FOLDERS = os.getenv("WATCH_FOLDERS", "~/Downloads,~/Desktop").split(",")
    WATCH_FOLDERS = [os.path.expanduser(f.strip()) for f in WATCH_FOLDERS]
    ORGANIZED_ROOT = os.path.expanduser(os.getenv("ORGANIZED_ROOT", "~/Documents/Organized"))

    # ─── File Categories & Folders ───
    CATEGORY_FOLDERS = {
        "invoice": "Finance/Invoices",
        "receipt": "Finance/Receipts",
        "contract": "Legal/Contracts",
        "report": "Reports",
        "presentation": "Presentations",
        "spreadsheet": "Spreadsheets",
        "image": "Images",
        "correspondence": "Correspondence",
        "resume": "HR/Resumes",
        "tax": "Finance/Tax",
        "insurance": "Insurance",
        "medical": "Medical",
        "other": "Other",
    }

    # ─── Spreadsheet ───
    SPREADSHEET_TYPE = os.getenv("SPREADSHEET_TYPE", "local")
    LOCAL_SPREADSHEET = DATA_DIR / "expenses.xlsx"

    # ─── Dashboard ───
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 5000))
    DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")

    # ─── Demo Mode ───
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

    # ─── Setup ───
    SETUP_COMPLETE = os.getenv("SETUP_COMPLETE", "false").lower() == "true"

    @classmethod
    def reload(cls):
        """Reload environment variables from .env file"""
        load_dotenv(override=True)
        cls.DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
        cls.SETUP_COMPLETE = os.getenv("SETUP_COMPLETE", "false").lower() == "true"

    # ─── Security ───
    AUTO_LOCK_MINUTES = int(os.getenv("AUTO_LOCK_MINUTES", 30))
    SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", 8))
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
    LOCKOUT_MINUTES = int(os.getenv("LOCKOUT_MINUTES", 15))
    MIN_PASSWORD_LENGTH = 12
    PBKDF2_ITERATIONS = 600000

    # ─── Data Retention (days) ───
    RETENTION = {
        "email_content": int(os.getenv("RETENTION_EMAIL_CONTENT", 30)),
        "attachments": int(os.getenv("RETENTION_ATTACHMENTS", 7)),
        "temp_files": int(os.getenv("RETENTION_TEMP_FILES", 1)),
        "audit_logs": int(os.getenv("RETENTION_AUDIT_LOGS", 2555)),
        "invoices": int(os.getenv("RETENTION_INVOICES", 365)),
        "learning_data": None,  # Never delete
    }

    # ─── Performance ───
    CYCLE_INTERVAL_MINUTES = int(os.getenv("CYCLE_INTERVAL_MINUTES", 5))
    MAX_EMAILS_PER_CYCLE = int(os.getenv("MAX_EMAILS_PER_CYCLE", 50))
    MAX_FILES_PER_CYCLE = int(os.getenv("MAX_FILES_PER_CYCLE", 30))

    # ─── Rate Limiting ───
    EMAIL_SEND_DELAY_SECONDS = 3
    MAX_EMAILS_PER_HOUR = 30
    MAX_API_CALLS_PER_MINUTE = 10

    # ─── Notifications ───
    ENABLE_NOTIFICATIONS = os.getenv("ENABLE_DESKTOP_NOTIFICATIONS", "true").lower() == "true"
    ENABLE_SOUND = os.getenv("ENABLE_SOUND", "true").lower() == "true"

    # ─── Compliance ───
    ENABLE_GDPR = os.getenv("ENABLE_GDPR", "false").lower() == "true"
    ENABLE_HIPAA = os.getenv("ENABLE_HIPAA", "false").lower() == "true"

    # ─── Bytez Cloud Backup ───
    BYTEZ_API_KEY = os.getenv("BYTEZ_API_KEY", "")
    USE_BYTEZ = os.getenv("USE_BYTEZ_FOR_HEAVY", "false").lower() == "true"

    # ─── Email Automation ───
    AUTO_SEND_DRAFTS = os.getenv("AUTO_SEND_DRAFTS", "false").lower() == "true"
    AUTO_SEND_TRUSTED_ONLY = os.getenv("AUTO_SEND_TRUSTED_ONLY", "true").lower() == "true"
    DRAFT_CONFIRMATION_REQUIRED = os.getenv("DRAFT_CONFIRMATION_REQUIRED", "true").lower() == "true"

    # ─── Calendar ───
    CALENDAR_DIR = BASE_DIR / "calendar"
    CALENDAR_PENDING_DIR = DATA_DIR / "calendar_pending"
    AUTO_PROCESS_MEETINGS = os.getenv("AUTO_PROCESS_MEETINGS", "false").lower() == "true"

    # ─── Dry Run Mode ───
    DRY_RUN = False

    @classmethod
    def load_email_accounts(cls):
        """Load email account configurations from .env"""
        accounts = []
        i = 1
        while True:
            address = os.getenv(f"EMAIL_{i}_ADDRESS")
            if not address:
                break

            accounts.append(
                {
                    "address": address,
                    "password": os.getenv(f"EMAIL_{i}_PASSWORD", ""),
                    "imap_host": os.getenv(f"EMAIL_{i}_IMAP_HOST", ""),
                    "imap_port": int(os.getenv(f"EMAIL_{i}_IMAP_PORT", 993)),
                    "smtp_host": os.getenv(f"EMAIL_{i}_SMTP_HOST", ""),
                    "smtp_port": int(os.getenv(f"EMAIL_{i}_SMTP_PORT", 587)),
                    "label": os.getenv(f"EMAIL_{i}_LABEL", f"Account {i}"),
                }
            )
            i += 1

        cls.EMAIL_ACCOUNTS = accounts
        return accounts

    @classmethod
    def create_directories(cls):
        """Create all required directories"""
        dirs = [
            cls.DATA_DIR,
            cls.LOG_DIR,
            cls.AUDIT_DIR,
            cls.BACKUP_DIR,
            cls.TEMP_DIR,
            cls.REPORT_DIR,
            cls.PROCESSED_DIR,
            cls.PENDING_DIR,
            cls.ATTACHMENTS_DIR,
            cls.CALENDAR_DIR,
            cls.CALENDAR_PENDING_DIR,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # Create organized folders
        for folder in cls.CATEGORY_FOLDERS.values():
            full_path = Path(cls.ORGANIZED_ROOT) / folder
            full_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []

        # Check Ollama is reachable
        try:
            import requests
            from core.retry import retry_requests

            @retry_requests(max_retries=3, base_delay=1.0)
            def check_ollama():
                return requests.get(f"{cls.OLLAMA_HOST}/api/tags", timeout=5)

            r = check_ollama()
            if r.status_code != 200:
                errors.append("Ollama is not responding")
        except Exception:
            errors.append(f"Cannot reach Ollama at {cls.OLLAMA_HOST}. Is it running?")

        # Check watch folders exist
        for folder in cls.WATCH_FOLDERS:
            if not os.path.exists(folder):
                errors.append(f"Watch folder not found: {folder}")

        return errors
