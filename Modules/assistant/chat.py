"""
GhostOffice Assistant - AI Chat Interface
Provides conversational access to system status, operations, and data
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from core.ollama_brain import OllamaBrain
from core.config import Config
from learning.memory import MemoryEngine


class OfficeAssistant:
    """AI Assistant that answers questions about GhostOffice operations"""

    def __init__(self):
        self.brain = OllamaBrain()
        self.memory = MemoryEngine()

    def get_system_context(self) -> str:
        """Get current system status and context for the AI"""
        from core.pilot import AIOfficePilot

        pilot = AIOfficePilot()
        status = pilot.get_status()

        # Simple text format instead of JSON
        context_lines = [
            "System Status:",
            f"- Health: {status['health']['overall']}",
            f"- RAM Usage: {status['health']['ram']['percent']}%",
            f"- Disk Free: {status['health']['disk']['free_gb']}GB",
            f"- Ollama: {status['health']['ollama']['status']}",
            f"- Cycles Completed: {status['cycles_completed']}",
            "",
            "Security:",
            f"- Status: {status['security']['overall']}",
            "- Encryption: Active",
            "",
            "Learning:",
            f"- Score: {status.get('learning', {}).get('learning_score', 0)}/100",
            f"- Contacts Learned: {status.get('learning', {}).get('contacts_learned', 0)}",
            f"- Patterns Found: {status.get('learning', {}).get('patterns_found', 0)}",
            "",
            "Operations:",
            f"- Cycle Interval: {Config.CYCLE_INTERVAL_MINUTES} minutes",
            f"- Max Files per Cycle: {Config.MAX_FILES_PER_CYCLE}",
            f"- Max Emails per Cycle: {Config.MAX_EMAILS_PER_CYCLE}",
            f"- Watch Folders: {len(Config.WATCH_FOLDERS)} folders configured",
        ]

        return "\n".join(context_lines)

    def get_file_stats(self) -> str:
        """Get file processing statistics"""
        try:
            from modules.file_commander.watcher import FileWatcher

            watcher = FileWatcher()
            new_files = watcher.scan_new()

            if new_files:
                return f"{len(new_files)} new files waiting, including: {', '.join([f['name'] for f in new_files[:3]])}"
            else:
                return "No new files waiting for processing"
        except:
            return "File statistics temporarily unavailable"

    def get_email_stats(self) -> str:
        """Get email processing statistics"""
        try:
            from core.config import Config

            Config.load_email_accounts()

            if Config.EMAIL_ACCOUNTS:
                return f"{len(Config.EMAIL_ACCOUNTS)} email accounts configured"
            else:
                return "No email accounts configured"
        except:
            return "Email statistics temporarily unavailable"

    def answer_question(self, question: str) -> str:
        """Answer questions about GhostOffice operations"""

        # Get current system context
        system_context = self.get_system_context()
        file_stats = self.get_file_stats()
        email_stats = self.get_email_stats()

        # Create combined prompt (avoid system parameter for now)
        combined_prompt = f"""
Based on this system status:
{system_context}

File Status: {file_stats}
Email Status: {email_stats}

Question: {question}

Answer concisely as GhostOffice Assistant:
"""

        response = self.brain.query(combined_prompt)
        return response.strip()

    def get_common_questions(self) -> List[Dict]:
        """Get list of common questions users might ask"""
        return [
            {
                "question": "What files are waiting to be processed?",
                "description": "Shows files detected but not yet organized",
            },
            {
                "question": "How is my system health?",
                "description": "Displays RAM, disk, and overall system status",
            },
            {
                "question": "What email accounts are configured?",
                "description": "Lists all connected email accounts",
            },
            {
                "question": "How much has the AI learned?",
                "description": "Shows learning progress and patterns discovered",
            },
            {
                "question": "How do I sort files manually?",
                "description": "Explains how to trigger file processing",
            },
            {
                "question": "What security features are active?",
                "description": "Shows encryption and security status",
            },
        ]


def ask_assistant(question: str) -> str:
    """Convenience function to ask the assistant a question"""
    assistant = OfficeAssistant()
    return assistant.answer_question(question)
