from pyrogram import Client, filters
import subprocess
import os
from flask import Flask, request, jsonify
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Replace 'your_api_id', 'your_api_hash', and 'your_bot_token' with your credentials
api_id = '25731065'
api_hash = 'be534fb5a5afd8c3308c9ca92afde672'
bot_token = '7351729896:AAGh9Z8Wn4vUjebCTWRtP8uXoflzgZHFhoc'

# Initialize the Telegram client
app = Client("video_encoder_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Initialize the Flask app
flask_app = Flask(__name__)

# Handler for video messages
@app.on_message(filters.video)
async def handle_video(client, message):
    try:
        logger.info("Received a video message")
        video_file = await message.download()  # Download the video
        logger.info(f"Downloaded video file: {video_file}")
        
        input_file = video_file
        output_file = "encoded_" + os.path.basename(input_file)
        
        # Command to encode the video using ffmpeg
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vcodec', 'libx264',  # Video codec
            '-acodec', 'aac',  # Audio codec
            output_file
        ]

        # Run the command
        subprocess.run(command, check=True)
        logger.info(f"Encoded video file: {output_file}")

        # Send the encoded video back to the user
        await message.reply_video(video=output_file)
        logger.info("Sent the encoded video back to the user")

    except Exception as e:
        logger.error(f"Error processing video: {e}")
    finally:
        # Clean up files
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

# Flask route for a simple test endpoint
@flask_app.route('/')
def index():
    return "Flask is running and the bot is active!"

# Function to run the Flask app
def run_flask():
    try:
        logger.info("Starting Flask server on port 8000")
        flask_app.run(host='0.0.0.0', port=8000)
    except Exception as e:
        logger.error(f"Error running Flask server: {e}")

if __name__ == "__main__":
    # Start Flask in a separate thread
    threading.Thread(target=run_flask).start()
    
    # Start the Pyrogram client
    try:
        logger.info("Starting Telegram bot")
        app.run()
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")
