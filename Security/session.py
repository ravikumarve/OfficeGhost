"""
AI Office Pilot - Session Management
Token-based authentication with refresh tokens
"""

import secrets
import time
import logging
from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """User session data"""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    refresh_token: str
    last_activity: datetime
    ip_address: Optional[str] = None


class SessionError(Exception):
    """Session-related errors"""
    pass


class SessionManager:
    """Manage user sessions with refresh tokens"""

    # Token lifetimes (in seconds)
    ACCESS_TOKEN_LIFETIME = 3600  # 1 hour
    REFRESH_TOKEN_LIFETIME = 604800  # 7 days

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Create a new session
        Returns: (access_token, refresh_token)
        """
        session_id = self._generate_token()
        refresh_token = self._generate_token()

        now = datetime.now()
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(seconds=self.ACCESS_TOKEN_LIFETIME),
            refresh_token=refresh_token,
            last_activity=now,
            ip_address=ip_address
        )

        self._sessions[session_id] = session
        logger.info(f"Created session for user {user_id}")

        return session_id, refresh_token

    def validate_session(self, session_id: str) -> Optional[str]:
        """
        Validate session and return user_id if valid
        Returns user_id or None if invalid/expired
        """
        session = self._sessions.get(session_id)

        if not session:
            return None

        if datetime.now() > session.expires_at:
            self._sessions.pop(session_id, None)
            logger.info(f"Session expired: {session_id}")
            return None

        # Update last activity
        session.last_activity = datetime.now()
        session.expires_at = datetime.now() + timedelta(
            seconds=self.ACCESS_TOKEN_LIFETIME
        )

        return session.user_id

    def refresh_session(self, refresh_token: str) -> Optional[tuple[str, str]]:
        """
        Refresh session using refresh token
        Returns: (new_access_token, new_refresh_token) or None
        """
        # Find session by refresh token
        session = None
        for s in self._sessions.values():
            if s.refresh_token == refresh_token:
                session = s
                break

        if not session:
            return None

        # Check if refresh token is expired
        if datetime.now() > session.created_at + timedelta(
            seconds=self.REFRESH_TOKEN_LIFETIME
        ):
            self._sessions.pop(session.session_id, None)
            logger.info(f"Refresh token expired for session {session.session_id}")
            return None

        # Generate new tokens
        new_session_id = self._generate_token()
        new_refresh_token = self._generate_token()

        now = datetime.now()

        # Create new session
        new_session = Session(
            session_id=new_session_id,
            user_id=session.user_id,
            created_at=now,
            expires_at=now + timedelta(seconds=self.ACCESS_TOKEN_LIFETIME),
            refresh_token=new_refresh_token,
            last_activity=now,
            ip_address=session.ip_address
        )

        # Remove old session and add new
        self._sessions.pop(session.session_id, None)
        self._sessions[new_session_id] = new_session

        logger.info(f"Refreshed session for user {session.user_id}")
        return new_session_id, new_refresh_token

    def revoke_session(self, session_id: str) -> bool:
        """Revoke a session"""
        if session_id in self._sessions:
            self._sessions.pop(session_id, None)
            logger.info(f"Revoked session: {session_id}")
            return True
        return False

    def revoke_all_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user"""
        to_remove = [
            sid for sid, s in self._sessions.items() if s.user_id == user_id
        ]
        for sid in to_remove:
            self._sessions.pop(sid, None)

        logger.info(f"Revoked {len(to_remove)} sessions for user {user_id}")
        return len(to_remove)

    def get_active_sessions(self, user_id: str) -> list[dict]:
        """Get all active sessions for a user"""
        sessions = []
        for s in self._sessions.values():
            if s.user_id == user_id and datetime.now() <= s.expires_at:
                sessions.append({
                    "session_id": s.session_id[:8] + "...",
                    "created": s.created_at.isoformat(),
                    "last_activity": s.last_activity.isoformat(),
                    "ip": s.ip_address
                })
        return sessions

    def cleanup_expired(self) -> int:
        """Remove expired sessions"""
        now = datetime.now()
        to_remove = [
            sid for sid, s in self._sessions.items() if now > s.expires_at
        ]
        for sid in to_remove:
            self._sessions.pop(sid, None)

        return len(to_remove)

    def _generate_token(self) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)

    def get_status(self) -> dict:
        """Get session manager status"""
        return {
            "total_sessions": len(self._sessions),
            "active_users": len(set(s.user_id for s in self._sessions.values() 
                if datetime.now() <= s.expires_at))
        }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager