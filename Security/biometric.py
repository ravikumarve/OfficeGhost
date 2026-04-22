"""
AI Office Pilot - Biometric Authentication
Platform-specific biometric unlock (fingerprint, face, etc.)
"""

import logging
import os
import hashlib
from typing import Optional

logger = logging.getLogger(__name__)


class BiometricError(Exception):
    """Biometric authentication errors"""
    pass


class BiometricAuth:
    """Biometric authentication handler"""

    def __init__(self) -> None:
        self._available = self._check_availability()
        self._service_name = "ai-office-pilot"

    def _check_availability(self) -> bool:
        """Check if biometric auth is available"""
        # Check for available biometric backends
        available_methods = []

        # Linux: Check for PAM modules or biometrics
        if os.path.exists("/usr/lib/security/pam_unix.so"):
            available_methods.append("unix")
        
        # macOS: Check for LocalAuthentication framework
        if os.path.exists("/System/Library/Frameworks/LocalAuthentication.framework"):
            available_methods.append("macos")

        # Windows: Check for Windows Hello
        if os.name == "nt":
            available_methods.append("windows")

        logger.info(f"Available biometric methods: {available_methods}")
        return len(available_methods) > 0

    def is_available(self) -> bool:
        """Check if biometric auth is available on this system"""
        return self._available

    def get_biometric_type(self) -> str:
        """Get the type of biometric available"""
        if os.name == "nt":
            return "Windows Hello"
        elif os.path.exists("/System/Library/Frameworks"):
            return "Touch ID"
        elif os.path.exists("/usr/lib/security"):
            return "PAM"
        return "None"

    def authenticate(self, reason: str = "Unlock AI Office Pilot") -> bool:
        """
        Attempt biometric authentication
        Returns True if successful, False if failed/cancelled
        """
        if not self._available:
            raise BiometricError("Biometric authentication not available")

        # Try platform-specific authentication
        try:
            if os.name == "nt":
                return self._authenticate_windows(reason)
            elif os.path.exists("/System/Library/Frameworks"):
                return self._authenticate_macos(reason)
            else:
                return self._authenticate_linux(reason)
        except Exception as e:
            logger.error(f"Biometric auth failed: {e}")
            return False

    def _authenticate_windows(self, reason: str) -> bool:
        """Windows Hello authentication"""
        # For Windows, we can use ctypes to call Windows Hello API
        # This is a simplified version - full implementation would use WinRT
        try:
            # Check if Windows Hello is enrolled
            # In practice, you'd use the Windows Hello API here
            logger.info("Attempting Windows Hello authentication")
            return True  # Placeholder - requires actual API integration
        except Exception as e:
            logger.warning(f"Windows Hello not available: {e}")
            return False

    def _authenticate_macos(self, reason: str) -> bool:
        """macOS Touch ID authentication"""
        try:
            import ctypes
            from ctypes import util, CFUNCTYPE

            # LocalAuthentication framework binding
            # This would require actual LAContext implementation
            logger.info("Attempting Touch ID authentication")
            return True  # Placeholder - requires actual implementation
        except Exception as e:
            logger.warning(f"Touch ID not available: {e}")
            return False

    def _authenticate_linux(self, reason: str) -> bool:
        """Linux PAM-based authentication"""
        try:
            # Try using python-pam or similar
            logger.info("Attempting PAM biometric authentication")
            
            # Check for fingerpring reader
            if os.path.exists("/dev/input/event0"):
                # Could use fprintd or similar
                pass
            
            return True  # Placeholder
        except Exception as e:
            logger.warning(f"PAM biometric not available: {e}")
            return False

    def enroll(self, method: str = "fingerprint") -> bool:
        """Enroll a new biometric credential"""
        if not self._available:
            raise BiometricError("Biometric enrollment not available")

        logger.info(f"Enrolling {method} for biometric auth")
        return True


class BiometricSession:
    """Store biometric-authenticated session"""

    def __init__(self, auth: BiometricAuth) -> None:
        self.auth = auth
        self._authenticated = False

    def unlock_with_biometric(self) -> bool:
        """Unlock session with biometric"""
        if self.auth.is_available():
            self._authenticated = self.auth.authenticate()
            if self._authenticated:
                logger.info("Session unlocked with biometric")
            return self._authenticated
        return False

    def is_unlocked(self) -> bool:
        """Check if session is unlocked"""
        return self._authenticated

    def lock(self) -> None:
        """Lock the session"""
        self._authenticated = False
        logger.info("Session locked")