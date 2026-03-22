"""Tests for encryption engine"""

import os
import pytest
import tempfile
from pathlib import Path
from security.encryption import EncryptionEngine, EncryptionError


class TestEncryption:
    def setup_method(self):
        self.engine = EncryptionEngine()
        # Override paths for testing
        self.test_dir = tempfile.mkdtemp()
        from core.config import Config

        Config.DATA_DIR = Path(self.test_dir)
        Config.SALT_FILE = Path(self.test_dir) / ".salt"
        Config.KEYSTORE_FILE = Path(self.test_dir) / ".keystore"
        Config.PEPPER_FILE = Path(self.test_dir) / ".pepper"

    def test_setup_and_unlock(self):
        self.engine.setup("TestPassword123!")
        assert self.engine.is_unlocked

        self.engine.lock()
        assert not self.engine.is_unlocked

        self.engine.unlock("TestPassword123!")
        assert self.engine.is_unlocked

    def test_wrong_password(self):
        self.engine.setup("TestPassword123!")
        self.engine.lock()

        with pytest.raises(EncryptionError):
            self.engine.unlock("WrongPassword")

    def test_encrypt_decrypt_string(self):
        self.engine.setup("TestPassword123!")

        original = "Hello, World! This is sensitive data."
        encrypted = self.engine.encrypt(original)
        assert encrypted != original

        decrypted = self.engine.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_decrypt_dict(self):
        self.engine.setup("TestPassword123!")

        original = {"name": "John", "amount": 459.00, "secret": True}
        encrypted = self.engine.encrypt_dict(original)
        decrypted = self.engine.decrypt_dict(encrypted)
        assert decrypted == original

    def test_encrypt_file(self):
        self.engine.setup("TestPassword123!")

        # Create test file
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Secret document content")

        # Encrypt
        enc_path = self.engine.encrypt_file(test_file)
        assert enc_path.exists()
        assert not test_file.exists()  # Original deleted

        # Decrypt
        dec_path = self.engine.decrypt_file(enc_path)
        assert dec_path.read_text() == "Secret document content"

    def test_short_password_rejected(self):
        with pytest.raises(EncryptionError):
            self.engine.setup("short")

    def test_secure_delete(self):
        test_file = Path(self.test_dir) / "delete_me.txt"
        test_file.write_text("Sensitive data to delete")
        assert test_file.exists()

        self.engine.secure_delete(test_file)
        assert not test_file.exists()
