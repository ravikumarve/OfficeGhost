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
    # Check for DATA_DIR environment variable first (for testing)
    data_dir_path = os.getenv("DATA_DIR")
    if data_dir_path:
        data_dir = Path(data_dir_path)
    else:
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
            last_login DATETIME,
            requires_password_change BOOLEAN DEFAULT 0
        )
    """)

    # Check if requires_password_change column exists, add if missing
    cursor = conn.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "requires_password_change" not in columns:
        print("🔄 Adding requires_password_change column to users table...")
        conn.execute("ALTER TABLE users ADD COLUMN requires_password_change BOOLEAN DEFAULT 0")
        conn.commit()

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
        # Generate secure random password for first-time setup
        import secrets
        default_password = secrets.token_urlsafe(16)
        password_hash = generate_password_hash(default_password)
        
        # Mark user as requiring password change on first login
        conn.execute(
            "INSERT INTO users (username, password_hash, email, requires_password_change) VALUES (?, ?, ?, ?)",
            ("admin", password_hash, "admin@localhost", True),
        )
        
        # Log the temporary password for setup
        print("\n" + "="*60)
        print("🔐 FIRST-TIME SETUP - TEMPORARY ADMIN PASSWORD")
        print("="*60)
        print(f"Username: admin")
        print(f"Temporary Password: {default_password}")
        print("="*60)
        print("⚠️  IMPORTANT: Change this password on first login!")
        print("="*60 + "\n")

    conn.commit()
    conn.close()


def create_session_token(user_id: int, expires_hours: int = 24) -> str:
    """Create JWT session token"""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
    }

    # Require JWT_SECRET from environment - no fallback for security
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise ValueError(
            "JWT_SECRET environment variable must be set. "
            "Generate a secure random key: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
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
        # Require JWT_SECRET from environment - no fallback for security
        secret = os.getenv("JWT_SECRET")
        if not secret:
            raise ValueError(
                "JWT_SECRET environment variable must be set. "
                "Generate a secure random key: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
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


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength requirements"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not (has_upper and has_lower):
        return False, "Password must contain both uppercase and lowercase letters"
    
    if not has_digit:
        return False, "Password must contain at least one digit"
    
    if not has_special:
        return False, "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    
    return True, "Password meets strength requirements"


def change_password(user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
    """Change user password with validation"""
    conn = get_db_connection()
    
    # Get current user
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return False, "User not found"
    
    # Verify old password
    if not check_password_hash(user["password_hash"], old_password):
        conn.close()
        return False, "Current password is incorrect"
    
    # Validate new password strength
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        conn.close()
        return False, message
    
    # Update password
    new_password_hash = generate_password_hash(new_password)
    conn.execute(
        "UPDATE users SET password_hash = ?, requires_password_change = 0 WHERE id = ?",
        (new_password_hash, user_id)
    )
    conn.commit()
    conn.close()
    
    return True, "Password changed successfully"


def force_password_change_required(user_id: int) -> bool:
    """Check if user is required to change password"""
    conn = get_db_connection()
    user = conn.execute("SELECT requires_password_change FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        # Convert Row to dict for access
        user_dict = dict(user)
        return user_dict.get("requires_password_change", False)
    return False
