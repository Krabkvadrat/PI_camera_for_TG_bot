import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from config import TOKEN, MIN_VIDEO_DURATION, MAX_VIDEO_DURATION
from camera_handler import CameraHandler
from file_manager import FileManager

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_DURATION = 1

class PiCameraBot:
    def __init__(self):
        self.camera = CameraHandler()
        self.file_manager = FileManager()
        self.application = Application.builder().token(TOKEN).build()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        await update.message.reply_text(
            'Hello! I am a Raspberry Pi Camera Bot.\n'
            'Available commands:\n'
            '/photo - take a photo\n'
            '/video - record a video\n'
            '/latest - show latest files\n'
            '/cleanup - clean up old files'
        )

    async def photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Take a photo and send it."""
        try:
            await update.message.reply_text("Taking a photo...")
            photo_path = self.camera.capture_photo()
            await update.message.reply_photo(open(photo_path, 'rb'))
            logger.info(f"Photo sent successfully: {photo_path}")
        except Exception as e:
            logger.error(f"Error taking photo: {e}", exc_info=True)
            await update.message.reply_text("An error occurred while taking the photo")

    async def video_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start video recording process."""
        await update.message.reply_text(
            f"Enter video duration in seconds (from {MIN_VIDEO_DURATION} to {MAX_VIDEO_DURATION}):"
        )
        return WAITING_FOR_DURATION

    async def video_duration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle video duration input."""
        try:
            duration = int(update.message.text)
            if not MIN_VIDEO_DURATION <= duration <= MAX_VIDEO_DURATION:
                await update.message.reply_text(
                    f"Duration must be between {MIN_VIDEO_DURATION} and {MAX_VIDEO_DURATION} seconds"
                )
                return WAITING_FOR_DURATION

            await update.message.reply_text(f"Recording video for {duration} seconds...")
            video_path = self.camera.record_video(duration)
            await update.message.reply_video(open(video_path, 'rb'))
            logger.info(f"Video sent successfully: {video_path}")
        except ValueError:
            await update.message.reply_text("Please enter a number")
            return WAITING_FOR_DURATION
        except Exception as e:
            logger.error(f"Error recording video: {e}", exc_info=True)
            await update.message.reply_text("An error occurred while recording the video")
        finally:
            return ConversationHandler.END

    async def latest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show latest files."""
        try:
            latest_videos = self.file_manager.get_latest_files(VIDEO_DIR, "*.mp4")
            latest_photos = self.file_manager.get_latest_files(IMAGE_DIR, "*.jpg")

            message = "Latest files:\n\n"
            if latest_videos:
                message += "Videos:\n"
                for video in latest_videos:
                    info = self.file_manager.get_file_info(video)
                    message += f"- {info['name']} ({info['created']})\n"

            if latest_photos:
                message += "\nPhotos:\n"
                for photo in latest_photos:
                    info = self.file_manager.get_file_info(photo)
                    message += f"- {info['name']} ({info['created']})\n"

            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Error listing files: {e}", exc_info=True)
            await update.message.reply_text("An error occurred while getting the file list")

    async def cleanup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clean up old files."""
        try:
            self.file_manager.cleanup_old_files()
            await update.message.reply_text("Old files have been successfully deleted")
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}", exc_info=True)
            await update.message.reply_text("An error occurred while cleaning up files")

    def setup_handlers(self):
        """Set up command handlers."""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("photo", self.photo))
        self.application.add_handler(CommandHandler("latest", self.latest))
        self.application.add_handler(CommandHandler("cleanup", self.cleanup))

        video_handler = ConversationHandler(
            entry_points=[CommandHandler("video", self.video_start)],
            states={
                WAITING_FOR_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.video_duration)]
            },
            fallbacks=[],
        )
        self.application.add_handler(video_handler)

    def run(self):
        """Run the bot."""
        self.setup_handlers()
        self.application.run_polling() 