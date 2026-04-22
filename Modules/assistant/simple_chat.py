"""
Simple test version of the assistant
"""

import sys

sys.path.insert(0, "/home/matrix/Desktop/officeghost")
from core.ollama_brain import OllamaBrain


def simple_ask(question: str) -> str:
    """Simple version without system context"""
    brain = OllamaBrain()

    prompt = f"""
You are GhostOffice Assistant. Please answer this question concisely.

Question: {question}

Answer:
"""

    return brain.query(prompt)


if __name__ == "__main__":
    # Test
    response = simple_ask("What is GhostOffice?")
    print("Response:", response)
