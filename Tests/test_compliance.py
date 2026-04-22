"""Tests for ComplianceEngine class"""

import pytest
from unittest.mock import MagicMock, patch


class TestComplianceEngine:
    """Test cases for ComplianceEngine"""

    def _create_engine(self, mock_config, crypto=None):
        """Helper to create ComplianceEngine with dependencies"""
        from security.compliance import ComplianceEngine
        from security.audit import AuditLogger
        from security.lifecycle import DataLifecycle
        from security.encryption import EncryptionEngine

        audit = AuditLogger()
        if crypto is None:
            crypto = EncryptionEngine()
        lifecycle = DataLifecycle(crypto)
        return ComplianceEngine(audit, lifecycle, crypto)

    def test_init(self, mock_config):
        """Test ComplianceEngine initialization"""
        from security.compliance import ComplianceEngine
        from security.audit import AuditLogger
        from security.lifecycle import DataLifecycle
        from security.encryption import EncryptionEngine

        audit = AuditLogger()
        crypto = EncryptionEngine()
        lifecycle = DataLifecycle(crypto)

        engine = ComplianceEngine(audit, lifecycle, crypto)

        assert engine.audit is not None
        assert engine.lifecycle is not None
        assert engine.crypto is not None
        assert len(engine.enabled) == 0

    def test_enable_gdpr(self, mock_config):
        """Test enabling GDPR compliance"""
        from security.compliance import ComplianceEngine
        from security.encryption import EncryptionEngine
        from core.config import Config

        crypto = EncryptionEngine()
        engine = self._create_engine(mock_config, crypto)

        # Store original values
        original_email = Config.RETENTION["email_content"]
        original_attach = Config.RETENTION["attachments"]

        engine.enable_gdpr()

        assert "GDPR" in engine.enabled
        assert Config.RETENTION["email_content"] == 30
        assert Config.RETENTION["attachments"] == 7

        # Restore
        Config.RETENTION["email_content"] = original_email
        Config.RETENTION["attachments"] = original_attach

    def test_enable_hipaa(self, mock_config):
        """Test enabling HIPAA compliance"""
        from security.compliance import ComplianceEngine
        from security.encryption import EncryptionEngine
        from core.config import Config

        crypto = EncryptionEngine()
        engine = self._create_engine(mock_config, crypto)

        # Store original
        original = Config.RETENTION["audit_logs"]

        engine.enable_hipaa()

        assert "HIPAA" in engine.enabled
        assert Config.RETENTION["audit_logs"] == 2190

        # Restore
        Config.RETENTION["audit_logs"] = original

    def test_check_compliance_all_pass(self, mock_config, mock_encryption):
        """Test compliance check when all pass"""
        engine = self._create_engine(mock_config, mock_encryption)

        result = engine.check_compliance()

        assert "timestamp" in result
        assert result["regulations"] == []
        assert result["overall"] == "COMPLIANT"
        assert len(result["checks"]) == 6

        # Check all checks pass
        for check in result["checks"]:
            assert check["status"] == "PASS"

    def test_check_compliance_with_regulation(self, mock_config):
        """Test compliance check with regulations enabled"""
        from security.encryption import EncryptionEngine

        crypto = EncryptionEngine()
        engine = self._create_engine(mock_config, crypto)

        engine.enable_gdpr()
        engine.enable_hipaa()

        result = engine.check_compliance()

        assert "GDPR" in result["regulations"]
        assert "HIPAA" in result["regulations"]

    def test_check_compliance_encryption_failed(self, mock_config):
        """Test compliance check when encryption is not setup"""
        from security.audit import AuditLogger
        from security.lifecycle import DataLifecycle

        audit = AuditLogger()

        # Mock encryption that is not setup
        crypto = MagicMock()
        crypto.is_setup = False

        lifecycle = DataLifecycle(crypto)

        from security.compliance import ComplianceEngine

        engine = ComplianceEngine(audit, lifecycle, crypto)

        result = engine.check_compliance()

        # Find encryption check
        encrypt_check = next(
            (c for c in result["checks"] if c["name"] == "Encryption active"), None
        )
        assert encrypt_check is not None
        assert encrypt_check["status"] == "FAIL"
        assert result["overall"] == "NON-COMPLIANT"

    def test_check_compliance_audit_failed(self, mock_config):
        """Test compliance check when audit verification fails"""
        from security.lifecycle import DataLifecycle
        from security.encryption import EncryptionEngine

        audit = MagicMock()
        audit.verify_integrity.return_value = {"verified": False, "status": "TAMPERED"}

        crypto = EncryptionEngine()
        lifecycle = DataLifecycle(crypto)

        from security.compliance import ComplianceEngine

        engine = ComplianceEngine(audit, lifecycle, crypto)

        result = engine.check_compliance()

        # Find audit check
        audit_check = next((c for c in result["checks"] if c["name"] == "Audit trail"), None)
        assert audit_check is not None
        assert audit_check["status"] == "FAIL"
        assert result["overall"] == "NON-COMPLIANT"

    def test_generate_report(self, mock_config, mock_encryption):
        """Test generating full compliance report"""
        engine = self._create_engine(mock_config, mock_encryption)

        report = engine.generate_report()

        assert "compliance" in report
        assert "audit_report" in report
        assert "generated" in report
        assert report["compliance"]["overall"] == "COMPLIANT"

    def test_multiple_regulations(self, mock_config):
        """Test enabling multiple regulations"""
        from security.encryption import EncryptionEngine

        crypto = EncryptionEngine()
        engine = self._create_engine(mock_config, crypto)

        engine.enable_gdpr()
        assert len(engine.enabled) == 1

        engine.enable_hipaa()
        assert len(engine.enabled) == 2
        assert "GDPR" in engine.enabled
        assert "HIPAA" in engine.enabled
