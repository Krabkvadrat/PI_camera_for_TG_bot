# -*- coding: utf-8 -*-
import os
import subprocess
from time import sleep
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import Quality
import telebot
from settings import TOKEN

bot = telebot.TeleBot(TOKEN)

# Constants
VIDEO_SIZE = (800, 600)
PHOTO_SIZE = (2592, 1944)
VIDEO_BITRATE = 10_000_000  # 10 Mbps
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
VIDEO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
FILES_LIMIT_VIDEO = 10
FILES_LIMIT_IMAGE = 20

# Create directories if they don't exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

def convert_h264_to_mp4(input_file: str, output_file: str):
    """Convert an H.264 file to MP4 format using ffmpeg and delete the original H.264 file after conversion."""
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"The input file {input_file} does not exist.")

    command = [
        'ffmpeg',
        '-fflags', '+genpts',
        '-i', input_file,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Successfully converted {input_file} to {output_file}.")
        os.remove(input_file)
        print(f"Deleted the original file: {input_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during conversion: {e}")
    except OSError as e:
        print(f"Error deleting file: {e}")

def send_latest_media_file(path: str, message, media_type: str):
    """Send the latest media file from a specified directory."""
    try:
        files = sorted(os.listdir(path))
        
        if not files:
            bot.send_message(message.chat.id, "No files found.")
            return

        # Construct file link
        latest_file = files[-1]
        link = os.path.join(path, latest_file)
        bot.send_message(message.chat.id, latest_file)
        
        with open(link, 'rb') as file:
            if media_type == 'video':
                bot.send_video(message.chat.id, video=file, supports_streaming=True)
            elif media_type == 'photo':
                bot.send_photo(message.chat.id, photo=file)

        # Delete all but the most recent files
        if len(files) > FILES_LIMIT_VIDEO:
            for file in files[:-FILES_LIMIT_VIDEO]:
                os.remove(os.path.join(path, file))

    except Exception as e:
        print(f"{e}, Error sending file")

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    """Handle the /start command."""
    bot.send_message(message.chat.id, "Hello!")

@bot.message_handler(commands=['video'])
def handle_video_command(message):
    """Handle the /video command to record and send a video."""
    try:
        # Ask for the duration
        bot.send_message(message.chat.id, "Enter the video duration in seconds (between 2 and 30 seconds):")
        bot.register_next_step_handler(message, process_video_duration)
    except Exception as e:
        bot.send_message(message.chat.id, f"{e}\nSomething went wrong")

def process_video_duration(message):
    """Process the video duration input."""
    try:
        duration = int(message.text)
        if duration < 2 or duration > 30:
            bot.send_message(message.chat.id, "Duration must be between 2 and 30 seconds.")
            return

        now = datetime.now().strftime('%Y%m%d_%H_%M_%S')
        output_file = os.path.join(VIDEO_DIR, f"{now}_now.mp4")
        output_file_converted = os.path.join(VIDEO_DIR, f"{now}_now.mp4")

        picam2 = Picamera2()
        picam2.video_configuration.size = VIDEO_SIZE
        
        picam2.start_and_record_video(f"{output_file}", duration = duration, quality=Quality.VERY_HIGH)
        bot.send_message(message.chat.id, f"Recording {duration} seconds video...")

        sleep(duration)
        picam2.stop_recording()
        picam2.close()

        #convert_h264_to_mp4(output_file, output_file_converted)
        bot.send_message(message.chat.id, "Video ready")
        send_latest_media_file(VIDEO_DIR, message, 'video')

    except ValueError:
        bot.send_message(message.chat.id, "Invalid input! Please enter a number.")
        picam2.close()
    except Exception as e:
        bot.send_message(message.chat.id, f"{e}\nSomething went wrong")
        picam2.close()

@bot.message_handler(commands=['show_video'])
def handle_show_video_command(message):
    """Handle the /show_video command to send the latest video."""
    send_latest_media_file(VIDEO_DIR, message, 'video')

@bot.message_handler(commands=['camera'])
def handle_camera_command(message):
    """Handle the /camera command to capture and send a photo."""
    bot.send_message(message.chat.id, "Capturing photo")
    try:
        picam2 = Picamera2()
        now = datetime.now().strftime('%Y%m%d_%H_%M_%S')
        camera_config = picam2.create_still_configuration(main={"size": PHOTO_SIZE})
        picam2.configure(camera_config) 
        picam2.start()
        sleep(2)
        picam2.capture_file(os.path.join(IMAGE_DIR, f"{now}.jpg"))
        bot.send_message(message.chat.id, "Photo captured")
        picam2.close()
        send_latest_media_file(IMAGE_DIR, message, 'photo')

    except Exception as e:
        bot.send_message(message.chat.id, f"{e}\nSome error while taking the photo")

@bot.message_handler(commands=['photo'])
def handle_photo_command(message):
    """Handle the /photo command to send the latest photo."""
    send_latest_media_file(IMAGE_DIR, message, 'photo')


print('TG bot started')
bot.infinity_polling()
