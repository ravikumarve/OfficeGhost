#!/bin/bash
# GhostOffice Screenshot Capture Script
# Captures screenshots of all major pages for Gumroad listing

SCREENSHOT_DIR="/media/matrix/DATA/opencode_projects/officeghost/screenshots"
BASE_URL="http://localhost:5000"

# Create screenshots directory
mkdir -p "$SCREENSHOT_DIR"

echo "📸 Capturing GhostOffice screenshots..."

# Function to capture screenshot
capture_screenshot() {
    local page_name=$1
    local url=$2
    local output_file="$SCREENSHOT_DIR/${page_name}.png"

    echo "  Capturing: $page_name"

    # Use Firefox with headless mode to capture screenshot
    firefox --headless --screenshot="$output_file" --window-size=1280,720 "$url" 2>/dev/null

    if [ -f "$output_file" ]; then
        echo "  ✅ Saved: $output_file"
        # Get file size
        size=$(du -h "$output_file" | cut -f1)
        echo "     Size: $size"
    else
        echo "  ❌ Failed to capture: $page_name"
    fi

    # Wait between screenshots
    sleep 2
}

# Capture Dashboard
capture_screenshot "dashboard" "$BASE_URL/"

# Capture Email Brain
capture_screenshot "email-brain" "$BASE_URL/email"

# Capture Learning
capture_screenshot "learning" "$BASE_URL/learning"

# Capture Settings
capture_screenshot "settings" "$BASE_URL/settings"

echo "✨ Screenshot capture complete!"
echo "📁 Screenshots saved to: $SCREENSHOT_DIR"

# List captured screenshots
ls -lh "$SCREENSHOT_DIR"