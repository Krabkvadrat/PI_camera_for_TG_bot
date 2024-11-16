# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from settings import TOKEN

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# Database file path
DB_FILE = "bot_interactions.db"


# Function to insert interaction into the database
def log_interaction(user_id, command):
    """Logs user interaction into the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO interactions (user_id, timestamp, command)
            VALUES (?, ?, ?, ?)
        """, (user_id, timestamp, command))

        conn.commit()
    except Exception as e:
        print(f"Error logging interaction: {e}")
    finally:
        conn.close()


# Function to create a keyboard for bot interactions
def create_keyboard():
    """Creates a keyboard for bot commands."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📷 Capture Photo"), KeyboardButton("🎥 Record Video"))
    keyboard.add(KeyboardButton("🖼 Show Photo"), KeyboardButton("📹 Show Video"))
    return keyboard


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    """Handle the /start command."""
    bot.send_message(
        message.chat.id,
        "Welcome! Use the buttons below to interact.",
        reply_markup=create_keyboard()
    )
    log_interaction(message.from_user.id, "/start")


@bot.message_handler(func=lambda message: message.text == "📷 Capture Photo")
def handle_capture_photo(message):
    """Handle photo capture."""
    log_interaction(message.from_user.id, "capture_photo")
    bot.send_message(message.chat.id, "Capturing photo... (Feature coming soon)", reply_markup=ReplyKeyboardRemove())
    # Add your photo capture logic here
    bot.send_message(message.chat.id, "Photo captured!", reply_markup=create_keyboard())


@bot.message_handler(func=lambda message: message.text == "🎥 Record Video")
def handle_record_video(message):
    """Handle video recording."""
    log_interaction(message.from_user.id, "record_video")
    bot.send_message(message.chat.id, "Recording video... (Feature coming soon)", reply_markup=ReplyKeyboardRemove())
    # Add your video recording logic here
    bot.send_message(message.chat.id, "Video recorded!", reply_markup=create_keyboard())


@bot.message_handler(func=lambda message: message.text == "🖼 Show Photo")
def handle_show_photo(message):
    """Handle showing the latest photo."""
    log_interaction(message.from_user.id, "show_photo")
    bot.send_message(message.chat.id, "Showing photo... (Feature coming soon)", reply_markup=ReplyKeyboardRemove())
    # Add your logic to send the latest photo here
    bot.send_message(message.chat.id, "Here is your photo!", reply_markup=create_keyboard())


@bot.message_handler(func=lambda message: message.text == "📹 Show Video")
def handle_show_video(message):
    """Handle showing the latest video."""
    log_interaction(message.from_user.id, "show_video")
    bot.send_message(message.chat.id, "Showing video... (Feature coming soon)", reply_markup=ReplyKeyboardRemove())
    # Add your logic to send the latest video here
    bot.send_message(message.chat.id, "Here is your video!", reply_markup=create_keyboard())


print("Bot is running...")
bot.infinity_polling()
