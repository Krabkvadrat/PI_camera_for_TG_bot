import os
from datetime import datetime
from pathlib import Path
import logging
from config import (
    VIDEO_DIR, IMAGE_DIR, FILES_LIMIT_VIDEO, FILES_LIMIT_IMAGE,
    FILE_DATE_FORMAT
)

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self):
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        VIDEO_DIR.mkdir(exist_ok=True)
        IMAGE_DIR.mkdir(exist_ok=True)

    def _get_file_list(self, directory: Path, pattern: str) -> list:
        """Get list of files matching pattern in directory."""
        return sorted(directory.glob(pattern), key=os.path.getctime, reverse=True)

    def _cleanup_old_files(self, directory: Path, pattern: str, limit: int):
        """Remove old files exceeding the limit."""
        files = self._get_file_list(directory, pattern)
        for file in files[limit:]:
            try:
                file.unlink()
                logger.debug(f"Deleted old file: {file}")
            except Exception as e:
                logger.error(f"Error deleting file {file}: {e}")

    def cleanup_old_files(self):
        """Clean up old files in both video and image directories."""
        self._cleanup_old_files(VIDEO_DIR, "*.mp4", FILES_LIMIT_VIDEO)
        self._cleanup_old_files(IMAGE_DIR, "*.jpg", FILES_LIMIT_IMAGE)

    def get_latest_files(self, directory: Path, pattern: str, limit: int = None) -> list:
        """Get list of latest files."""
        if limit is None:
            limit = FILES_LIMIT_VIDEO if pattern == "*.mp4" else FILES_LIMIT_IMAGE
        return self._get_file_list(directory, pattern)[:limit]

    def get_file_info(self, file_path: Path) -> dict:
        """Get information about a file."""
        stat = file_path.stat()
        return {
            'name': file_path.name,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).strftime(FILE_DATE_FORMAT),
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime(FILE_DATE_FORMAT)
        } 