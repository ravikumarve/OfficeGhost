"""
AI Office Pilot - Authentication & Access Control
"""

import os
import json
import secrets
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from core.config import Config
from security.encryption import EncryptionEngine, EncryptionError


class AuthError(Exception):
    """Authentication errors"""

    pass


class TwoFactorError(Exception):
    """2FA-related errors"""

    pass


class AccessControl:
    """
    Authentication and session management

    Features:
    - Master password login
    - Auto-lock after inactivity
    - Brute-force protection (lockout)
    - Session management
    - Password strength checking
    - Optional TOTP 2FA
    """

    def __init__(self, crypto: EncryptionEngine):
        self.crypto = crypto
        self.session: Optional[dict] = None
        self.failed_attempts = 0
        self.lockout_until: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self._totp_secret: Optional[str] = None
        self._totp_enabled = False

    @property
    def is_2fa_enabled(self) -> bool:
        """Check if 2FA is configured"""
        return self._totp_enabled and self._totp_secret is not None

    def generate_2fa_secret(self) -> tuple[str, str]:
        """
        Generate a new TOTP secret for 2FA setup
        Returns: (secret, qr_url)
        """
        try:
            import pyotp
        except ImportError:
            raise TwoFactorError("pyotp not installed. Run: pip install pyotp")

        secret = pyotp.random_base32()
        qr_url = pyotp.totp.TOTP(secret).provisioning_uri(
            name="AI Office Pilot", issuer_name="AI Office Pilot"
        )
        return secret, qr_url

    def setup_2fa(self, secret: str, token: str) -> bool:
        """
        Complete 2FA setup with verification
        """
        try:
            import pyotp
        except ImportError:
            raise TwoFactorError("pyotp not installed")

        totp = pyotp.TOTP(secret)
        if not totp.verify(token):
            raise TwoFactorError("Invalid verification code")

        self._totp_secret = secret
        self._totp_enabled = True
        self._save_2fa_config()
        return True

    def verify_2fa(self, token: str) -> bool:
        """Verify TOTP token"""
        if not self.is_2fa_enabled:
            return True

        try:
            import pyotp
        except ImportError:
            return True

        totp = pyotp.TOTP(self._totp_secret)
        return totp.verify(token)

    def disable_2fa(self, password: str, token: str) -> bool:
        """Disable 2FA with password verification"""
        try:
            self.crypto.unlock(password)
        except EncryptionError:
            raise AuthError("Invalid password")

        if not self.verify_2fa(token):
            raise TwoFactorError("Invalid 2FA token")

        self._totp_secret = None
        self._totp_enabled = False
        self._save_2fa_config()
        return True

    def _save_2fa_config(self) -> None:
        """Save 2FA configuration"""
        config_file = Config.DATA_DIR / ".2fa_config"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        config = {"enabled": self._totp_enabled, "secret": self._totp_secret}
        config_file.write_text(json.dumps(config))

    def _load_2fa_config(self) -> None:
        """Load 2FA configuration"""
        config_file = Config.DATA_DIR / ".2fa_config"
        if config_file.exists():
            config = json.loads(config_file.read_text())
            self._totp_enabled = config.get("enabled", False)
            self._totp_secret = config.get("secret")

    def login(self, password: str, totp_token: Optional[str] = None) -> bool:
        """Authenticate and create session"""

        self._load_2fa_config()

        # Check lockout
        if self.lockout_until and datetime.now() < self.lockout_until:
            remaining = (self.lockout_until - datetime.now()).seconds // 60
            raise AuthError(f"Account locked. Try again in {remaining} minutes.")
        elif self.lockout_until:
            self.lockout_until = None
            self.failed_attempts = 0

        # Attempt unlock
        try:
            self.crypto.unlock(password)
        except EncryptionError:
            self.failed_attempts += 1

            if self.failed_attempts >= Config.MAX_LOGIN_ATTEMPTS:
                self.lockout_until = datetime.now() + timedelta(minutes=Config.LOCKOUT_MINUTES)
                raise AuthError(
                    f"Too many failed attempts. Locked for {Config.LOCKOUT_MINUTES} minutes."
                )

            remaining = Config.MAX_LOGIN_ATTEMPTS - self.failed_attempts
            raise AuthError(f"Wrong password. {remaining} attempts remaining.")

        # Verify 2FA if enabled
        if self.is_2fa_enabled:
            if not totp_token:
                raise TwoFactorError("2FA token required")
            if not self.verify_2fa(totp_token):
                self.crypto.lock()
                raise TwoFactorError("Invalid 2FA token")

        # Success — create session
        self.session = {
            "id": secrets.token_hex(32),
            "created": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(hours=Config.SESSION_TIMEOUT_HOURS)).isoformat(),
        }
        self.failed_attempts = 0
        self.last_activity = datetime.now()

        return True

    def check_session(self) -> bool:
        """Verify active session — call before every operation"""
        if not self.session:
            raise AuthError("Not authenticated. Please login.")

        expires = datetime.fromisoformat(self.session["expires"])
        if datetime.now() > expires:
            self.logout()
            raise AuthError("Session expired. Please login again.")

        if self.last_activity:
            idle = (datetime.now() - self.last_activity).total_seconds()
            if idle > Config.AUTO_LOCK_MINUTES * 60:
                self.lock_screen()
                raise AuthError(
                    f"Auto-locked after {Config.AUTO_LOCK_MINUTES} minutes of inactivity."
                )

        self.last_activity = datetime.now()
        return True

    def lock_screen(self) -> None:
        """Lock without full logout"""
        self.crypto.lock()

    def unlock_screen(self, password: str, totp_token: Optional[str] = None) -> bool:
        """Unlock screen with password"""
        try:
            self.crypto.unlock(password)
        except EncryptionError:
            raise AuthError("Wrong password.")

        if self.is_2fa_enabled:
            if not totp_token:
                self.crypto.lock()
                raise TwoFactorError("2FA token required")
            if not self.verify_2fa(totp_token):
                self.crypto.lock()
                raise TwoFactorError("Invalid 2FA token")

        self.last_activity = datetime.now()
        return True

    def logout(self) -> None:
        """Full logout"""
        self.crypto.lock()
        self.session = None
        self.last_activity = None

    @staticmethod
    def check_password_strength(password: str) -> dict:
        """Check password strength"""
        score = 0
        feedback = []

        if len(password) >= 12:
            score += 1
        else:
            feedback.append("Use at least 12 characters")

        if len(password) >= 16:
            score += 1

        if any(c.isupper() for c in password) and any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Mix uppercase and lowercase")

        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Add numbers")

        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            feedback.append("Add special characters")

        strength_labels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]

        return {
            "score": score,
            "max_score": 5,
            "label": strength_labels[score],
            "feedback": feedback,
            "bar": "█" * score + "░" * (5 - score),
        }

    def get_status(self) -> dict:
        """Get auth status"""
        return {
            "authenticated": self.session is not None,
            "session_id": self.session["id"][:8] + "..." if self.session else None,
            "locked": self.crypto.is_unlocked is False,
            "failed_attempts": self.failed_attempts,
            "locked_out": self.lockout_until is not None,
            "two_factor_enabled": self.is_2fa_enabled,
        }
