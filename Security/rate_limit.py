"""
AI Office Pilot - Rate Limiting Middleware
Dashboard API rate limiting with configurable limits
"""

import os
import time
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps

from flask import request, jsonify


class RateLimiter:
    """
    Token bucket rate limiter for API endpoints

    Supports:
    - Per-IP limiting
    - Per-endpoint limiting
    - Burst handling
    - Configurable via environment variables
    """

    def __init__(
        self,
        requests_per_minute: Optional[int] = None,
        burst_size: Optional[int] = None,
        unauthenticated_limit: Optional[int] = None
    ):
        # Load from environment variables with defaults
        self.requests_per_minute = requests_per_minute or int(
            os.getenv("RATE_LIMIT_PER_MINUTE", "60")
        )
        self.burst_size = burst_size or int(
            os.getenv("RATE_LIMIT_BURST", "10")
        )
        self.unauthenticated_limit = unauthenticated_limit or int(
            os.getenv("RATE_LIMIT_UNAUTHENTICATED", "10")
        )
        self._buckets: dict[str, dict] = defaultdict(self._create_bucket)

    def _create_bucket(self) -> dict:
        """Create a new token bucket"""
        return {"tokens": self.burst_size, "last_refill": time.time()}

    def _refill_bucket(self, bucket: dict) -> None:
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - bucket["last_refill"]
        tokens_to_add = elapsed * (self.requests_per_minute / 60.0)
        bucket["tokens"] = min(self.burst_size, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

    def is_allowed(self, key: str) -> tuple[bool, dict]:
        """
        Check if request is allowed

        Returns: (allowed: bool, info: dict)
        """
        bucket = self._buckets[key]
        self._refill_bucket(bucket)

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, {"allowed": True, "remaining": int(bucket["tokens"]), "reset_in": 60}
        else:
            return False, {"allowed": False, "remaining": 0, "reset_in": 60, "retry_after": 60}

    def get_identifier(self, request) -> str:
        """Get identifier for rate limiting (IP by default)"""
        # Use X-Forwarded-For if available
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.remote_addr or "unknown"


# Global rate limiters for different endpoints
_api_limiter = RateLimiter(requests_per_minute=60, burst_size=10)
_auth_limiter = RateLimiter(requests_per_minute=10, burst_size=3)
_status_limiter = RateLimiter(requests_per_minute=120, burst_size=20)


def rate_limit(limiter: Optional[RateLimiter] = None, key_func=None):
    """
    Decorator to apply rate limiting to endpoints

    Usage:
        @rate_limit()  # Uses default API limiter
        @rate_limit(limiter=_auth_limiter)  # Use specific limiter
        @rate_limit(key_func=lambda req: req.user.id)  # Custom key
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limit = limiter or _api_limiter

            if key_func:
                identifier = key_func(request)
            else:
                identifier = limit.get_identifier(request)

            allowed, info = limit.is_allowed(identifier)

            response = f(*args, **kwargs)

            # Add rate limit headers
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
                response.headers["X-RateLimit-Limit"] = str(limit.requests_per_minute)
                if "retry_after" in info:
                    response.headers["Retry-After"] = str(info["retry_after"])

            if not allowed:
                return jsonify(
                    {"error": "Rate limit exceeded", "retry_after": info["retry_after"]}
                ), 429

            return response

        return decorated_function

    return decorator


def rate_limit_auth():
    """Rate limit for authentication endpoints"""
    return rate_limit(limiter=_auth_limiter)


def rate_limit_api():
    """Rate limit for general API endpoints"""
    return rate_limit(limiter=_api_limiter)


def rate_limit_status():
    """Rate limit for status/metrics endpoints"""
    return rate_limit(limiter=_status_limiter)
