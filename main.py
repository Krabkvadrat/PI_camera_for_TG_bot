# -*- coding: utf-8 -*-
import os
import sqlite3
from time import sleep
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import Quality
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from settings import TOKEN

bot = telebot.TeleBot(TOKEN)

# Constants
VIDEO_SIZE = (800, 600)
PHOTO_SIZE = (2592, 1944)
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
VIDEO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
FILES_LIMIT_VIDEO = 10
FILES_LIMIT_IMAGE = 20

# Create directories if they don't exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)



# Function to insert interaction into the database
def log_interaction(user_id, command, DB_FILE = "bot_interactions.db"):
    """Logs user interaction into the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO interactions (user_id, timestamp, command)
            VALUES (?, ?, ?)
        """, (user_id, timestamp, command, details))

        conn.commit()
    except Exception as e:
        print(f"Error logging interaction: {e}")
    finally:
        conn.close()

def create_main_keyboard():
    """Create the main menu keyboard."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        KeyboardButton("📹 Record Video"),
        KeyboardButton("📸 Capture Photo"),
    )
    markup.add(
        KeyboardButton("🎥 Show Latest Video"),
        KeyboardButton("🖼️ Show Latest Photo")
    )
    return markup


def send_latest_media_file(path: str, message, media_type: str):
    """Send the latest media file from a specified directory."""
    try:
        files = sorted(os.listdir(path))

        if not files:
            bot.send_message(message.chat.id, "No files found.")
            return

        latest_file = files[-1]
        link = os.path.join(path, latest_file)

        with open(link, 'rb') as file:
            if media_type == 'video':
                bot.send_video(message.chat.id, video=file, supports_streaming=True)
            elif media_type == 'photo':
                bot.send_photo(message.chat.id, photo=file)

        # Redisplay the main menu keyboard after sending the media
        bot.send_message(
            message.chat.id,
            "Choose another option:",
            reply_markup=create_main_keyboard()
        )

        # Delete all but the most recent files
        for file in files[:-FILES_LIMIT_VIDEO]:
            try:
                os.remove(os.path.join(path, file))
            except FileNotFoundError:
                pass  # Ignore files that may have already been deleted

    except Exception as e:
        bot.send_message(message.chat.id, f"Error sending file: {e}")


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    """Handle the /start command and show main menu."""
    bot.send_message(
        message.chat.id,
        "Welcome! Choose an option:",
        reply_markup=create_main_keyboard()
    )
    log_interaction(message.from_user.id, "start")

@bot.message_handler(func=lambda message: message.text == "📹 Record Video")
def handle_video_command(message):
    """Handle the video recording option."""
    bot.send_message(
        message.chat.id,
        "Enter the video duration in seconds (between 2 and 30 seconds):",
        reply_markup=ReplyKeyboardRemove()  # Hide the keyboard
    )
    bot.register_next_step_handler(message, process_video_duration)
    log_interaction(message.from_user.id, "record_video")


def process_video_duration(message):
    """Process the video duration input."""
    try:
        duration = int(message.text)
        if duration < 2 or duration > 30:
            bot.send_message(message.chat.id, "Duration must be between 2 and 30 seconds. Try again.")
            bot.register_next_step_handler(message, process_video_duration)
            return

        now = datetime.now().strftime('%Y%m%d_%H_%M_%S')
        output_file = os.path.join(VIDEO_DIR, f"{now}_now.mp4")

        try:
            picam2 = Picamera2()
            picam2.video_configuration.size = VIDEO_SIZE
            picam2.start_and_record_video(output_file, duration=duration, quality=Quality.VERY_HIGH)
            bot.send_message(message.chat.id, f"Recording {duration} seconds video...")

            sleep(duration)
        finally:
            picam2.stop_recording()
            picam2.close()

        bot.send_message(message.chat.id, "Video ready")
        send_latest_media_file(VIDEO_DIR, message, 'video')

    except ValueError:
        bot.send_message(message.chat.id, "Invalid input! Please enter a valid number.")
        bot.register_next_step_handler(message, process_video_duration)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")


@bot.message_handler(func=lambda message: message.text == "📸 Capture Photo")
def handle_camera_command(message):
    """Handle capturing a photo."""
    log_interaction(message.from_user.id, "capture_photo")

    bot.send_message(message.chat.id, "Capturing photo...", reply_markup=ReplyKeyboardRemove())
    try:
        now = datetime.now().strftime('%Y%m%d_%H_%M_%S')
        photo_path = os.path.join(IMAGE_DIR, f"{now}.jpg")

        try:
            picam2 = Picamera2()
            camera_config = picam2.create_still_configuration(main={"size": PHOTO_SIZE})
            picam2.configure(camera_config)
            picam2.start()
            sleep(2)
            picam2.capture_file(photo_path)
        finally:
            picam2.close()

        bot.send_message(message.chat.id, "Photo captured")
        send_latest_media_file(IMAGE_DIR, message, 'photo')

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")


@bot.message_handler(func=lambda message: message.text == "🎥 Show Latest Video")
def handle_show_video_command(message):
    """Send the latest video."""
    log_interaction(message.from_user.id, "show_latest_video")

    bot.send_message(message.chat.id, "Fetching the latest video...", reply_markup=ReplyKeyboardRemove())
    send_latest_media_file(VIDEO_DIR, message, 'video')


@bot.message_handler(func=lambda message: message.text == "🖼️ Show Latest Photo")
def handle_photo_command(message):
    """Send the latest photo."""
    log_interaction(message.from_user.id, "show_latest_photo")

    bot.send_message(message.chat.id, "Fetching the latest photo...", reply_markup=ReplyKeyboardRemove())
    send_latest_media_file(IMAGE_DIR, message, 'photo')


print('TG bot started')
bot.infinity_polling()
