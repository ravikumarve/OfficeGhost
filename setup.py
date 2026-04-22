#!/usr/bin/env python3
"""
AI Office Pilot - One-Click Setup Script
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          🤖 AI OFFICE PILOT — INSTALLER                     ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Check Python
    print("1️⃣ Checking Python version...")
    if sys.version_info < (3, 9):
        print(f"   ❌ Python 3.9+ required (you have {sys.version})")
        sys.exit(1)
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Step 2: Check Ollama
    print("\n2️⃣ Checking Ollama...")
    try:
        import requests

        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.status_code == 200:
            models = r.json().get("models", [])
            print(f"   ✅ Ollama running ({len(models)} models loaded)")

            model_names = [m["name"] for m in models]
            if not any("phi3" in m or "phi-3" in m or "llama" in m for m in model_names):
                print("   📥 Downloading phi3:mini (recommended for 8GB RAM)...")
                subprocess.run(["ollama", "pull", "phi3:mini"])
        else:
            print("   ⚠️ Ollama not responding")
    except Exception:
        print("   ⚠️ Ollama not detected. Install from: https://ollama.ai")
        print("   Then run: ollama pull phi3:mini")

    # Step 3: Install dependencies
    print("\n3️⃣ Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
    print("   ✅ Dependencies installed")

    # Step 4: Create .env
    print("\n4️⃣ Setting up configuration...")
    env_file = Path(".env")
    if not env_file.exists():
        shutil.copy(".env.example", ".env")
        print("   ✅ Created .env from template")
        print("   📝 Edit .env to add your email credentials")
    else:
        print("   ✅ .env already exists")

    # Step 5: Create directories
    print("\n5️⃣ Creating directories...")
    from core.config import Config

    Config.create_directories()
    print("   ✅ All directories created")

    # Done
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ✅ INSTALLATION COMPLETE!                                 ║
║                                                              ║
║   Next steps:                                                ║
║   1. Edit .env with your email credentials                   ║
║   2. Make sure Ollama is running (ollama serve)             ║
║   3. Run: python main.py                                     ║
║                                                              ║
║   First run will ask you to create a master password.       ║
║   All your data will be encrypted with AES-256.             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
