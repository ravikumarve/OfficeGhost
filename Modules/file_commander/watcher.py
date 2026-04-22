"""
AI Office Pilot - File Watcher
Monitor folders for new files
"""

import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from core.config import Config

logger = logging.getLogger(__name__)


class FileWatcher:
    """Watch folders for new files"""

    FILE_STABILITY_DELAY = 0.5

    def __init__(self) -> None:
        self.known_files: set[str] = set()
        self._scan_existing()

    def _scan_existing(self) -> None:
        """Record existing files on startup"""
        for folder in Config.WATCH_FOLDERS:
            folder_path = Path(folder)
            if folder_path.exists():
                for f in folder_path.iterdir():
                    if f.is_file() and not f.name.startswith("."):
                        self.known_files.add(str(f))

    def scan_new(self) -> list[dict]:
        """Scan for new files since last check"""
        new_files: list[dict] = []

        for folder in Config.WATCH_FOLDERS:
            folder_path = Path(folder)
            if not folder_path.exists():
                continue

            for f in folder_path.iterdir():
                if f.is_file() and not f.name.startswith("."):
                    file_str = str(f)
                    if file_str not in self.known_files:
                        try:
                            size1 = f.stat().st_size
                            time.sleep(self.FILE_STABILITY_DELAY)
                            size2 = f.stat().st_size

                            if size1 == size2 and size1 > 0:
                                new_files.append(
                                    {
                                        "path": str(f),
                                        "name": f.name,
                                        "extension": f.suffix.lower(),
                                        "size": size2,
                                        "modified": datetime.fromtimestamp(
                                            f.stat().st_mtime
                                        ).isoformat(),
                                        "source_folder": folder,
                                    }
                                )
                                self.known_files.add(file_str)
                        except OSError as e:
                            logger.warning(f"Error accessing file {file_path}: {e}")
                            continue

        return new_files[: Config.MAX_FILES_PER_CYCLE]
