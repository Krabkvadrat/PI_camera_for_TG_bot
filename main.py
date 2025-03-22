# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from bot import PiCameraBot
from config import BASE_DIR

# Create logs directory if it doesn't exist
log_dir = BASE_DIR / 'logs'
log_dir.mkdir(exist_ok=True)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Console handler (INFO and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler (DEBUG and above)
file_handler = RotatingFileHandler(
    log_dir / 'bot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def main():
    """Start the bot."""
    try:
        logger.info("Starting Pi Camera Bot...")
        bot = PiCameraBot()
        bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
