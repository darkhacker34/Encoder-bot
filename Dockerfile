# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and the script into the container
COPY requirements.txt requirements.txt
COPY bot.py bot.py

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Expose port 8000 for Flask
EXPOSE 8000

# Set the entry point to your script
CMD ["python", "bot.py"]
