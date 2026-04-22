"""
Minimal assistant test
"""

from core.ollama_brain import OllamaBrain


def minimal_ask(question: str) -> str:
    """Minimal version"""
    brain = OllamaBrain()

    system_prompt = (
        """You are GhostOffice Assistant. Answer questions about the system concisely."""
    )

    return brain.query(question, system=system_prompt)


if __name__ == "__main__":
    # Test
    response = minimal_ask("What is GhostOffice?")
    print("Response:", response)
