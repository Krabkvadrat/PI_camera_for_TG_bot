# Raspberry Pi Camera Telegram Bot

A Telegram bot that allows you to control a Raspberry Pi camera, take photos, and record videos.

## Features

- Take photos using the Raspberry Pi camera
- Record videos with customizable duration
- View latest photos and videos
- Clean up old files
- Comprehensive logging system

## Prerequisites

- Raspberry Pi with camera module
- Python 3.9 or later
- Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PI_camera_for_TG_bot
```

2. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y libcamera0.0.3 libcamera-tools libcamera-dev python3-picamera2
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `settings.py` file in the project root and add your Telegram bot token:
```python
TOKEN = "your_bot_token_here"
```

## Usage

1. Start the bot:
```bash
python main.py
```

2. Open Telegram and start a chat with your bot
3. Use the following commands:
   - `/start` - Show welcome message and available commands
   - `/photo` - Take a photo
   - `/video` - Record a video (will prompt for duration)
   - `/latest` - Show latest photos and videos
   - `/cleanup` - Clean up old files

## Logging

The bot includes a comprehensive logging system:
- Console output: INFO level and above
- File output: DEBUG level and above
- Log files are stored in the `logs` directory
- Log files are rotated when they reach 10MB
- Up to 5 backup log files are kept

## File Management

- Photos are stored in the `images` directory
- Videos are stored in the `videos` directory
- Old files are automatically cleaned up when the limit is reached
- File limits can be configured in `config.py`

## Error Handling

The bot includes comprehensive error handling for:
- Camera operations
- File operations
- Network issues
- Invalid user input

## Contributing

Feel free to submit issues and enhancement requests! 