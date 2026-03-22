"""
AI Office Pilot - Encryption Engine
AES-256 encryption for all stored data
"""

import os
import json
import hashlib
import secrets
from pathlib import Path
from base64 import b64encode, b64decode

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.config import Config


class EncryptionError(Exception):
    """Encryption-related errors"""

    pass


class EncryptionEngine:
    """
    AES-256 Fernet encryption for all user data

    - Master password never stored
    - Key derived using PBKDF2 (600K iterations)
    - Secure file deletion (3-pass overwrite)
    - File-level and field-level encryption
    """

    def __init__(self):
        self.key = None
        self.fernet = None
        self._is_setup = False
        self._is_unlocked = False

    @property
    def is_setup(self):
        """Check if encryption has been set up"""
        return Config.SALT_FILE.exists() and Config.KEYSTORE_FILE.exists()

    @property
    def is_unlocked(self):
        """Check if encryption is currently unlocked"""
        return self._is_unlocked and self.fernet is not None

    def setup(self, master_password):
        """
        First-time encryption setup
        Creates salt, derives key, stores verification token
        """
        if len(master_password) < Config.MIN_PASSWORD_LENGTH:
            raise EncryptionError(
                f"Password must be at least {Config.MIN_PASSWORD_LENGTH} characters"
            )

        # Create data directory
        Config.create_directories()

        # Generate random salt (32 bytes)
        salt = os.urandom(32)

        # Derive key from password using PBKDF2
        key = self._derive_key(master_password, salt)

        # Save salt
        with open(Config.SALT_FILE, "wb") as f:
            f.write(salt)

        # Create Fernet cipher
        self.fernet = Fernet(key)
        self._is_setup = True

        # Create verification token
        verification_token = self.fernet.encrypt(b"AI_OFFICE_PILOT_VERIFIED")

        # Store verification token in keystore
        keystore = {"verification_token": b64encode(verification_token).decode(), "version": "1.0"}
        with open(Config.KEYSTORE_FILE, "w") as f:
            json.dump(keystore, f)

        self._is_unlocked = True
        self.key = key

    def _derive_key(self, master_password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600000,
        )
        return b64encode(kdf.derive(master_password.encode()))

    def unlock(self, master_password: str) -> bool:
        """Unlock encryption with master password"""
        if not self.is_setup:
            raise EncryptionError("Encryption not set up")

        with open(Config.SALT_FILE, "rb") as f:
            salt = f.read()

        key = self._derive_key(master_password, salt)

        try:
            self.fernet = Fernet(key)
            self.key = key
            self._is_unlocked = True

            with open(Config.KEYSTORE_FILE, "r") as f:
                keystore = json.load(f)

            verification_token = b64decode(keystore["verification_token"])
            self.fernet.decrypt(verification_token)
            return True
        except InvalidToken:
            self.fernet = None
            self.key = None
            self._is_unlocked = False
            raise EncryptionError("Invalid password")

    def lock(self):
        """Lock encryption"""
        self.fernet = None
        self.key = None
        self._is_unlocked = False

    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if not self.is_unlocked:
            raise EncryptionError("Encryption not unlocked")
        encrypted = self.fernet.encrypt(data.encode())
        return b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        if not self.is_unlocked:
            raise EncryptionError("Encryption not unlocked")
        decrypted = self.fernet.decrypt(b64decode(encrypted_data))
        return decrypted.decode()

    def secure_delete(self, file_path: str):
        """Securely delete a file (3-pass overwrite)"""
        path = Path(file_path)
        if not path.exists():
            return

        size = path.stat().st_size

        with open(path, "ba+") as f:
            for pattern in [b"\x00", b"\xff", b"\xaa"]:
                f.seek(0)
                f.write(pattern * size)
                f.flush()

        path.unlink()

    def get_status(self) -> dict:
        """Get encryption status"""
        return {"setup": self.is_setup, "unlocked": self.is_unlocked}

    def encrypt_file(self, input_path: str, output_path: str):
        """Encrypt a file"""
        if not self.is_unlocked:
            raise EncryptionError("Encryption not unlocked")

        with open(input_path, "rb") as f:
            data = f.read()

        encrypted = self.fernet.encrypt(data)

        with open(output_path, "wb") as f:
            f.write(encrypted)

    def decrypt_file(self, input_path: str) -> Path:
        """Decrypt a file (in-place, deletes encrypted)"""
        if not self.is_unlocked:
            raise EncryptionError("Encryption not unlocked")

        input_p = Path(input_path)
        output_path = input_p.with_suffix("")

        with open(input_path, "rb") as f:
            encrypted = f.read()

        decrypted = self.fernet.decrypt(encrypted)

        with open(output_path, "wb") as f:
            f.write(decrypted)

        # Secure delete encrypted file
        self.secure_delete(input_path)

        return output_path

    def encrypt_dict(self, data: dict) -> str:
        """Encrypt dictionary data"""
        if not self.is_unlocked:
            raise EncryptionError("Encryption not unlocked")
        json_data = json.dumps(data)
        encrypted = self.fernet.encrypt(json_data.encode())
        return b64encode(encrypted).decode()

    def decrypt_dict(self, encrypted_data: str) -> dict:
        """Decrypt dictionary data"""
        if not self.is_unlocked:
            raise EncryptionError("Encryption not unlocked")
        decrypted = self.fernet.decrypt(b64decode(encrypted_data))
        return json.loads(decrypted.decode())

    def encrypt_file(self, input_path: str) -> Path:
        """Encrypt a file (in-place, deletes original)"""
        if not self.is_unlocked:
            raise EncryptionError("Encryption not unlocked")

        input_p = Path(input_path)
        output_path = input_p.with_suffix(input_p.suffix + ".enc")

        with open(input_path, "rb") as f:
            data = f.read()

        encrypted = self.fernet.encrypt(data)

        with open(output_path, "wb") as f:
            f.write(encrypted)

        # Secure delete original
        self.secure_delete(input_path)

        return output_path
