#!/bin/bash
# GhostOffice Dashboard Launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH="$SCRIPT_DIR"

# Kill existing dashboard if running
pkill -f "python3.*Dashboard/app.py" 2>/dev/null || true
sleep 1

echo "Starting GhostOffice Dashboard..."
python3 Dashboard/app.py