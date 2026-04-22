# GhostOffice Screenshot Capture Guide

## Screenshots Needed for Gumroad Listing

### 1. Dashboard (dashboard.png)
**URL:** http://localhost:5000/
**What to capture:**
- Main dashboard with demo data
- Stats cards showing email processing, file organization, learning metrics
- Activity feed with recent actions
- Quick actions panel
- Yellow "DEMO MODE" banner at top

**Key elements to ensure visible:**
- Amber accent colors (#F59E0B)
- Dark background (#0A0A0B)
- Professional card layouts
- Data visualization elements

### 2. Email Brain (email-brain.png)
**URL:** http://localhost:5000/email
**What to capture:**
- Email classification table
- Category breakdown (Urgent, Important, Newsletter, etc.)
- Processing statistics
- AI confidence scores
- Batch processing controls

**Key elements to ensure visible:**
- Classification table with amber highlights
- Category badges with proper styling
- Processing progress indicators
- Clean, professional table layout

### 3. Learning (learning.png)
**URL:** http://localhost:5000/learning
**What to capture:**
- Chart.js projection graphs
- Learning metrics and trends
- Model performance data
- Training progress indicators
- Prediction accuracy charts

**Key elements to ensure visible:**
- Chart.js visualizations with amber accents
- Data trend lines
- Performance metrics cards
- Professional chart styling

### 4. Settings (settings.png)
**URL:** http://localhost:5000/settings
**What to capture:**
- Watch folders configuration
- Email account settings
- AI model preferences
- Security options
- System configuration panels

**Key elements to ensure visible:**
- Form inputs with proper styling
- Toggle switches and controls
- Configuration sections
- Professional settings layout

## Manual Screenshot Instructions

### Option 1: Using GNOME Screenshot
```bash
# Open Firefox and navigate to each page
firefox http://localhost:5000/

# Use GNOME Screenshot tool
gnome-screenshot --area
# Or for full window:
gnome-screenshot --window
```

### Option 2: Using Firefox Developer Tools
1. Open Firefox and navigate to page
2. Press F12 for Developer Tools
3. Use the screenshot tool in the toolbox
4. Capture full page or specific area

### Option 3: Using Command Line Tools
```bash
# Install ImageMagick if needed
sudo apt-get install imagemagick

# Use import command
import -window root screenshot.png
```

## Screenshot Requirements
- **Resolution:** 1280x720 minimum
- **Format:** PNG
- **Quality:** High resolution, clear text
- **Content:** Must show demo mode with yellow banner
- **Branding:** Must use GhostOffice color scheme (amber #F59E0B, dark #0A0A0B)

## Current Status
⚠️ **Automated screenshot capture encountered issues**
- HTTP server startup problems
- Firefox headless mode limitations
- Inotify watch limits on system

**Recommendation:** Manual screenshot capture using the guide above
**Alternative:** Use a different system with fewer limitations for automated capture

## Files Created
- Icon files: ✅ Created successfully
  - ui-upgrade/public/icon-192.png (5.2K)
  - ui-upgrade/public/icon-512.png (18K)
- Screenshots: ⚠️ Need manual capture
  - screenshots/dashboard.png (pending)
  - screenshots/email-brain.png (pending)
  - screenshots/learning.png (pending)
  - screenshots/settings.png (pending)