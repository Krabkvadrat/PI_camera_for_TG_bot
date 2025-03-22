FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcamera0 \
    libcamera-tools \
    libcamera-dev \
    python3-picamera2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p images videos logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"] 