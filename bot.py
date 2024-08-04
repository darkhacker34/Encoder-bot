from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import subprocess
import os
import threading
import logging
from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/health')
def health_check():
    return 'Healthy', 200

def run_flask():
    app.run(host='0.0.0.0', port=8000)

# Replace 'YOUR_BOT_TOKEN' with your bot's API token
TOKEN = '7351729896:AAGh9Z8Wn4vUjebCTWRtP8uXoflzgZHFhoc'

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Send me a video and I will process it.')

def handle_document(update: Update, context: CallbackContext):
    # Download the file
    file = update.message.document.get_file()
    file.download('input.mp4')

    # Run ffmpeg command to encode the video
    subprocess.run(['ffmpeg', '-i', 'input.mp4', '-vcodec', 'libx264', '-b:v', '1M', 'output.mp4'])

    # Send the encoded video back
    context.bot.send_video(chat_id=update.effective_chat.id, video=open('output.mp4', 'rb'))

    # Clean up files
    os.remove('input.mp4')
    os.remove('output.mp4')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("video/mp4"), handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start the Telegram bot
    main()
