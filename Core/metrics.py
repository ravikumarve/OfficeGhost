"""
AI Office Pilot - Prometheus Metrics
Collects and exposes application metrics
"""

import time
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock

from core.config import Config


class Metrics:
    """Application metrics collector with Prometheus-compatible output"""

    _instance: Optional["Metrics"] = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_metrics()
        return cls._instance

    def _init_metrics(self) -> None:
        """Initialize metrics counters and gauges"""
        self.counters: dict[str, float] = defaultdict(float)
        self.gauges: dict[str, float] = {}
        self.histograms: dict[str, list[float]] = defaultdict(list)
        self._start_time = time.time()
        self._last_cycle_time: Optional[float] = None
        self._cycle_durations: list[float] = []

    def inc(self, name: str, value: float = 1.0) -> None:
        """Increment a counter"""
        self.counters[name] += value

    def set(self, name: str, value: float) -> None:
        """Set a gauge value"""
        self.gauges[name] = value

    def observe(self, name: str, value: float) -> None:
        """Observe a value for histogram"""
        self.histograms[name].append(value)
        # Keep only last 1000 observations
        if len(self.histograms[name]) > 1000:
            self.histograms[name] = self.histograms[name][-1000:]

    def cycle_completed(self, duration: float, emails: int, files: int, errors: int) -> None:
        """Record cycle completion metrics"""
        self._last_cycle_time = time.time()
        self._cycle_durations.append(duration)
        if len(self._cycle_durations) > 100:
            self._cycle_durations = self._cycle_durations[-100:]

        self.inc("pilot_cycles_total")
        self.inc("pilot_emails_processed_total", emails)
        self.inc("pilot_files_organized_total", files)
        self.inc("pilot_errors_total", errors)
        self.observe("pilot_cycle_duration_seconds", duration)

    def get_prometheus_output(self) -> str:
        """Generate Prometheus-compatible metrics output"""
        lines = []

        # Uptime
        uptime = time.time() - self._start_time
        lines.append(f"# HELP pilot_uptime_seconds Time since pilot started")
        lines.append(f"# TYPE pilot_uptime_seconds gauge")
        lines.append(f"pilot_uptime_seconds {uptime}")

        # Counters
        lines.append(f"# HELP pilot_emails_processed_total Total emails processed")
        lines.append(f"# TYPE pilot_emails_processed_total counter")
        lines.append(
            f"pilot_emails_processed_total {self.counters.get('pilot_emails_processed_total', 0)}"
        )

        lines.append(f"# HELP pilot_files_organized_total Total files organized")
        lines.append(f"# TYPE pilot_files_organized_total counter")
        lines.append(
            f"pilot_files_organized_total {self.counters.get('pilot_files_organized_total', 0)}"
        )

        lines.append(f"# HELP pilot_errors_total Total errors encountered")
        lines.append(f"# TYPE pilot_errors_total counter")
        lines.append(f"pilot_errors_total {self.counters.get('pilot_errors_total', 0)}")

        lines.append(f"# HELP pilot_cycles_total Total automation cycles completed")
        lines.append(f"# TYPE pilot_cycles_total counter")
        lines.append(f"pilot_cycles_total {self.counters.get('pilot_cycles_total', 0)}")

        # Gauges
        lines.append(f"# HELP pilot_queue_pending Number of pending tasks")
        lines.append(f"# TYPE pilot_queue_pending gauge")
        lines.append(f"pilot_queue_pending {self.gauges.get('pilot_queue_pending', 0)}")

        lines.append(f"# HELP pilot_memory_usage_bytes Current memory usage")
        lines.append(f"# TYPE pilot_memory_usage_bytes gauge")
        lines.append(f"pilot_memory_usage_bytes {self.gauges.get('pilot_memory_usage_bytes', 0)}")

        # Cycle duration histogram
        if self._cycle_durations:
            avg_duration = sum(self._cycle_durations) / len(self._cycle_durations)
            lines.append(f"# HELP pilot_cycle_duration_seconds Duration of automation cycles")
            lines.append(f"# TYPE pilot_cycle_duration_seconds summary")
            lines.append(f"pilot_cycle_duration_seconds_avg {avg_duration}")
            lines.append(f"pilot_cycle_duration_seconds_last {self._cycle_durations[-1]}")

        return "\n".join(lines) + "\n"

    def to_dict(self) -> dict:
        """Export metrics as dictionary"""
        return {
            "uptime_seconds": time.time() - self._start_time,
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                k: {
                    "count": len(v),
                    "avg": sum(v) / len(v) if v else 0,
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0,
                }
                for k, v in self.histograms.items()
            },
            "cycle_stats": {
                "total_cycles": self.counters.get("pilot_cycles_total", 0),
                "avg_duration": sum(self._cycle_durations) / len(self._cycle_durations)
                if self._cycle_durations
                else 0,
                "last_duration": self._cycle_durations[-1] if self._cycle_durations else 0,
            }
            if self._cycle_durations
            else None,
        }


# Convenience functions
def get_metrics() -> Metrics:
    """Get the metrics instance"""
    return Metrics()


def record_email_processed() -> None:
    """Record an email was processed"""
    get_metrics().inc("pilot_emails_processed_total")


def record_file_organized() -> None:
    """Record a file was organized"""
    get_metrics().inc("pilot_files_organized_total")


def record_error() -> None:
    """Record an error occurred"""
    get_metrics().inc("pilot_errors_total")


def record_cycle(emails: int, files: int, duration: float, errors: int = 0) -> None:
    """Record cycle completion"""
    get_metrics().cycle_completed(duration, emails, files, errors)
