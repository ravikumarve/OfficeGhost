"""
AI Office Pilot - Retry Utilities
Exponential backoff retry logic for network operations
"""

import time
import logging
from functools import wraps
from typing import Callable, TypeVar, Any, Optional

import requests
import smtplib
import imaplib

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryError(Exception):
    """Retry-related errors"""

    pass


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retriable_exceptions: tuple = (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.ChunkedEncodingError,
        smtplib.SMTPException,
        imaplib.IMAP4.error,
    ),
):
    """
    Decorator for retrying functions with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential calculation
        retriable_exceptions: Tuple of exceptions that trigger retry
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retriable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {func.__name__} - {e}")
                        raise

                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.1f}s: {e}"
                    )
                    time.sleep(delay)

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            raise RetryError(f"Unknown error in {func.__name__}")

        return wrapper

    return decorator


def retry_requests(
    max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0
) -> Callable:
    """Decorator specifically for requests operations"""
    return retry_with_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        retriable_exceptions=(
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.RequestException,
        ),
    )


def retry_smtp(max_retries: int = 3, base_delay: float = 2.0, max_delay: float = 60.0) -> Callable:
    """Decorator specifically for SMTP operations"""
    return retry_with_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        retriable_exceptions=(smtplib.SMTPException,),
    )


def retry_imap(max_retries: int = 3, base_delay: float = 2.0, max_delay: float = 60.0) -> Callable:
    """Decorator specifically for IMAP operations"""
    return retry_with_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        retriable_exceptions=(imaplib.IMAP4.error,),
    )
