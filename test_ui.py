#!/usr/bin/env python3
"""
Test script to verify brutalist UI templates work correctly
"""

from flask import Flask, render_template

app = Flask(__name__)


# Mock data for testing
def get_mock_status():
    return {
        "health": {"overall": "🟢 EXCELLENT", "ram": {"percent": 45}, "disk": {"free_gb": 128}},
        "cycles_completed": 42,
        "learning": {
            "learning_score": 78,
            "accuracy": {
                "email_reply": {"accuracy": 92},
                "file_categorize": {"accuracy": 85},
                "data_extract": {"accuracy": 88},
            },
            "contacts_learned": 15,
            "categories_learned": 8,
        },
        "queue": {"completed": 156, "pending": 3},
    }


@app.route("/")
def test_dashboard():
    status = get_mock_status()
    security_status = {"overall": "🟢 FULLY SECURE", "detail": "AES-256 ENCRYPTED"}

    activity = [
        {"timestamp": "2026-04-11T10:30:00", "detail": "PROCESSED 12 EMAILS"},
        {"timestamp": "2026-04-11T10:15:00", "detail": "SORTED 8 FILES"},
        {"timestamp": "2026-04-11T10:00:00", "detail": "EXTRACTED 5 DATA ENTRIES"},
    ]

    return render_template(
        "index.html",
        status=status,
        security_status=security_status,
        activity=activity,
        demo_mode=True,
    )


if __name__ == "__main__":
    app.run(port=5002, debug=True)
