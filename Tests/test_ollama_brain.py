"""Tests for OllamaBrain class"""

import pytest
from unittest.mock import MagicMock, patch


class TestOllamaBrain:
    """Test cases for OllamaBrain"""

    def test_init(self, mock_config):
        """Test OllamaBrain initialization"""
        from core.ollama_brain import OllamaBrain

        brain = OllamaBrain()

        assert brain.model is not None
        assert brain.base_url is not None
        assert brain.timeout == 120

    @patch("core.ollama_brain.requests.post")
    def test_query_success(self, mock_post, mock_config):
        """Test successful query"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.query("Test prompt")

        assert result == "Test response"
        mock_post.assert_called_once()

    @patch("core.ollama_brain.requests.post")
    def test_query_with_system(self, mock_post, mock_config):
        """Test query with system prompt"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Response"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        brain.query("User prompt", system="You are a helpful assistant.")

        call_kwargs = mock_post.call_args[1]
        assert "json" in call_kwargs
        assert call_kwargs["json"]["system"] == "You are a helpful assistant."

    @patch("core.ollama_brain.requests.post")
    def test_query_connection_error(self, mock_post, mock_config):
        """Test query with connection error"""
        import requests
        from core.ollama_brain import OllamaBrain

        mock_post.side_effect = requests.exceptions.ConnectionError()

        brain = OllamaBrain()

        with pytest.raises(ConnectionError) as exc_info:
            brain.query("Test prompt")

        assert "Cannot connect to Ollama" in str(exc_info.value)

    @patch("core.ollama_brain.requests.post")
    def test_query_timeout(self, mock_post, mock_config):
        """Test query with timeout"""
        import requests
        from core.ollama_brain import OllamaBrain

        mock_post.side_effect = requests.exceptions.Timeout()

        brain = OllamaBrain()

        with pytest.raises(TimeoutError) as exc_info:
            brain.query("Test prompt")

        assert "took too long" in str(exc_info.value)

    @patch("core.ollama_brain.requests.post")
    def test_classify_email_urgent(self, mock_post, mock_config):
        """Test email classification - URGENT"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "URGENT"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.classify_email("Test", "sender@test.com", "Body text")

        assert result == "URGENT"

    @patch("core.ollama_brain.requests.post")
    def test_classify_email_routine(self, mock_post, mock_config):
        """Test email classification - ROUTINE"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "ROUTINE"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.classify_email("Test", "sender@test.com", "Body text")

        assert result == "ROUTINE"

    @patch("core.ollama_brain.requests.post")
    def test_classify_email_invalid_response(self, mock_post, mock_config):
        """Test email classification with invalid response"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "INVALID_CATEGORY"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.classify_email("Test", "sender@test.com", "Body text")

        # Should default to ROUTINE
        assert result == "ROUTINE"

    @patch("core.ollama_brain.requests.post")
    def test_draft_reply(self, mock_post, mock_config):
        """Test drafting email reply"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Thank you for your email."}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.draft_reply("Original Subject", "sender@test.com", "Original body text")

        assert "Thank you" in result
        mock_post.assert_called_once()

    @patch("core.ollama_brain.requests.post")
    def test_draft_reply_with_contact(self, mock_post, mock_config):
        """Test drafting reply with contact info"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Reply text"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        contact = {"name": "John", "greeting": "Hey John", "tone": "casual"}

        brain.draft_reply("Subject", "john@test.com", "Body", contact_info=contact)

        # Verify contact info was included in prompt
        call_kwargs = mock_post.call_args[1]
        prompt = call_kwargs["json"]["prompt"]
        assert "John" in prompt

    @patch("core.ollama_brain.requests.post")
    def test_categorize_file(self, mock_post, mock_config):
        """Test file categorization"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "invoice"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.categorize_file("invoice.pdf", "Invoice content")

        assert result == "invoice"

    @patch("core.ollama_brain.requests.post")
    def test_categorize_file_invalid(self, mock_post, mock_config):
        """Test file categorization with invalid response"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "invalid_category"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.categorize_file("file.xyz", "Content")

        assert result == "other"

    @patch("core.ollama_brain.requests.post")
    def test_generate_filename(self, mock_post, mock_config):
        """Test filename generation"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "2026-03-22_Amazon_Invoice.pdf"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.generate_filename("Invoice content", "old_name.pdf")

        assert ".pdf" in result

    @patch("core.ollama_brain.requests.post")
    def test_extract_invoice_data(self, mock_post, mock_config):
        """Test invoice data extraction"""
        import json
        from core.ollama_brain import OllamaBrain

        invoice_json = json.dumps(
            {
                "vendor": "Amazon",
                "date": "2026-03-22",
                "amount": 59.99,
                "currency": "USD",
                "invoice_number": "INV-123",
                "category": "Shopping",
                "line_items": ["Item 1", "Item 2"],
            }
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": invoice_json}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.extract_invoice_data("Invoice content")

        assert result["vendor"] == "Amazon"
        assert result["amount"] == 59.99

    @patch("core.ollama_brain.requests.post")
    def test_extract_invoice_data_invalid_json(self, mock_post, mock_config):
        """Test invoice extraction with invalid JSON"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Not valid JSON"}
        mock_post.return_value = mock_response

        brain = OllamaBrain()
        result = brain.extract_invoice_data("Invoice content")

        assert result["vendor"] == "Unknown"
        assert result["amount"] == 0

    @patch("core.ollama_brain.requests.get")
    def test_is_available_true(self, mock_get, mock_config):
        """Test checking if Ollama is available"""
        from core.ollama_brain import OllamaBrain

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "phi3:mini"}, {"name": "llama3:3b"}]}
        mock_get.return_value = mock_response

        brain = OllamaBrain()
        result = brain.is_available()

        assert result["available"] is True
        assert result["model_loaded"] is True
        assert len(result["models"]) == 2

    @patch("core.ollama_brain.requests.get")
    def test_is_available_false(self, mock_get, mock_config):
        """Test when Ollama is not available"""
        from core.ollama_brain import OllamaBrain

        mock_get.side_effect = Exception("Connection refused")

        brain = OllamaBrain()
        result = brain.is_available()

        assert result["available"] is False
