from pyrogram import Client, filters
import subprocess
import os

# Replace 'your_api_id' and 'your_api_hash' with your Telegram API credentials
api_id = 'your_api_id'
api_hash = 'your_api_hash'
bot_token = 'your_bot_token'

app = Client("video_encoder_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.video)
async def handle_video(client, message):
    video_file = await message.download()  # Download the video
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

    # Send the encoded video back to the user
    await message.reply_video(video=output_file)

    # Clean up files
    os.remove(input_file)
    os.remove(output_file)

if __name__ == "__main__":
    app.run()
