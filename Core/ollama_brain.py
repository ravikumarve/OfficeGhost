"""
AI Office Pilot - Ollama AI Brain
Local LLM interface — ZERO cloud
"""

import json
import requests
from core.config import Config


class OllamaBrain:
    """
    Interface to local Ollama LLM

    All AI processing happens HERE, on YOUR machine.
    Nothing sent to any cloud service. Ever.
    """

    def __init__(self):
        self.model = Config.OLLAMA_MODEL
        self.base_url = Config.OLLAMA_HOST
        self.timeout = Config.OLLAMA_TIMEOUT

    def query(self, prompt, system=None, temperature=0.7):
        """Send prompt to local Ollama"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }

        if system:
            payload["system"] = system

        try:
            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. Is it running? Try: ollama serve"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Ollama took too long (>{self.timeout}s). Try a smaller model.")

    def classify_email(self, subject, sender, body_preview):
        """Classify email into category"""
        prompt = f"""Classify this email into EXACTLY ONE category:
- URGENT (needs immediate human attention)
- ROUTINE (can be auto-replied)
- HAS_ATTACHMENT (has files attached)
- INVOICE (contains invoice/receipt/bill)
- MEETING (meeting request/calendar)
- SPAM (junk/promotional)

Subject: {subject}
From: {sender}
Body: {body_preview[:500]}

Reply with ONLY the category name, nothing else."""

        result = self.query(prompt, temperature=0.1)
        # Clean response
        result = result.strip().upper().replace('"', "").replace("'", "")

        valid = ["URGENT", "ROUTINE", "HAS_ATTACHMENT", "INVOICE", "MEETING", "SPAM"]
        if result not in valid:
            return "ROUTINE"
        return result

    def draft_reply(self, subject, sender, body, contact_info=None, style_prompt=""):
        """Draft email reply"""
        context = ""
        if contact_info:
            context = f"""
Contact info:
- Name: {contact_info.get("name", "Unknown")}
- Use greeting: {contact_info.get("greeting", "Auto")}
- Tone: {contact_info.get("tone", "professional")}
- Priority: {contact_info.get("priority", "normal")}
"""

        prompt = f"""Draft a professional email reply.

Original email:
From: {sender}
Subject: {subject}
Body: {body[:1500]}

{context}
{style_prompt}

Rules:
- Keep it concise (3-5 sentences)
- Be helpful and friendly
- Don't make up information
- If unsure, say you'll follow up

Draft the reply (just the body, no subject):"""

        return self.query(prompt)

    def categorize_file(self, filename, content_preview):
        """Categorize a file"""
        prompt = f"""Categorize this file into ONE category:
invoice, receipt, contract, report, presentation,
spreadsheet, image, correspondence, resume, tax, insurance, medical, other

Filename: {filename}
Content preview: {content_preview[:500]}

Reply with ONLY the category name:"""

        result = self.query(prompt, temperature=0.1).strip().lower()

        valid = list(Config.CATEGORY_FOLDERS.keys())
        if result not in valid:
            return "other"
        return result

    def generate_filename(self, content_preview, original_name, naming_convention=None):
        """Generate smart filename"""
        convention = naming_convention or "YYYY-MM-DD_Source_Description"

        prompt = f"""Generate a smart filename for this document.
Follow this naming convention: {convention}

Original filename: {original_name}
Content preview: {content_preview[:500]}

Examples:
- 2024-12-15_Amazon_Invoice_$459.pdf
- 2024-12-14_ClientXYZ_Contract.pdf
- 2024-12-13_Q4_Sales_Report.pdf

Reply with ONLY the filename (with extension):"""

        result = self.query(prompt, temperature=0.3).strip()
        # Sanitize filename
        result = "".join(c for c in result if c.isalnum() or c in "._-$")
        return result if result else original_name

    def extract_invoice_data(self, content):
        """Extract structured data from invoice"""
        prompt = f"""Extract data from this invoice/document.
Return as valid JSON only:

{{
    "vendor": "company name",
    "date": "YYYY-MM-DD",
    "amount": 0.00,
    "currency": "USD",
    "invoice_number": "if available",
    "category": "expense category",
    "line_items": ["item1", "item2"]
}}

Document content:
{content[:2000]}

Return ONLY valid JSON:"""

        result = self.query(prompt, temperature=0.1)

        # Try to parse JSON
        try:
            # Find JSON in response
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except json.JSONDecodeError:
            pass

        return {
            "vendor": "Unknown",
            "date": None,
            "amount": 0,
            "currency": "USD",
            "invoice_number": None,
            "category": "other",
            "line_items": [],
        }

    def is_available(self):
        """Check if Ollama is running and model is loaded"""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if r.status_code == 200:
                models = r.json().get("models", [])
                model_names = [m["name"] for m in models]
                return {
                    "available": True,
                    "models": model_names,
                    "current_model": self.model,
                    "model_loaded": any(self.model in m for m in model_names),
                }
        except Exception:
            pass

        return {"available": False, "models": [], "current_model": self.model}
