"""
AI Office Pilot - File Sorter
Move files to organized folders
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from core.config import Config


class FileSorter:
    """Sort files into organized folder structure"""

    def get_destination(self, category: str) -> str:
        """Get destination folder for a category"""
        subfolder = Config.CATEGORY_FOLDERS.get(category, "Other")
        year = datetime.now().strftime("%Y")
        dest = Path(Config.ORGANIZED_ROOT) / subfolder / year
        dest.mkdir(parents=True, exist_ok=True)
        return str(dest)

    def move_file(
        self, source_path: str, destination_dir: str, new_name: Optional[str] = None
    ) -> str:
        """Move file to destination with optional rename"""
        source = Path(source_path)
        dest_dir = Path(destination_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)

        filename = new_name if new_name else source.name

        dest_path = dest_dir / filename
        if dest_path.exists():
            stem = dest_path.stem
            suffix = dest_path.suffix
            counter = 1
            while dest_path.exists():
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        shutil.move(str(source), str(dest_path))
        return str(dest_path)

    def rename_file(self, file_path: str, new_name: str) -> str:
        """Rename a file in place"""
        source = Path(file_path)
        dest = source.parent / new_name
        source.rename(dest)
        return str(dest)
