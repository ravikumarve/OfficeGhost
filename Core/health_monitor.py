"""
AI Office Pilot - System Health Monitor
"""

import shutil
import logging
from typing import Optional
import psutil

from core.config import Config
from core.retry import retry_requests

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitor system resources and service health"""

    RAM_WARNING_THRESHOLD = 85
    RAM_GREEN_THRESHOLD = 80
    RAM_YELLOW_THRESHOLD = 90
    DISK_WARNING_GB = 5
    DISK_GREEN_GB = 10
    DISK_YELLOW_GB = 5
    REQUEST_TIMEOUT = 5

    def check_all(self) -> dict:
        """Run all health checks"""
        return {
            "ram": self.check_ram(),
            "disk": self.check_disk(),
            "ollama": self.check_ollama(),
            "overall": self._overall_status(),
        }

    def check_ram(self) -> dict:
        """Check RAM usage"""
        mem = psutil.virtual_memory()
        percent = mem.percent
        return {
            "total_gb": round(mem.total / (1024**3), 1),
            "used_gb": round(mem.used / (1024**3), 1),
            "available_gb": round(mem.available / (1024**3), 1),
            "percent": percent,
            "status": "🟢"
            if percent < self.RAM_GREEN_THRESHOLD
            else "🟡"
            if percent < self.RAM_YELLOW_THRESHOLD
            else "🔴",
            "warning": percent > self.RAM_WARNING_THRESHOLD,
        }

    def check_disk(self) -> dict:
        """Check disk space"""
        usage = shutil.disk_usage(Config.DATA_DIR)
        free_gb = usage.free / (1024**3)
        total_gb = usage.total / (1024**3)
        percent = (usage.used / usage.total) * 100

        return {
            "total_gb": round(total_gb, 1),
            "free_gb": round(free_gb, 1),
            "percent_used": round(percent, 1),
            "status": "🟢"
            if free_gb > self.DISK_GREEN_GB
            else "🟡"
            if free_gb > self.DISK_YELLOW_GB
            else "🔴",
            "warning": free_gb < self.DISK_WARNING_GB,
        }

    @retry_requests(max_retries=3, base_delay=1.0)
    def check_ollama(self) -> dict:
        """Check if Ollama is running"""
        try:
            import requests

            r = requests.get(f"{Config.OLLAMA_HOST}/api/tags", timeout=self.REQUEST_TIMEOUT)
            if r.status_code == 200:
                models = r.json().get("models", [])
                return {"running": True, "models_loaded": len(models), "status": "🟢"}
        except Exception:
            pass

        return {
            "running": False,
            "models_loaded": 0,
            "status": "🔴",
            "error": "Ollama not running. Start with: ollama serve",
        }

    def _overall_status(self) -> str:
        """Overall system health"""
        ram = self.check_ram()
        disk = self.check_disk()
        ollama = self.check_ollama()

        if not ollama["running"]:
            return "🔴 OLLAMA DOWN"
        if ram["warning"] or disk["warning"]:
            return "🟡 RESOURCE WARNING"
        return "🟢 ALL SYSTEMS GO"
