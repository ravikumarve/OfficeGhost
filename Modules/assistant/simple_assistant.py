"""
Simple rule-based assistant for immediate usability
"""

from typing import Dict, List
from core.config import Config


class SimpleOfficeAssistant:
    """Simple assistant that answers common questions without Ollama"""

    def __init__(self):
        self.responses = self._build_responses()

    def _build_responses(self) -> Dict[str, str]:
        """Build response database for common questions"""
        return {
            "system health": "I can check your system health. Let me look at the current status...",
            "files waiting": "I'll check what files are waiting to be processed...",
            "email accounts": "Let me check your configured email accounts...",
            "learning progress": "I'll check how much the AI has learned...",
            "security status": "Let me check your security settings...",
            "how does it work": "GhostOffice automatically processes emails, organizes files, and extracts data using local AI.",
            "what is ghostoffice": "GhostOffice is your private AI assistant that handles emails, files, and data processing locally.",
            "help": "I can help you with: system status, file processing, email accounts, learning progress, and security questions.",
        }

    def get_system_status(self) -> str:
        """Get current system status"""
        try:
            from core.pilot import AIOfficePilot

            pilot = AIOfficePilot()
            status = pilot.get_status()

            return (
                f"System Status: {status['health']['overall']}\n"
                f"RAM Usage: {status['health']['ram']['percent']}%\n"
                f"Disk Free: {status['health']['disk']['free_gb']}GB\n"
                f"Ollama Status: {status['health']['ollama']['status']}\n"
                f"Cycles Completed: {status['cycles_completed']}"
            )
        except:
            return "System status temporarily unavailable"

    def get_file_status(self) -> str:
        """Get file processing status"""
        try:
            from modules.file_commander.watcher import FileWatcher

            watcher = FileWatcher()
            new_files = watcher.scan_new()

            if new_files:
                file_list = ", ".join([f["name"] for f in new_files[:3]])
                if len(new_files) > 3:
                    file_list += f" and {len(new_files) - 3} more"
                return f"{len(new_files)} files waiting: {file_list}"
            else:
                return "No files waiting for processing"
        except:
            return "File status temporarily unavailable"

    def get_email_status(self) -> str:
        """Get email account status"""
        try:
            Config.load_email_accounts()
            if Config.EMAIL_ACCOUNTS:
                accounts = ", ".join([acc["label"] for acc in Config.EMAIL_ACCOUNTS])
                return f"{len(Config.EMAIL_ACCOUNTS)} email accounts: {accounts}"
            else:
                return "No email accounts configured"
        except:
            return "Email status temporarily unavailable"

    def answer_question(self, question: str) -> str:
        """Answer questions based on rules"""
        question_lower = question.lower()

        # Check for specific patterns
        if any(word in question_lower for word in ["health", "status", "how is system"]):
            return self.get_system_status()

        elif any(word in question_lower for word in ["file", "document", "waiting", "process"]):
            return self.get_file_status()

        elif any(word in question_lower for word in ["email", "account", "configure"]):
            return self.get_email_status()

        elif any(word in question_lower for word in ["learn", "progress", "pattern"]):
            return "Learning progress: The AI is continuously learning from your interactions."

        elif any(word in question_lower for word in ["security", "encrypt", "safe"]):
            return "Security: Your data is encrypted with AES-256 and remains 100% local."

        elif "help" in question_lower:
            return (
                "I can help you with:\n"
                "• System health and status\n"
                "• File processing status\n"
                "• Email account information\n"
                "• Learning progress\n"
                "• Security features\n"
                "Just ask me about any of these!"
            )

        else:
            return (
                "I'm your GhostOffice Assistant! I can help you with:\n"
                "• Checking system health\n"
                "• Viewing files waiting processing\n"
                "• Email account status\n"
                "• Learning progress\n"
                "• Security information\n"
                "Try asking about any of these topics."
            )


def ask_simple_assistant(question: str) -> str:
    """Convenience function"""
    assistant = SimpleOfficeAssistant()
    return assistant.answer_question(question)
