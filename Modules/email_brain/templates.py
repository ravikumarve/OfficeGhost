"""
AI Office Pilot - Email Templates
Customizable email reply templates
"""

import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from core.config import Config

logger = logging.getLogger(__name__)


class EmailTemplate:
    """Email reply template"""

    def __init__(
        self,
        name: str,
        subject_template: str,
        body_template: str,
        category: str = "general"
    ) -> None:
        self.name = name
        self.subject_template = subject_template
        self.body_template = body_template
        self.category = category

    def render(
        self,
        sender_name: str,
        original_subject: str,
        context: Optional[dict] = None
    ) -> tuple[str, str]:
        """Render template with context"""
        ctx = context or {}
        ctx.setdefault("sender", sender_name)
        ctx.setdefault("original_subject", original_subject)
        ctx.setdefault("date", datetime.now().strftime("%Y-%m-%d"))

        subject = self.subject_template
        body = self.body_template

        for key, value in ctx.items():
            placeholder = f"{{{key}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))

        return subject, body

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "subject_template": self.subject_template,
            "body_template": self.body_template,
            "category": self.category
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EmailTemplate":
        """Create from dictionary"""
        return cls(
            name=data["name"],
            subject_template=data["subject_template"],
            body_template=data["body_template"],
            category=data.get("category", "general")
        )


class EmailTemplateManager:
    """Manage email templates"""

    DEFAULT_TEMPLATES = [
        EmailTemplate(
            name="acknowledgment",
            subject_template="Re: {original_subject}",
            body_template="""Hi {sender},

Thank you for your email. I've received it and will respond shortly.

Best regards""",
            category="general"
        ),
        EmailTemplate(
            name="meeting_request",
            subject_template="Re: {original_subject}",
            body_template="""Hi {sender},

Thank you for the meeting request. I'm available and would be happy to meet.

Could you please suggest some time slots that work for you?

Best regards""",
            category="meetings"
        ),
        EmailTemplate(
            name="thank_you",
            subject_template="Re: {original_subject}",
            body_template="""Hi {sender},

Thank you so much for your message. I really appreciate it.

Best regards""",
            category="general"
        ),
        EmailTemplate(
            name="information_received",
            subject_template="Re: {original_subject}",
            body_template="""Hi {sender},

Thank you for sharing this information. I've noted the details and will take any necessary action.

Best regards""",
            category="general"
        ),
    ]

    def __init__(self) -> None:
        self.templates: dict[str, EmailTemplate] = {}
        self._load_templates()

    def _get_templates_file(self) -> Path:
        """Get templates file path"""
        return Config.DATA_DIR / "email_templates.json"

    def _load_templates(self) -> None:
        """Load templates from file or use defaults"""
        templates_file = self._get_templates_file()

        if templates_file.exists():
            try:
                with open(templates_file, "r") as f:
                    data = json.load(f)
                    for template_data in data.get("templates", []):
                        template = EmailTemplate.from_dict(template_data)
                        self.templates[template.name] = template
                logger.info(f"Loaded {len(self.templates)} email templates")
            except Exception as e:
                logger.warning(f"Failed to load templates: {e}, using defaults")
                self._load_defaults()
        else:
            self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default templates"""
        for template in self.DEFAULT_TEMPLATES:
            self.templates[template.name] = template

    def save_templates(self) -> None:
        """Save templates to file"""
        templates_file = self._get_templates_file()
        Config.DATA_DIR.mkdir(parents=True, exist_ok=True)

        data = {
            "version": "1.0",
            "templates": [t.to_dict() for t in self.templates.values()]
        }

        with open(templates_file, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(self.templates)} email templates")

    def get_template(self, name: str) -> Optional[EmailTemplate]:
        """Get template by name"""
        return self.templates.get(name)

    def list_templates(self) -> list[dict]:
        """List all templates"""
        return [
            {"name": t.name, "category": t.category}
            for t in self.templates.values()
        ]

    def add_template(self, template: EmailTemplate) -> None:
        """Add or update template"""
        self.templates[template.name] = template
        self.save_templates()

    def delete_template(self, name: str) -> bool:
        """Delete template"""
        if name in self.templates:
            del self.templates[name]
            self.save_templates()
            return True
        return False

    def get_by_category(self, category: str) -> list[EmailTemplate]:
        """Get templates by category"""
        return [t for t in self.templates.values() if t.category == category]