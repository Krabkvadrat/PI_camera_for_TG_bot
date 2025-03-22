import threading
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import Quality
import logging
from config import (
    VIDEO_SIZE, PHOTO_SIZE, CAMERA_TIMEOUT, CAMERA_WARMUP,
    VIDEO_DIR, IMAGE_DIR, FILE_DATE_FORMAT
)
from file_manager import FileManager

logger = logging.getLogger(__name__)

class CameraHandler:
    def __init__(self):
        self.camera_lock = threading.Lock()
        self.file_manager = FileManager()
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        VIDEO_DIR.mkdir(exist_ok=True)
        IMAGE_DIR.mkdir(exist_ok=True)

    def _get_camera(self):
        """Get camera instance with lock."""
        if not self.camera_lock.acquire(timeout=CAMERA_TIMEOUT):
            raise RuntimeError("Camera is currently in use")
        return Picamera2()

    def _release_camera(self, camera):
        """Release camera resources and lock."""
        try:
            camera.close()
        finally:
            self.camera_lock.release()

    def record_video(self, duration: int) -> str:
        """Record a video for the specified duration."""
        timestamp = datetime.now().strftime(FILE_DATE_FORMAT)
        output_file = VIDEO_DIR / f"{timestamp}_now.mp4"

        camera = self._get_camera()
        try:
            camera.video_configuration.size = VIDEO_SIZE
            logger.debug("Camera initialized for video recording")
            
            camera.start_and_record_video(str(output_file), duration=duration, quality=Quality.VERY_HIGH)
            self.file_manager.cleanup_old_files()  # Clean up old files after recording
            return str(output_file)

        except Exception as e:
            logger.error(f"Error during video recording: {e}", exc_info=True)
            raise
        finally:
            camera.stop_recording()
            self._release_camera(camera)

    def capture_photo(self) -> str:
        """Capture a single photo."""
        timestamp = datetime.now().strftime(FILE_DATE_FORMAT)
        photo_path = IMAGE_DIR / f"{timestamp}.jpg"

        camera = self._get_camera()
        try:
            camera_config = camera.create_still_configuration(main={"size": PHOTO_SIZE})
            camera.configure(camera_config)
            camera.start()
            logger.debug("Camera initialized for photo capture")
            
            camera.capture_file(str(photo_path))
            self.file_manager.cleanup_old_files()  # Clean up old files after capturing
            return str(photo_path)

        except Exception as e:
            logger.error(f"Error capturing photo: {e}", exc_info=True)
            raise
        finally:
            self._release_camera(camera) 