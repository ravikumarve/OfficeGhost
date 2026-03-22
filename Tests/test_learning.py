"""Tests for learning engine"""

import os
import pytest
import tempfile
from pathlib import Path
from learning.memory import MemoryEngine
from core.config import Config


class TestLearning:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        Config.DATA_DIR = Path(self.test_dir)
        Config.MEMORY_DB = Path(self.test_dir) / "test_memory.db"
        self.memory = MemoryEngine()

    def test_feedback_recording(self):
        self.memory.record_feedback("email_reply", "Test Subject", "AI wrote this", "positive")
        stats = self.memory.get_accuracy()
        assert "email_reply" in stats
        assert stats["email_reply"]["accuracy"] == 100.0

    def test_preference_learning(self):
        self.memory.set_preference("file_category", ".pdf", "invoice")
        result = self.memory.get_preference("file_category", ".pdf")
        assert result == "invoice"

    def test_contact_memory(self):
        self.memory.learn_contact(
            "john@example.com", name="John Smith", tone="casual", greeting="Hey John"
        )
        contact = self.memory.get_contact("john@example.com")
        assert contact is not None
        assert contact["name"] == "John Smith"
        assert contact["tone"] == "casual"

    def test_style_learning(self):
        self.memory.learn_style("Hey Mike, Thanks for the update. Looks good to me! Best, Alex")
        profile = self.memory.get_style()
        assert len(profile) > 0
        assert "formality" in profile

    def test_vendor_category(self):
        self.memory.learn_vendor_category("Amazon", "Shopping")
        self.memory.learn_vendor_category("Amazon", "Shopping")

        result = self.memory.predict_category("Amazon")
        assert result["category"] == "Shopping"
        assert result["confidence"] > 0.5

    def test_learning_report(self):
        # Add some data
        self.memory.record_feedback("test", "detail", "output", "positive")
        self.memory.learn_contact("a@b.com", name="Test")
        self.memory.learn_vendor_category("Test Co", "office")

        report = self.memory.get_learning_report()
        assert "learning_score" in report
        assert report["contacts_learned"] >= 1
        assert report["categories_learned"] >= 1
