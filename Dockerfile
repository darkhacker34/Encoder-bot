# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy the application code into the container
COPY . .

# Expose port 8000 for Flask
EXPOSE 8000

# Set environment variable for the Telegram bot token
ENV TELEGRAM_BOT_TOKEN=7351729896:AAGh9Z8Wn4vUjebCTWRtP8uXoflzgZHFhoc

# Copy and set the entrypoint script
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
