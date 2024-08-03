import os
import subprocess
import logging
from flask import Flask, request
from pyrogram import Client, filters
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask app
app = Flask(__name__)


# Replace with your actual credentials
API_ID = '25731065'
API_HASH = 'be534fb5a5afd8c3308c9ca92afde672'
BOT_TOKEN = '7351729896:AAGh9Z8Wn4vUjebCTWRtP8uXoflzgZHFhoc'

bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Handle incoming webhook from Telegram
    json_str = request.get_data(as_text=True)
    update = bot.parse_update(json_str)
    bot.process_update(update)
    return 'OK'

@bot.on_message(filters.video | filters.document)
async def handle_video(client, message):
    logging.info(f"Received a file: {message.document.file_name if message.document else 'video'}")
    
    # Check if the file is a video
    if message.video or (message.document and message.document.mime_type.startswith('video')):
        # Download the file
        file_path = await message.download()
        logging.info(f"Downloaded file to {file_path}")
        
        # Send initial progress message
        progress_message = await client.send_message(message.chat.id, "Processing video... 0%")
        
        # Process the file using FFmpeg
        output_file = "processed_" + os.path.basename(file_path)
        progress_file = "progress.txt"
        
        # Command to process the video and capture progress
        cmd = [
            "ffmpeg",
            "-i", file_path,
            "-vf", "scale=1280:720",  # Example: Resize to 720p
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-progress", progress_file,
            output_file
        ]
        
        logging.info("Starting FFmpeg process")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Monitor progress
        while process.poll() is None:
            if os.path.exists(progress_file):
                with open(progress_file, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith("out_time_ms="):
                            time_ms = int(line.split("=")[1])
                            # Calculate progress as a percentage
                            # Note: For simplicity, assuming a fixed duration; adapt for accurate progress
                            percent = min(time_ms / 10000000 * 100, 100)  # Example: 10 seconds duration
                            await progress_message.edit(f"Processing video... {int(percent)}%")
            
            await asyncio.sleep(1)

        # Ensure progress file is cleaned up
        if os.path.exists(progress_file):
            os.remove(progress_file)

        logging.info("Sending processed video back to user")
        # Send the processed file back to the user
        await client.send_document(message.chat.id, output_file)
        
        # Optionally delete the local files
        os.remove(file_path)
        os.remove(output_file)

@app.before_first_request
def setup():
    bot.start()

if __name__ == '__main__':
    app.run(port=8000)
