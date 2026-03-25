"""
Dashboard Authentication Module
"""

import jwt
import datetime
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
import os

from core.config import Config


def get_db_connection():
    """Get SQLite database connection"""
    data_dir = Path(Config.DATA_DIR)
    db_path = data_dir / "dashboard.db"

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    """Initialize authentication database"""
    conn = get_db_connection()

    # Create users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    """)

    # Create sessions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Create default admin user if none exists
    cursor = conn.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()["count"] == 0:
        password_hash = generate_password_hash("admin")
        conn.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            ("admin", password_hash, "admin@localhost"),
        )

    conn.commit()
    conn.close()


def create_session_token(user_id: int, expires_hours: int = 24) -> str:
    """Create JWT session token"""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
    }

    # Use secret from config or fallback
    secret = getattr(Config, "JWT_SECRET", "fallback-secret-key-change-in-production")
    token = jwt.encode(payload, secret, algorithm="HS256")

    # Store session in database
    conn = get_db_connection()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours)

    conn.execute(
        "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)",
        (user_id, token, expires_at),
    )
    conn.commit()
    conn.close()

    return token


def verify_session_token(token: str) -> dict:
    """Verify JWT session token"""
    try:
        secret = getattr(Config, "JWT_SECRET", "fallback-secret-key-change-in-production")
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        # Check if session exists in database
        conn = get_db_connection()
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE session_token = ? AND expires_at > datetime('now')",
            (token,),
        )
        session_data = cursor.fetchone()
        conn.close()

        if session_data:
            return payload
        else:
            return None
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def login_required(f):
    """Decorator to require authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("session_token") or session.get("session_token")

        if not token:
            if request.accept_mimetypes.accept_json:
                return jsonify({"error": "Authentication required"}), 401
            else:
                return redirect(url_for("login"))

        payload = verify_session_token(token)
        if not payload:
            if request.accept_mimetypes.accept_json:
                return jsonify({"error": "Invalid or expired session"}), 401
            else:
                return redirect(url_for("login"))

        # Add user info to request context
        request.user_id = payload["user_id"]
        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    """Get current user from session"""
    token = request.cookies.get("session_token") or session.get("session_token")
    if token:
        payload = verify_session_token(token)
        if payload:
            conn = get_db_connection()
            user = conn.execute(
                "SELECT * FROM users WHERE id = ?", (payload["user_id"],)
            ).fetchone()
            conn.close()
            return user
    return None
