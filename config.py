from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / 'images'
VIDEO_DIR = BASE_DIR / 'videos'

# Camera settings
VIDEO_SIZE = (800, 600)
PHOTO_SIZE = (2592, 1944)
MIN_VIDEO_DURATION = 2
MAX_VIDEO_DURATION = 30
CAMERA_TIMEOUT = 10  # seconds
CAMERA_WARMUP = 2    # seconds

# File management
FILES_LIMIT_VIDEO = 4
FILES_LIMIT_IMAGE = 4
FILE_DATE_FORMAT = '%Y%m%d_%H_%M_%S'

# Bot settings
from settings import TOKEN 