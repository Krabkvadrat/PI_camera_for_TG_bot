# Raspberry Pi Camera Telegram Bot

A Telegram bot that allows you to capture photos and record videos using a Raspberry Pi camera module.

## Features

- 📸 Capture photos
- 📹 Record videos (2-30 seconds)
- 🖼️ View latest captured photo
- 🎥 View latest recorded video
- 📊 Log all interactions
- 🔒 Thread-safe camera operations
- 📝 Comprehensive logging

## Prerequisites

- Raspberry Pi with camera module
- Docker and Docker Compose installed
- Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PI_camera_for_TG_bot
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Edit `.env` file and add your Telegram bot token:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## Running with Docker

1. Build and start the container:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f
```

3. Stop the bot:
```bash
docker-compose down
```

## Manual Installation (without Docker)

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the bot:
```bash
python main.py
```

## Usage

1. Open Telegram and start a chat with your bot
2. Use the following commands:
   - `/start` - Show main menu
   - 📸 Capture Photo - Take a new photo
   - 📹 Record Video - Record a new video (2-30 seconds)
   - 🖼️ Show Latest Photo - View the most recent photo
   - 🎥 Show Latest Video - View the most recent video

## Project Structure

```
PI_camera_for_TG_bot/
├── main.py           # Main bot logic
├── camera.py         # Camera operations
├── database.py       # Database operations
├── logger.py         # Logging utility
├── config.py         # Configuration settings
├── images/          # Directory for photos
├── videos/          # Directory for videos
├── logs/            # Directory for logs
├── Dockerfile       # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── .env             # Environment variables
├── .env.example     # Environment variables template
├── requirements.txt  # Project dependencies
└── README.md        # Project documentation
```

## Logging

Logs are stored in the `logs` directory. The log file contains:
- Bot operations
- Camera operations
- Database operations
- Error messages

## Database

The bot uses SQLite to store interaction logs. The database file is created automatically in the project root directory.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 