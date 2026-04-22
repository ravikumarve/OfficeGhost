"""
AI Office Pilot - Task Queue Manager
Priority-based task processing with dead letter queue
"""

import heapq
import logging
from datetime import datetime
from threading import Lock
from enum import IntEnum
from typing import Any, Optional, List

logger = logging.getLogger(__name__)


class Priority(IntEnum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class Task:
    MAX_RETRIES = 3

    def __init__(self, task_type: str, data: Any, priority: Priority = Priority.NORMAL) -> None:
        self.id = f"{datetime.now().strftime('%H%M%S')}-{id(self) % 10000}"
        self.task_type = task_type
        self.data = data
        self.priority = priority
        self.created = datetime.now()
        self.status = "pending"
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.retry_count = 0
        self.failed_at: Optional[datetime] = None

    def __lt__(self, other: "Task") -> bool:
        return self.priority < other.priority

    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < self.MAX_RETRIES


class DeadLetterTask:
    """Wrapper for tasks in dead letter queue"""

    def __init__(self, task: Task, original_error: str) -> None:
        self.task = task
        self.original_error = original_error
        self.added_at = datetime.now()
        self.retry_count = 0
        self.last_attempt: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for display"""
        return {
            "id": self.task.id,
            "type": self.task.task_type,
            "priority": self.task.priority.name,
            "created": self.task.created.isoformat(),
            "error": self.original_error,
            "retry_count": self.retry_count,
            "added_at": self.added_at.isoformat(),
        }


class QueueManager:
    """Thread-safe priority task queue with dead letter queue"""

    MAX_DEAD_LETTER_SIZE = 1000

    def __init__(self) -> None:
        self._queue: list[Task] = []
        self._lock = Lock()
        self._completed: list[Task] = []
        self._failed: list[Task] = []
        self._dead_letter: List[DeadLetterTask] = []

    def add(self, task_type: str, data: Any, priority: Priority = Priority.NORMAL) -> str:
        """Add task to queue"""
        task = Task(task_type, data, priority)
        with self._lock:
            heapq.heappush(self._queue, task)
        logger.info(f"Task added to queue: {task.id} ({task_type})")
        return task.id

    def get_next(self) -> Optional[Task]:
        """Get highest priority task"""
        with self._lock:
            if self._queue:
                task = heapq.heappop(self._queue)
                task.status = "processing"
                return task
        return None

    def complete(self, task: Task, result: Optional[Any] = None) -> None:
        """Mark task as completed"""
        task.status = "completed"
        task.result = result
        with self._lock:
            self._completed.append(task)
        logger.info(f"Task completed: {task.id}")

    def fail(self, task: Task, error: Exception) -> None:
        """Mark task as failed"""
        task.status = "failed"
        task.error = str(error)
        task.failed_at = datetime.now()
        task.retry_count += 1

        if task.can_retry():
            logger.warning(
                f"Task failed (retry {task.retry_count}/{Task.MAX_RETRIES}): {task.id} - {error}"
            )
            with self._lock:
                heapq.heappush(self._queue, task)
        else:
            logger.error(f"Task moved to dead letter queue (max retries): {task.id} - {error}")
            self._add_to_dead_letter(task, str(error))

    def _add_to_dead_letter(self, task: Task, error: str) -> None:
        """Add failed task to dead letter queue"""
        dlt = DeadLetterTask(task, error)

        with self._lock:
            self._dead_letter.append(dlt)
            self._failed.append(task)

            # Trim if too large
            if len(self._dead_letter) > self.MAX_DEAD_LETTER_SIZE:
                self._dead_letter = self._dead_letter[-self.MAX_DEAD_LETTER_SIZE :]

    def get_dead_letter(self, limit: int = 100) -> List[dict]:
        """Get tasks from dead letter queue"""
        with self._lock:
            return [dlt.to_dict() for dlt in self._dead_letter[-limit:]]

    def retry_dead_letter(self, task_id: str) -> bool:
        """Retry a task from dead letter queue"""
        with self._lock:
            for dlt in self._dead_letter:
                if dlt.task.id == task_id:
                    dlt.task.status = "pending"
                    dlt.task.retry_count = 0
                    dlt.task.error = None
                    heapq.heappush(self._queue, dlt.task)
                    self._dead_letter.remove(dlt)
                    logger.info(f"Retried dead letter task: {task_id}")
                    return True
        return False

    def clear_dead_letter(self, older_than_days: int = 7) -> int:
        """Clear old tasks from dead letter queue"""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=older_than_days)
        removed = 0

        with self._lock:
            self._dead_letter = [dlt for dlt in self._dead_letter if dlt.added_at > cutoff]
            removed = len(self._dead_letter)

        logger.info(f"Cleared dead letter queue: {removed} tasks removed")
        return removed

    def size(self) -> int:
        """Current queue size"""
        with self._lock:
            return len(self._queue)

    def stats(self) -> dict:
        """Queue statistics"""
        with self._lock:
            return {
                "pending": len(self._queue),
                "completed": len(self._completed),
                "failed": len(self._failed),
                "dead_letter": len(self._dead_letter),
            }
