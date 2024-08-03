from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import subprocess
import os, logging
from flask import Flask
import threading

API_ID = os.getenv('API_ID', '25731065')
API_HASH = os.getenv('API_HASH', 'be534fb5a5afd8c3308c9ca92afde672')
BOT_TOKEN = os.getenv('BOT_TOKEN', '7351729896:AAGh9Z8Wn4vUjebCTWRtP8uXoflzgZHFhoc')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize Flask
bot = Flask(__name__)

@bot.route('/')
def hello_world():
    return 'Hello, World!'

@bot.route('/health')
def health_check():
    return 'Healthy', 200

def run_flask():
    bot.run(host='0.0.0.0', port=8080)

app = Client("my_bot", api_id="API_ID", api_hash="API_HASH", bot_token="BOT_TOKEN")

# Define quality options and corresponding FFmpeg scale arguments
quality_options = {
    "480p": "640:480",
    "720p": "1280:720",
    "1080p": "1920:1080"
}

@app.on_message(filters.document & filters.video)
async def handle_movie(client, message):
    file_name = message.document.file_name
    # Notify user that downloading has started
    await message.reply_text("Downloading...")

    # Download the file
    downloaded_file = await message.download()

    # Create quality selection buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("480p", callback_data="480p")],
        [InlineKeyboardButton("720p", callback_data="720p")],
        [InlineKeyboardButton("1080p", callback_data="1080p")]
    ])

    # Ask the user for the desired quality
    await message.reply_text("Now quality:", reply_markup=keyboard)

    # Save the original file path
    message.data = downloaded_file

@app.on_callback_query()
async def handle_quality_selection(client, callback_query):
    quality = callback_query.data
    downloaded_file = callback_query.message.reply_to_message.document.file_name

    if quality in quality_options:
        # Define the output file name and encoding options
        output_file = f"encoded_{quality}.mp4"
        scale_option = quality_options[quality]

        # Run FFmpeg command to compress the video
        subprocess.run([
            "ffmpeg",
            "-i", downloaded_file,
            "-vf", f"scale={scale_option}",
            output_file
        ], check=True)

        # Send the encoded video back
        await callback_query.message.reply_text(f"Here is your video at {quality}:")
        await callback_query.message.reply_document(output_file)

        # Clean up
        os.remove(downloaded_file)
        os.remove(output_file)

        # Acknowledge the callback query
        await callback_query.answer()


if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    
    # Start the Pyrogram Client
    app.run()
