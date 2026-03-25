#!/usr/bin/env python3
"""
GhostOffice CLI Entry Point
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Cli import cli

if __name__ == "__main__":
    cli()
