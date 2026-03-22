"""
GhostOffice - Web Dashboard
Beautiful local web interface
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

from core.pilot import AIOfficePilot
from core.config import Config
from security.auth import AuthError, TwoFactorError

try:
    from core.metrics import get_metrics

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

try:
    from security.rate_limit import rate_limit_api, rate_limit_auth
    from security.network import check_ip_allowlist, get_allowlist

    SECURITY_MODULES = True
except ImportError:
    SECURITY_MODULES = False

app = Flask(__name__)
app.secret_key = "change-this-to-random-secret-on-setup"

# Global pilot instance
pilot = None


def get_pilot():
    """Get or create pilot instance"""
    global pilot
    if pilot is None:
        pilot = AIOfficePilot()
    return pilot


def login_required(f):
    """Decorator to require authentication"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        try:
            p = get_pilot()
            if p.auth.session is None:
                session.clear()
                return redirect(url_for("login"))
            p.auth.check_session()
        except AuthError:
            session.clear()
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


# ═══════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════


@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect to setup if not complete
    if not Config.SETUP_COMPLETE:
        return redirect(url_for("setup"))
    
    if request.method == "POST":
        # Check IP allowlist
        if SECURITY_MODULES and not check_ip_allowlist(request):
            return render_template("login.html", error="Access denied from this IP address")

        password = request.form.get("password", "")
        totp_token = request.form.get("totp_token", "")
        p = get_pilot()

        if not p.crypto.is_setup:
            confirm = request.form.get("confirm_password", "")
            if password != confirm:
                flash("Passwords do not match", "error")
                return render_template("login.html", setup=True)
            if len(password) < 12:
                flash("Password must be at least 12 characters", "error")
                return render_template("login.html", setup=True)

            try:
                p.first_time_setup(password)
                p.login(password)
                session["authenticated"] = True
                flash("Setup complete! Welcome to AI Office Pilot", "success")
                return redirect(url_for("dashboard"))
            except TwoFactorError as e:
                flash(str(e), "error")
                return render_template("login.html", setup=True)
            except Exception as e:
                flash(str(e), "error")
                return render_template("login.html", setup=True)
        else:
            try:
                p.login(password, totp_token=totp_token or None)
                session["authenticated"] = True
                return redirect(url_for("dashboard"))
            except TwoFactorError as e:
                flash(str(e), "error")
                return render_template("login.html", setup=False, require_2fa=True)
            except Exception as e:
                flash(str(e), "error")
                return render_template("login.html", setup=False)

    p = get_pilot()
    return render_template("login.html", setup=not p.crypto.is_setup)


@app.route("/logout")
def logout():
    p = get_pilot()
    try:
        p.shutdown()
    except Exception:
        pass
    session.clear()
    flash("Logged out securely", "success")
    return redirect(url_for("login"))


# ═══════════════════════════════════════
# SETUP WIZARD
# ═══════════════════════════════════════


