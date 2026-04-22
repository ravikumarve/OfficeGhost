"""Tests for DataExtractor class"""

import pytest
from unittest.mock import MagicMock, patch


class TestDataExtractor:
    """Test cases for DataExtractor"""

    def test_init(self, mock_config):
        """Test DataExtractor initialization"""
        from modules.data_engine.extractor import DataExtractor

        mock_brain = MagicMock()
        extractor = DataExtractor(mock_brain)

        assert extractor.brain == mock_brain
        assert extractor.VENDOR_WEIGHT == 0.2
        assert extractor.AMOUNT_WEIGHT == 0.3
        assert extractor.DATE_WEIGHT == 0.15

    def test_extract_invoice(self, mock_config):
        """Test invoice data extraction"""
        from modules.data_engine.extractor import DataExtractor

        mock_brain = MagicMock()
        mock_brain.extract_invoice_data.return_value = {
            "vendor": "Acme Corp",
            "amount": 100.00,
            "date": "2026-03-01",
        }

        extractor = DataExtractor(mock_brain)
        result = extractor.extract_invoice("test content")

        assert result["vendor"] == "Acme Corp"
        assert result["amount"] == 100.00

    def test_validate_complete_data(self, mock_config):
        """Test validation with complete data"""
        from modules.data_engine.extractor import DataExtractor

        mock_brain = MagicMock()
        extractor = DataExtractor(mock_brain)

        data = {"vendor": "Acme Corp", "amount": 100.00, "date": "2026-03-01"}

        result = extractor.validate(data)

        assert result["valid"] is True
        assert result["confidence"] == 1.0
        assert len(result["issues"]) == 0

    def test_validate_missing_vendor(self, mock_config):
        """Test validation with missing vendor"""
        from modules.data_engine.extractor import DataExtractor

        mock_brain = MagicMock()
        extractor = DataExtractor(mock_brain)

        data = {"vendor": "Unknown", "amount": 100.00, "date": "2026-03-01"}

        result = extractor.validate(data)

        assert result["valid"] is False
        assert result["confidence"] < 1.0
        assert "vendor_missing" in result["issues"]

    def test_validate_missing_amount(self, mock_config):
        """Test validation with missing amount"""
        from modules.data_engine.extractor import DataExtractor

        mock_brain = MagicMock()
        extractor = DataExtractor(mock_brain)

        data = {"vendor": "Acme Corp", "amount": 0, "date": "2026-03-01"}

        result = extractor.validate(data)

        assert result["valid"] is False
        assert "amount_missing" in result["issues"]

    def test_validate_missing_date(self, mock_config):
        """Test validation with missing date"""
        from modules.data_engine.extractor import DataExtractor

        mock_brain = MagicMock()
        extractor = DataExtractor(mock_brain)

        data = {"vendor": "Acme Corp", "amount": 100.00, "date": None}

        result = extractor.validate(data)

        assert result["valid"] is False
        assert "date_missing" in result["issues"]

    def test_validate_multiple_issues(self, mock_config):
        """Test validation with multiple issues"""
        from modules.data_engine.extractor import DataExtractor

        mock_brain = MagicMock()
        extractor = DataExtractor(mock_brain)

        data = {"vendor": None, "amount": 0, "date": None}

        result = extractor.validate(data)

        assert len(result["issues"]) == 3
        assert result["confidence"] < 0.5

    def test_validate_confidence_calculation(self, mock_config):
        """Test confidence score calculation"""
        from modules.data_engine.extractor import DataExtractor

        mock_brain = MagicMock()
        extractor = DataExtractor(mock_brain)

        # Only vendor missing
        data = {"vendor": "Unknown", "amount": 100, "date": "2026-03-01"}
        result = extractor.validate(data)
        assert result["confidence"] == pytest.approx(0.8, rel=0.01)

        # Vendor and amount missing
        data = {"vendor": "Unknown", "amount": 0, "date": "2026-03-01"}
        result = extractor.validate(data)
        assert result["confidence"] == pytest.approx(0.5, rel=0.01)

    def test_validate_empty_vendor_string(self, mock_config):
        """Test validation with empty vendor string"""
        from modules.data_engine.extractor import DataExtractor

        mock_brain = MagicMock()
        extractor = DataExtractor(mock_brain)

        data = {"vendor": "", "amount": 100, "date": "2026-03-01"}
        result = extractor.validate(data)

        assert result["valid"] is False

    def test_constants_defined(self, mock_config):
        """Test that weight constants are properly defined"""
        from modules.data_engine.extractor import DataExtractor

        assert hasattr(DataExtractor, "VENDOR_WEIGHT")
        assert hasattr(DataExtractor, "AMOUNT_WEIGHT")
        assert hasattr(DataExtractor, "DATE_WEIGHT")
        assert hasattr(DataExtractor, "UNKNOWN_VENDOR")
