"""
AI Office Pilot - Threat Detection
Real-time security monitoring
"""

from datetime import datetime, timedelta
from collections import defaultdict

from security.audit import AuditLogger


class ThreatDetector:
    """
    Monitors for suspicious activity in real-time

    Rules:
    - Bulk data access detection
    - After-hours access alerts
    - External connection blocking
    - Anomaly detection
    """

    def __init__(self, audit: AuditLogger):
        self.audit = audit
        self.activity = defaultdict(list)
        self.alerts = []

        # Thresholds
        self.rules = {
            "bulk_email": {"limit": 100, "window_min": 5},
            "bulk_file": {"limit": 50, "window_min": 5},
            "normal_hours": {"start": 6, "end": 23},
        }

    def check(self, action_type, detail=None):
        """
        Check action against security rules
        Returns: (allowed: bool, reason: str)
        """
        now = datetime.now()

        # Track activity
        self.activity[action_type].append(now)

        # Clean old entries (keep 30 min)
        cutoff = now - timedelta(minutes=30)
        self.activity[action_type] = [t for t in self.activity[action_type] if t > cutoff]

        # Check bulk email access
        if action_type == "email_access":
            rule = self.rules["bulk_email"]
            window = timedelta(minutes=rule["window_min"])
            recent = [t for t in self.activity["email_access"] if t > now - window]
            if len(recent) > rule["limit"]:
                self._alert(
                    "BULK_EMAIL_ACCESS", f"{len(recent)} emails in {rule['window_min']}min", "high"
                )
                return False, "Bulk email access blocked"

        # Check bulk file access
        if action_type == "file_access":
            rule = self.rules["bulk_file"]
            window = timedelta(minutes=rule["window_min"])
            recent = [t for t in self.activity["file_access"] if t > now - window]
            if len(recent) > rule["limit"]:
                self._alert(
                    "BULK_FILE_ACCESS", f"{len(recent)} files in {rule['window_min']}min", "high"
                )
                return False, "Bulk file access blocked"

        # Block external connections
        if action_type == "external_connection":
            self._alert("EXTERNAL_CONNECTION_BLOCKED", f"Attempted: {detail}", "critical")
            return False, "External connections blocked"

        # After-hours warning
        hours = self.rules["normal_hours"]
        if now.hour < hours["start"] or now.hour > hours["end"]:
            self._alert("AFTER_HOURS", f"Access at {now.strftime('%H:%M')}", "low")

        return True, "OK"

    def check_network(self):
        """Check for unauthorized network connections"""
        import socket

        suspicious = []
        test_hosts = [
            ("api.openai.com", 443),
            ("api.anthropic.com", 443),
            ("api.cohere.com", 443),
        ]

        for host, port in test_hosts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    suspicious.append(host)
            except Exception:
                pass  # Can't reach = good

        return {"isolated": len(suspicious) == 0, "reachable_hosts": suspicious}

    def get_status(self):
        """Current security status"""
        network = self.check_network()
        recent_alerts = [
            a
            for a in self.alerts
            if datetime.fromisoformat(a["timestamp"]) > datetime.now() - timedelta(hours=24)
        ]

        if not network["isolated"]:
            overall = "🟡 PARTIALLY SECURE"
        elif recent_alerts:
            overall = "🟡 ALERTS PRESENT"
        else:
            overall = "🟢 FULLY SECURE"

        return {
            "overall": overall,
            "network_isolated": network["isolated"],
            "reachable_hosts": network["reachable_hosts"],
            "recent_alerts": len(recent_alerts),
            "alerts": recent_alerts[-10:],
        }

    def _alert(self, alert_type, detail, severity):
        """Create security alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "detail": detail,
            "severity": severity,
        }
        self.alerts.append(alert)

        self.audit.log_security(alert_type, detail, severity)

        return alert