@app.route("/setup")
def setup():
    """First-run setup wizard"""
    if Config.SETUP_COMPLETE:
        return redirect(url_for("login"))
    
    available_models = []
    try:
        import requests
        r = requests.get(f"{Config.OLLAMA_HOST}/api/tags", timeout=5)
        if r.status_code == 200:
            data = r.json()
            available_models = [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        pass
    
    return render_template("setup.html", models=available_models)


@app.route("/api/email/test", methods=["POST"])
def test_email():
    """Test email connection"""
    data = request.get_json()
    email = data.get("email", "")
    password = data.get("password", "")
    imap_host = data.get("imap_host", "imap.gmail.com")
    
    try:
        import imaplib
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(email, password)
        mail.logout()
        return jsonify({"success": True, "message": "Connected successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/setup/email", methods=["POST"])
def save_email_setup():
    """Save email configuration"""
    data = request.get_json()
    
    env_path = Config.BASE_DIR / ".env"
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    email_num = 1
    for line in lines:
        if line.startswith("EMAIL_"):
            parts = line.split("_")
            if len(parts) >= 2:
                try:
                    num = int(parts[1].split("_")[0])
                    email_num = max(email_num, num + 1)
                except (ValueError, IndexError):
                    pass
    
    new_lines = []
    for line in lines:
        if line.startswith(f"EMAIL_{email_num}_ADDRESS="):
            line = f"EMAIL_{email_num}_ADDRESS={data.get('email', '')}\n"
        elif line.startswith(f"EMAIL_{email_num}_PASSWORD="):
            line = f"EMAIL_{email_num}_PASSWORD={data.get('password', '')}\n"
        elif line.startswith(f"EMAIL_{email_num}_IMAP_HOST="):
            line = f"EMAIL_{email_num}_IMAP_HOST={data.get('imap_host', 'imap.gmail.com')}\n"
        elif line.startswith(f"EMAIL_{email_num}_SMTP_HOST="):
            line = f"EMAIL_{email_num}_SMTP_HOST={data.get('smtp_host', 'smtp.gmail.com')}\n"
        new_lines.append(line)
    
    if not any(f"EMAIL_{email_num}_ADDRESS=" in l for l in new_lines):
        new_lines.append(f"EMAIL_{email_num}_ADDRESS={data.get('email', '')}\n")
        new_lines.append(f"EMAIL_{email_num}_PASSWORD={data.get('password', '')}\n")
        new_lines.append(f"EMAIL_{email_num}_IMAP_HOST={data.get('imap_host', 'imap.gmail.com')}\n")
        new_lines.append(f"EMAIL_{email_num}_SMTP_HOST={data.get('smtp_host', 'smtp.gmail.com')}\n")
    
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    
    return jsonify({"status": "success"})


@app.route("/api/setup/model", methods=["POST"])
def save_model_setup():
    """Save model selection"""
    data = request.get_json()
    model = data.get("model", "")
    
    env_path = Config.BASE_DIR / ".env"
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    found = False
    for line in lines:
        if line.startswith("OLLAMA_MODEL="):
            new_lines.append(f"OLLAMA_MODEL={model}\n")
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        new_lines.append(f"OLLAMA_MODEL={model}\n")
    
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    
    return jsonify({"status": "success"})


@app.route("/api/setup/complete", methods=["POST"])
def complete_setup():
    """Mark setup as complete"""
    env_path = Config.BASE_DIR / ".env"
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    found = False
    for line in lines:
        if line.startswith("SETUP_COMPLETE="):
            new_lines.append("SETUP_COMPLETE=true\n")
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        new_lines.append("SETUP_COMPLETE=true\n")
    
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    
    return jsonify({"status": "success"})


# ═══════════════════════════════════════
# MAIN DASHBOARD
# ═══════════════════════════════════════


@app.route("/")
def index():
    """Landing page - shows for everyone"""
    if not Config.SETUP_COMPLETE:
        return redirect(url_for("setup"))
    if session.get("authenticated"):
        return redirect("/dashboard")
    return render_template("landing.html")


@app.route("/docs")
def docs():
    """Documentation page"""
    return """
    <!DOCTYPE html>
    <html lang="en" data-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Documentation — GhostOffice</title>
        <style>
            body { font-family: 'Inter', sans-serif; max-width: 900px; margin: 0 auto; padding: 40px 20px; background: #1a1a2e; color: #fff; }
            h1 { color: #6366f1; }
            h2 { color: #a855f7; margin-top: 40px; }
            a { color: #6366f1; }
            code { background: #16213e; padding: 2px 8px; border-radius: 4px; }
            pre { background: #16213e; padding: 20px; border-radius: 8px; overflow-x: auto; }
            .nav { margin-bottom: 30px; }
            .nav a { margin-right: 20px; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">← Back to Home</a>
            <a href="https://github.com/ravikumarve/OfficeGhost" target="_blank">GitHub →</a>
        </div>
        <h1>📖 GhostOffice Documentation</h1>
        
        <h2>Quick Start</h2>
        <pre>pip install -r requirements.txt
python3 setup.py
python3 main.py</pre>

        <h2>Dashboard</h2>
        <p>Access the web dashboard at: <code>http://localhost:5000</code></p>

        <h2>Configuration</h2>
        <p>Copy <code>.env.example</code> to <code>.env</code> and configure your email accounts.</p>

        <h2>GitHub</h2>
        <p>For full documentation, source code, and contributions, visit:</p>
        <p><a href="https://github.com/ravikumarve/OfficeGhost" target="_blank">https://github.com/ravikumarve/OfficeGhost</a></p>
        
        <hr style="margin-top: 60px; border-color: #333;">
        <p style="color: #666;">GhostOffice v3.0 — Your Private AI Assistant</p>
    </body>
    </html>
    """


@app.route("/dashboard")
@login_required
def dashboard():
    if Config.DEMO_MODE:
        from core.demo_data import get_demo_status, get_demo_emails, get_demo_notifications
        
        status = get_demo_status()
        processed_emails = get_demo_emails()[:5]
        recent_activity = get_demo_notifications()
        security_status = {
            "overall": "🟢 FULLY SECURE",
            "color": "green",
            "icon": "🟢",
            "detail": "AES-256 Encrypted"
        }
    else:
        p = get_pilot()
        status = p.get_status()
        recent_activity = p.audit.get_recent(10) if p.audit else []
        
        from modules.email_brain.reader import EmailReader
        processed_emails = EmailReader.get_processed_emails(5) or []
        
        encryption = status.get("encryption", {})
        if encryption.get("setup") and encryption.get("unlocked"):
            security_status = {
                "overall": "🟢 FULLY SECURE",
                "color": "green",
                "icon": "🟢",
                "detail": "AES-256 Encrypted"
            }
        else:
            security_status = {
                "overall": "🟡 PARTIALLY SECURE",
                "color": "yellow",
                "icon": "🟡",
                "detail": "Encryption Not Initialized"
            }
    
    return render_template(
        "index.html", 
        status=status, 
        activity=recent_activity,
        processed_emails=processed_emails,
        security_status=security_status,
        demo_mode=Config.DEMO_MODE
    )


# ═══════════════════════════════════════
# ACTION ROUTES
# ═══════════════════════════════════════


@app.route("/run-cycle", methods=["POST"])
@login_required
@rate_limit_api()
def run_cycle():
    p = get_pilot()
    result = p.run_cycle()
    return jsonify(result)


@app.route("/start-continuous", methods=["POST"])
@login_required
def start_continuous():
    p = get_pilot()
    # In production, run in background thread
    import threading

    thread = threading.Thread(target=p.run_continuous, daemon=True)
    thread.start()
    return jsonify({"status": "started"})


@app.route("/stop", methods=["POST"])
@login_required
def stop_continuous():
    p = get_pilot()
    p.is_running = False
    return jsonify({"status": "stopped"})


# ═══════════════════════════════════════
# STATUS ROUTES
# ═══════════════════════════════════════


@app.route("/api/status")
@login_required
@rate_limit_api()
def api_status():
    p = get_pilot()
    return jsonify(p.get_status())


@app.route("/api/health")
@login_required
@rate_limit_api()
def api_health():
    p = get_pilot()
    return jsonify(p.health.check_all())


# ═══════════════════════════════════════
# NOTIFICATION ROUTES
# ═══════════════════════════════════════


@app.route("/api/notifications")
@login_required
def api_notifications():
    from dashboard.notifications import get_notification_db
    db = get_notification_db()
    notifications = db.get_recent(20)
    return jsonify({
        "unread_count": db.get_unread_count(),
        "notifications": [
            {
                "id": n.id,
                "category": n.category,
                "title": n.title,
                "message": n.message,
                "read": n.read,
                "created_at": n.created_at,
                "metadata": n.metadata
            }
            for n in notifications
        ]
    })


@app.route("/api/notifications/mark-read", methods=["POST"])
@login_required
def api_mark_read():
    from dashboard.notifications import get_notification_db
    db = get_notification_db()
    db.mark_all_read()
    return jsonify({"success": True})


@app.route("/api/notifications/unread-count")
@login_required
def api_unread_count():
    from dashboard.notifications import get_notification_db
    db = get_notification_db()
    return jsonify({"count": db.get_unread_count()})


# ═══════════════════════════════════════
# EMAIL BRAIN ROUTES
# ═══════════════════════════════════════


@app.route("/email")
@login_required
def email_brain():
    if Config.DEMO_MODE:
        from core.demo_data import get_demo_emails
        emails = get_demo_emails()
    else:
        from modules.email_brain.reader import EmailReader
        emails = EmailReader.get_processed_emails(50) or []
    
    stats = {
        "total": len(emails),
        "urgent": sum(1 for e in emails if e.get("classification", "").upper() == "URGENT"),
        "routine": sum(1 for e in emails if e.get("classification", "").upper() == "ROUTINE"),
        "spam": sum(1 for e in emails if e.get("classification", "").upper() == "SPAM"),
        "meeting": sum(1 for e in emails if e.get("classification", "").upper() == "MEETING"),
    }
    
    return render_template("email.html", emails=emails, stats=stats, demo_mode=Config.DEMO_MODE)


# ═══════════════════════════════════════
# LEARNING ROUTES
# ═══════════════════════════════════════


@app.route("/learning")
@login_required
def learning():
    p = get_pilot()
    report = p.memory.get_learning_report() if p.memory else {}
    return render_template("learning.html", report=report)


@app.route("/api/learning")
@login_required
def api_learning():
    p = get_pilot()
    if p.memory:
        return jsonify(p.memory.get_learning_report())
    return jsonify({})


# ═══════════════════════════════════════
# SECURITY ROUTES
# ═══════════════════════════════════════


@app.route("/security")
@login_required
def security():
    p = get_pilot()
    sec_status = p.threats.get_status()
    compliance = p.compliance.check_compliance()
    audit_entries = p.audit.get_recent(20)
    encryption_status = p.crypto.get_status()
    return render_template(
        "security.html", security=sec_status, compliance=compliance, 
        audit=audit_entries, encryption=encryption_status
    )


@app.route("/api/security")
@login_required
def api_security():
    p = get_pilot()
    return jsonify(
        {
            "security": p.threats.get_status(),
            "compliance": p.compliance.check_compliance(),
            "encryption": p.crypto.get_status(),
            "audit_integrity": p.audit.verify_integrity(),
        }
    )


# ═══════════════════════════════════════
# METRICS ROUTES
# ═══════════════════════════════════════


@app.route("/api/metrics")
def api_metrics():
    """Prometheus-compatible metrics endpoint"""
    if not METRICS_AVAILABLE:
        return jsonify({"error": "Metrics not available"}), 503

    metrics = get_metrics()
    return metrics.get_prometheus_output(), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/api/metrics/json")
@login_required
def api_metrics_json():
    """Metrics as JSON"""
    if not METRICS_AVAILABLE:
        return jsonify({"error": "Metrics not available"}), 503

    metrics = get_metrics()
    return jsonify(metrics.to_dict())


# ═══════════════════════════════════════
# BACKUP & DATA ROUTES
# ═══════════════════════════════════════


@app.route("/backup", methods=["POST"])
@login_required
def create_backup():
    p = get_pilot()
    try:
        path = p.backup.create_backup()
        return jsonify({"status": "success", "path": path})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/export-data", methods=["POST"])
@login_required
def export_data():
    p = get_pilot()
    try:
        path = Config.REPORT_DIR / "my_data_export.json"
        p.lifecycle.export_all_data(path)
        return jsonify({"status": "success", "path": str(path)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/compliance-report", methods=["POST"])
@login_required
def compliance_report():
    p = get_pilot()
    try:
        result = p.compliance.generate_report()
        return jsonify({"status": "success", "report": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ═══════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════


@app.route("/settings")
@login_required
def settings():
    p = get_pilot()
    backups = p.backup.list_backups()
    
    # Get available models from Ollama
    available_models = []
    current_model = Config.OLLAMA_MODEL
    try:
        import requests
        r = requests.get(f"{Config.OLLAMA_HOST}/api/tags", timeout=5)
        if r.status_code == 200:
            data = r.json()
            available_models = [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        pass
    
    # Get watch folders from .env
    watch_folders = []
    env_path = Config.BASE_DIR / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if line.strip().startswith("WATCH_FOLDERS="):
                    value = line.split("=", 1)[1].strip()
                    if value:
                        watch_folders = [f.strip() for f in value.split(",") if f.strip()]
                    break
    
    return render_template(
        "settings.html", 
        backups=backups,
        available_models=available_models,
        current_model=current_model,
        watch_folders=watch_folders
    )


@app.route("/settings/add-watch-folder", methods=["POST"])
@login_required
def add_watch_folder():
    import os
    from pathlib import Path
    
    data = request.get_json()
    folder_path = data.get("path", "").strip()
    
    if not folder_path:
        return jsonify({"status": "error", "message": "Path cannot be empty"})
    
    # Expand user path (e.g., ~/Downloads)
    folder_path = os.path.expanduser(folder_path)
    
    # Validate path exists
    if not os.path.exists(folder_path):
        return jsonify({"status": "error", "message": "Folder does not exist"})
    
    if not os.path.isdir(folder_path):
        return jsonify({"status": "error", "message": "Path is not a directory"})
    
    # Read .env file
    env_path = Config.BASE_DIR / ".env"
    if not env_path.exists():
        return jsonify({"status": "error", "message": ".env file not found"})
    
    with open(env_path, "r") as f:
        lines = f.readlines()
    
    # Find or create WATCH_FOLDERS line
    found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("WATCH_FOLDERS="):
            existing = line.split("=", 1)[1].strip()
            if existing:
                folders = [f.strip() for f in existing.split(",")]
                # Normalize path for comparison
                normalized = str(Path(folder_path).resolve())
                if normalized not in [str(Path(f).resolve()) for f in folders]:
                    folders.append(folder_path)
                    line = "WATCH_FOLDERS=" + ",".join(folders) + "\n"
                else:
                    return jsonify({"status": "error", "message": "Folder already in watch list"})
            else:
                line = f"WATCH_FOLDERS={folder_path}\n"
            found = True
        new_lines.append(line)
    
    if not found:
        new_lines.append(f"WATCH_FOLDERS={folder_path}\n")
    
    # Write back
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    
    return jsonify({"status": "success", "message": "Folder added to watch list"})


@app.route("/api/models", methods=["GET"])
@login_required
def api_get_models():
    """Get available Ollama models"""
    import requests
    try:
        r = requests.get(f"{Config.OLLAMA_HOST}/api/tags", timeout=10)
        if r.status_code == 200:
            data = r.json()
            models = [{"name": m.get("name", ""), "size": m.get("size", 0)} for m in data.get("models", [])]
            return jsonify({"status": "success", "models": models, "current": Config.OLLAMA_MODEL})
        return jsonify({"status": "error", "message": "Failed to fetch models"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/models/pull", methods=["POST"])
@login_required
def api_pull_model():
    """Pull a new Ollama model"""
    import requests
    data = request.json
    model_name = data.get("model", "").strip()
    
    if not model_name:
        return jsonify({"status": "error", "message": "Model name required"})
    
    try:
        r = requests.post(
            f"{Config.OLLAMA_HOST}/api/pull",
            json={"name": model_name},
            timeout=300
        )
        if r.status_code == 200:
            return jsonify({"status": "success", "message": f"Model '{model_name}' pulled successfully"})
        return jsonify({"status": "error", "message": "Failed to pull model"})
    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "message": "Model pull timed out"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/models/set", methods=["POST"])
@login_required
def api_set_model():
    """Set the active Ollama model"""
    data = request.json
    model_name = data.get("model", "").strip()
    
    if not model_name:
        return jsonify({"status": "error", "message": "Model name required"})
    
    # Update .env file
    env_path = Config.BASE_DIR / ".env"
    env_content = env_path.read_text() if env_path.exists() else ""
    
    # Update or add OLLAMA_MODEL
    if "OLLAMA_MODEL=" in env_content:
        import re
        env_content = re.sub(r"OLLAMA_MODEL=.*", f"OLLAMA_MODEL={model_name}", env_content)
    else:
        env_content += f"\nOLLAMA_MODEL={model_name}\n"
    
    env_path.write_text(env_content)
    
    return jsonify({"status": "success", "message": f"Model set to '{model_name}'"})


# ═══════════════════════════════════════
# FEEDBACK API (Learning)
# ═══════════════════════════════════════


@app.route("/api/feedback", methods=["POST"])
@login_required
@rate_limit_api()
def submit_feedback():
    """Submit feedback on AI action"""
    p = get_pilot()
    data = request.json

    p.memory.record_feedback(
        action_type=data.get("action_type", ""),
        detail=data.get("detail", ""),
        ai_output=data.get("ai_output", ""),
        feedback=data.get("feedback", ""),
        correction=data.get("correction"),
        context=data.get("context"),
    )

    return jsonify({"status": "recorded"})


# ═══════════════════════════════════════
# 2FA SETUP ROUTES
# ═══════════════════════════════════════


@app.route("/api/2fa/setup", methods=["POST"])
@login_required
def setup_2fa():
    """Generate 2FA secret for setup"""
    try:
        from security.auth import TwoFactorError

        p = get_pilot()
        secret, qr_url = p.auth.generate_2fa_secret()
        return jsonify({"secret": secret, "qr_url": qr_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/2fa/enable", methods=["POST"])
@login_required
def enable_2fa():
    """Complete 2FA setup"""
    try:
        from security.auth import TwoFactorError

        p = get_pilot()
        data = request.json
        secret = data.get("secret", "")
        token = data.get("token", "")

        p.auth.setup_2fa(secret, token)
        return jsonify({"status": "2FA enabled"})
    except TwoFactorError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/2fa/disable", methods=["POST"])
@login_required
def disable_2fa():
    """Disable 2FA"""
    try:
        from security.auth import TwoFactorError

        p = get_pilot()
        data = request.json
        password = data.get("password", "")
        token = data.get("token", "")

        p.auth.disable_2fa(password, token)
        return jsonify({"status": "2FA disabled"})
    except (AuthError, TwoFactorError) as e:
        return jsonify({"error": str(e)}), 400


# ═══════════════════════════════════════
# RUN
# ═══════════════════════════════════════


def start_dashboard():
    """Start the web dashboard"""
    print(f"\n🌐 Dashboard: http://{Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}")
    app.run(host=Config.DASHBOARD_HOST, port=Config.DASHBOARD_PORT, debug=False)


if __name__ == "__main__":
    start_dashboard()
