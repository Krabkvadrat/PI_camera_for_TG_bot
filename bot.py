import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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

    def create_main_keyboard(self):
        """Create the main menu keyboard."""
        keyboard = [
            ["📹 Record Video", "📸 Capture Photo"],
            ["🎥 Show Latest Video", "🖼️ Show Latest Photo"]
        ]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        return markup

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        await update.message.reply_text(
            'Hello! I am a Raspberry Pi Camera Bot.\n'
            'Choose an option:',
            reply_markup=self.create_main_keyboard()
        )

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle capturing a photo."""
        try:
            await update.message.reply_text("Taking a photo...", reply_markup=ReplyKeyboardRemove())
            photo_path = self.camera.capture_photo()
            await update.message.reply_photo(open(photo_path, 'rb'))
            await update.message.reply_text(
                "Choose an option:",
                reply_markup=self.create_main_keyboard()
            )
            logger.info(f"Photo sent successfully: {photo_path}")
        except Exception as e:
            logger.error(f"Error taking photo: {e}", exc_info=True)
            await update.message.reply_text(
                "An error occurred while taking the photo",
                reply_markup=self.create_main_keyboard()
            )

    async def handle_video_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start video recording process."""
        await update.message.reply_text(
            f"Enter video duration in seconds (from {MIN_VIDEO_DURATION} to {MAX_VIDEO_DURATION}):",
            reply_markup=ReplyKeyboardRemove()
        )
        return WAITING_FOR_DURATION

    async def handle_video_duration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await update.message.reply_text(
                "Choose an option:",
                reply_markup=self.create_main_keyboard()
            )
            logger.info(f"Video sent successfully: {video_path}")
        except ValueError:
            await update.message.reply_text("Please enter a number")
            return WAITING_FOR_DURATION
        except Exception as e:
            logger.error(f"Error recording video: {e}", exc_info=True)
            await update.message.reply_text(
                "An error occurred while recording the video",
                reply_markup=self.create_main_keyboard()
            )
        finally:
            return ConversationHandler.END

    async def handle_latest_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show latest video."""
        try:
            latest_videos = self.file_manager.get_latest_files(VIDEO_DIR, "*.mp4")
            if not latest_videos:
                await update.message.reply_text(
                    "No videos found.",
                    reply_markup=self.create_main_keyboard()
                )
                return

            latest_video = latest_videos[0]
            await update.message.reply_video(open(latest_video, 'rb'))
            await update.message.reply_text(
                "Choose an option:",
                reply_markup=self.create_main_keyboard()
            )
            logger.info(f"Latest video sent successfully: {latest_video}")
        except Exception as e:
            logger.error(f"Error sending latest video: {e}", exc_info=True)
            await update.message.reply_text(
                "An error occurred while getting the latest video",
                reply_markup=self.create_main_keyboard()
            )

    async def handle_latest_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show latest photo."""
        try:
            latest_photos = self.file_manager.get_latest_files(IMAGE_DIR, "*.jpg")
            if not latest_photos:
                await update.message.reply_text(
                    "No photos found.",
                    reply_markup=self.create_main_keyboard()
                )
                return

            latest_photo = latest_photos[0]
            await update.message.reply_photo(open(latest_photo, 'rb'))
            await update.message.reply_text(
                "Choose an option:",
                reply_markup=self.create_main_keyboard()
            )
            logger.info(f"Latest photo sent successfully: {latest_photo}")
        except Exception as e:
            logger.error(f"Error sending latest photo: {e}", exc_info=True)
            await update.message.reply_text(
                "An error occurred while getting the latest photo",
                reply_markup=self.create_main_keyboard()
            )

    def setup_handlers(self):
        """Set up command handlers."""
        # Start command
        self.application.add_handler(CommandHandler("start", self.start))

        # Button handlers
        self.application.add_handler(MessageHandler(filters.Regex("^📸 Capture Photo$"), self.handle_photo))
        self.application.add_handler(MessageHandler(filters.Regex("^🎥 Show Latest Video$"), self.handle_latest_video))
        self.application.add_handler(MessageHandler(filters.Regex("^🖼️ Show Latest Photo$"), self.handle_latest_photo))

        # Video recording conversation
        video_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^📹 Record Video$"), self.handle_video_start)],
            states={
                WAITING_FOR_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_video_duration)]
            },
            fallbacks=[],
        )
        self.application.add_handler(video_handler)

    def run(self):
        """Run the bot."""
        self.setup_handlers()
        self.application.run_polling() 