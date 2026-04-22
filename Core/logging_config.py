"""
AI Office Pilot - Logging Configuration
Centralized logging with structured output
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from core.config import Config


class Logger:
    """Structured logger for AI Office Pilot"""

    _instance: Optional["Logger"] = None
    _configured = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not Logger._configured:
            self._setup_logging()
            Logger._configured = True

    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        log_dir = Config.LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        simple_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S"
        )

        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # Console handler (INFO+)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)

        # File handler with rotation (DEBUG+)
        # Rotate daily, keep 7 days of logs
        log_file = log_dir / "ai_office_pilot.log"
        file_handler = TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        file_handler.suffix = "%Y-%m-%d"
        root_logger.addHandler(file_handler)

        # Also add a size-based rotating handler for error logs
        error_log = log_dir / "errors.log"
        error_handler = RotatingFileHandler(
            error_log,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)

        # Suppress noisy loggers
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("werkzeug").setLevel(logging.WARNING)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance"""
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger"""
    Logger()
    return logging.getLogger(name)


# Module-level loggers
def log_security(action: str, detail: str, level: str = "INFO") -> None:
    """Log security events"""
    logger = get_logger("security")
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"[SECURITY] {action}: {detail}")


def log_email(action: str, detail: str, level: str = "INFO") -> None:
    """Log email events"""
    logger = get_logger("email")
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"[EMAIL] {action}: {detail}")


def log_file(action: str, detail: str, level: str = "INFO") -> None:
    """Log file events"""
    logger = get_logger("files")
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"[FILE] {action}: {detail}")


def log_data(action: str, detail: str, level: str = "INFO") -> None:
    """Log data events"""
    logger = get_logger("data")
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"[DATA] {action}: {detail}")


def log_ai(action: str, detail: str, level: str = "INFO") -> None:
    """Log AI events"""
    logger = get_logger("ai")
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"[AI] {action}: {detail}")


def log_learning(action: str, detail: str, level: str = "DEBUG") -> None:
    """Log learning events"""
    logger = get_logger("learning")
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"[LEARNING] {action}: {detail}")


def log_system(action: str, detail: str, level: str = "INFO") -> None:
    """Log system events"""
    logger = get_logger("system")
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"[SYSTEM] {action}: {detail}")
