"""
AI Office Pilot - Data Extractor
Extract structured data from documents
"""

from core.ollama_brain import OllamaBrain


class DataExtractor:
    """Extract structured data from documents using AI"""

    VENDOR_WEIGHT = 0.2
    AMOUNT_WEIGHT = 0.3
    DATE_WEIGHT = 0.15
    UNKNOWN_VENDOR = "Unknown"

    def __init__(self, brain: OllamaBrain) -> None:
        self.brain = brain

    def extract_invoice(self, content: str) -> dict:
        """Extract invoice data"""
        return self.brain.extract_invoice_data(content)

    def validate(self, extracted_data: dict) -> dict:
        """Validate extracted data"""
        issues: list[str] = []
        confidence = 1.0

        if not extracted_data.get("vendor") or extracted_data["vendor"] == self.UNKNOWN_VENDOR:
            issues.append("vendor_missing")
            confidence -= self.VENDOR_WEIGHT

        if not extracted_data.get("amount") or extracted_data["amount"] == 0:
            issues.append("amount_missing")
            confidence -= self.AMOUNT_WEIGHT

        if not extracted_data.get("date"):
            issues.append("date_missing")
            confidence -= self.DATE_WEIGHT

        return {"valid": len(issues) == 0, "confidence": max(0, confidence), "issues": issues}
