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
# MAIN DASHBOARD
# ═══════════════════════════════════════


@app.route("/")
def index():
    """Landing page - shows for everyone"""
    if session.get("authenticated"):
        return redirect("/dashboard")
    return render_template("landing.html")


@app.route("/dashboard")
@login_required
def dashboard():
    p = get_pilot()
    status = p.get_status()
    return render_template("index.html", status=status)


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
    return render_template(
        "security.html", security=sec_status, compliance=compliance, audit=audit_entries
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
    return render_template("settings.html", backups=backups)


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
