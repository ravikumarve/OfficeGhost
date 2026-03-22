"""Tests for QueueManager class"""

import pytest
from core.queue_manager import QueueManager, Task, Priority


class TestTask:
    """Test cases for Task"""

    def test_init(self):
        """Test Task initialization"""
        task = Task("email_process", {"test": "data"}, Priority.HIGH)

        assert task.task_type == "email_process"
        assert task.data == {"test": "data"}
        assert task.priority == Priority.HIGH
        assert task.status == "pending"
        assert task.result is None
        assert task.error is None

    def test_lt(self):
        """Test task comparison"""
        low_task = Task("test", {}, Priority.LOW)
        high_task = Task("test", {}, Priority.HIGH)

        # Higher priority (lower number) should be less than
        assert high_task < low_task


class TestQueueManager:
    """Test cases for QueueManager"""

    def test_init(self):
        """Test QueueManager initialization"""
        queue = QueueManager()

        assert queue.size() == 0
        assert isinstance(queue._queue, list)

    def test_add(self):
        """Test adding tasks"""
        queue = QueueManager()

        task_id = queue.add("email_process", {"email": "test"})

        assert task_id is not None
        assert queue.size() == 1

    def test_get_next(self):
        """Test getting highest priority task"""
        queue = QueueManager()

        # Add tasks with different priorities
        queue.add("low_priority", {"data": 1}, Priority.LOW)
        queue.add("high_priority", {"data": 2}, Priority.HIGH)

        task = queue.get_next()

        # High priority (lower number) should come first
        assert task.task_type == "high_priority"
        assert task.status == "processing"

    def test_get_next_empty(self):
        """Test getting from empty queue"""
        queue = QueueManager()

        task = queue.get_next()

        assert task is None

    def test_complete(self):
        """Test marking task complete"""
        queue = QueueManager()

        task_id = queue.add("test", {"data": 1})
        task = queue.get_next()

        queue.complete(task, {"result": "success"})

        assert task.status == "completed"
        assert task.result == {"result": "success"}
        assert queue.stats()["completed"] == 1

    def test_fail(self):
        """Test marking task failed - with retry logic"""
        queue = QueueManager()

        task_id = queue.add("test", {"data": 1})
        task = queue.get_next()

        # First failure - task goes back to queue for retry
        queue.fail(task, ValueError("Test error"))

        assert task.status == "failed"
        assert task.retry_count == 1
        assert task.error == "Test error"

        # Second failure - task goes back to queue
        task = queue.get_next()
        queue.fail(task, ValueError("Test error"))

        # Third failure - task moves to dead letter
        task = queue.get_next()
        queue.fail(task, ValueError("Test error"))

        assert queue.stats()["failed"] == 1
        assert queue.stats()["dead_letter"] == 1

    def test_stats(self):
        """Test queue statistics"""
        queue = QueueManager()

        # Add some tasks
        queue.add("task1", {}, Priority.NORMAL)
        queue.add("task2", {}, Priority.NORMAL)

        # Complete one
        task = queue.get_next()
        queue.complete(task)

        stats = queue.stats()

        assert stats["pending"] == 1
        assert stats["completed"] == 1
        assert stats["failed"] == 0

    def test_priority_ordering(self):
        """Test that priority queue maintains order"""
        queue = QueueManager()

        # Add in random order
        queue.add("critical", {}, Priority.CRITICAL)
        queue.add("normal", {}, Priority.NORMAL)
        queue.add("high", {}, Priority.HIGH)
        queue.add("low", {}, Priority.LOW)

        tasks = []
        while True:
            task = queue.get_next()
            if task is None:
                break
            tasks.append(task.task_type)

        # Should be ordered: critical, high, normal, low
        assert tasks == ["critical", "high", "normal", "low"]

    def test_thread_safety(self):
        """Test that operations are thread-safe"""
        import threading

        queue = QueueManager()

        def add_tasks():
            for i in range(100):
                queue.add(f"task_{i}", {"i": i})

        threads = [threading.Thread(target=add_tasks) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All tasks should be added
        assert queue.size() == 500
