from pyrogram import Client, filters
from flask import Flask, request, jsonify
import threading, logging, time, subprocess, json, os, subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Replace with your actual credentials
api_id = '25731065'
api_hash = 'be534fb5a5afd8c3308c9ca92afde672'
bot_token = '7351729896:AAGh9Z8Wn4vUjebCTWRtP8uXoflzgZHFhoc'

# Initialize the Telegram client
app = Client("video_encoder_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Initialize the Flask app
flask_app = Flask(__name__)

def format_progress_bar(filename, percentage, done, total_size, status, eta, speed, elapsed, user_mention, user_id):
    bar_length = 10
    filled_length = int(bar_length * percentage / 100)
    bar = '●' * filled_length + '○' * (bar_length - filled_length)
    
    def format_size(size):
        size = int(size)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 ** 3:
            return f"{size / 1024 ** 2:.2f} MB"
        else:
            return f"{size / 1024 ** 3:.2f} GB"
    
    def format_time(seconds):
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds} sec"
        elif seconds < 3600:
            return f"{seconds // 60} min"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} hr {minutes} min"
    
    return (
        f"┏ ғɪʟᴇɴᴀᴍᴇ: {filename}\n"
        f"┠ [{bar}] {percentage:.2f}%\n"
        f"┠ ᴘʀᴏᴄᴇssᴇᴅ: {format_size(done)} ᴏғ {format_size(total_size)}\n"
        f"┠ sᴛᴀᴛᴜs: {status}\n"
        f"┠ sᴘᴇᴇᴅ: {format_size(speed)}/s\n"
        f"┖ ᴜsᴇʀ: {user_mention} | ɪᴅ: {user_id}" 
    )

def get_ffmpeg_info(file_path):
    try:
        result = subprocess.run(['ffmpeg', '-v', 'error', '-show_entries', 'format=duration,bit_rate', '-show_entries', 'stream=codec_type,codec_name,profile,width,height,bit_rate', '-of', 'json', file_path],
                                capture_output=True, text=True)
        return json.loads(result.stdout)
    except Exception as e:
        logger.error(f"Error getting FFmpeg info: {e}")
        return {}

@app.on_message(filters.video)
async def handle_video(client, message):
    try:
        user_mention = message.from_user.mention
        user_id = message.from_user.id
        filename = message.video.file_name
        total_size = message.video.file_size
        logger.info(f"Received a video message from {user_mention} (ID: {user_id})")

        # Download the video
        start_time = time.time()
        download_file = await message.download()  # Download the video with progress updates
        elapsed_time = time.time() - start_time
        logger.info(f"Downloaded video file: {download_file}")

        input_file = download_file
        output_file = f"encoded_{int(time.time())}_{os.path.basename(input_file)}"  # Unique filename
        
        # Command to encode the video using ffmpeg
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vcodec', 'libx264',  # Video codec
            '-acodec', 'aac',  # Audio codec
            output_file
        ]

        # Run the command
        start_time = time.time()
        subprocess.run(command, check=True)
        elapsed_time = time.time() - start_time
        logger.info(f"Encoded video file: {output_file}")

        # Get detailed information about the original and encoded videos
        original_info = get_ffmpeg_info(input_file)
        encoded_info = get_ffmpeg_info(output_file)

        # Format detailed information
        def format_detailed_info(info, file_type):
            streams = info.get('streams', [])
            format_info = info.get('format', {})
            duration = format_info.get('duration', 'N/A')
            bitrate = format_info.get('bit_rate', 'N/A')
            
            details = [f"┏ {file_type} ɪɴғᴏʀᴍᴀᴛɪᴏɴ:"]
            details.append(f"┠ Duration: {duration} sec")
            details.append(f"┠ Bitrate: {bitrate} bps")
            for stream in streams:
                codec_type = stream.get('codec_type', 'N/A')
                codec_name = stream.get('codec_name', 'N/A')
                profile = stream.get('profile', 'N/A')
                width = stream.get('width', 'N/A')
                height = stream.get('height', 'N/A')
                details.append(f"┠ {codec_type.capitalize()} Codec: {codec_name} (Profile: {profile})")
                if codec_type == 'video':
                    details.append(f"┠ Resolution: {width}x{height}")
            return '\n'.join(details)

        # Upload the encoded video back to the user
        async def update_upload_progress(current, total):
            percentage = (current / total) * 100
            progress_bar = format_progress_bar(
                filename=output_file,
                percentage=percentage,
                done=current,
                total_size=total,
                status="Uploading",
                eta="N/A",
                speed="N/A",
                elapsed=elapsed_time,
                user_mention=user_mention,
                user_id=user_id
            )
            await message.reply_text(progress_bar)

        start_time = time.time()
        await message.reply_video(video=output_file, progress=update_upload_progress)
        elapsed_time = time.time() - start_time
        logger.info("Sent the encoded video back to the user")

        # Final progress message
        upload_size = os.path.getsize(output_file)
        percentage = 100.0
        progress_bar = format_progress_bar(
            filename=output_file,
            percentage=percentage,
            done=upload_size,
            total_size=upload_size,
            status="Completed",
            eta="N/A",
            speed=upload_size / elapsed_time,
            elapsed=elapsed_time,
            user_mention=user_mention,
            user_id=user_id
        )

        detailed_info = (
            format_detailed_info(original_info, "Original") + '\n' +
            format_detailed_info(encoded_info, "Encoded") + '\n' +
            progress_bar
        )

        await message.reply_text(detailed_info)

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
