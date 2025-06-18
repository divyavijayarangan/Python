import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import ffmpeg
import os
import subprocess

TOKEN = '7667022636:AAFReTf7PNXFFQmdGGRYoZ647oy5q_MXuUY'  # Replace with your actual token

async def start(update: Update, context: CallbackContext):
    """Handle the /start command."""
    await update.message.reply_text('Hello! Send me a video and I will compress it for you.')

async def handle_video(update: Update, context: CallbackContext):
    """Handle video messages."""
    video = update.message.video
    file_id = video.file_id
    file = await context.bot.get_file(file_id)
    
    # Download the video
    input_path = f'./downloads/{file_id}.mp4'
    await file.download(input_path)
    output_path = f'./downloads/compressed_{file_id}.mp4'
    
    # Example video compression function
    try:
        compress_video(input_path, output_path)
        # Send the compressed video back
        await update.message.reply_video(video=open(output_path, 'rb'))
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")
    finally:
        # Clean up downloaded files
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

def compress_video(input_path: str, output_path: str, target_size_mb: float = 50, 
                  resolution: str = '1080p', bitrate_choice: int = 2) -> None:
    """Compress a video file to a target size while maintaining quality."""
    # Check if FFmpeg is installed
    if not check_ffmpeg():
        raise Exception("FFmpeg is not installed or accessible.")
    
    # Validate input path
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    print("Starting compression...")
    # Get video information and compress
    target_video_bitrate = get_bitrate_for_resolution_and_choice(resolution, bitrate_choice)
    
    stream = ffmpeg.input(input_path)
    stream = ffmpeg.output(stream, output_path,
                         **{
                             'c:v': 'libx264',
                             'b:v': f'{target_video_bitrate}k',
                             'maxrate': f'{target_video_bitrate}k',
                             'bufsize': f'{target_video_bitrate*2}k',
                             'preset': 'slower',
                             'c:a': 'aac',
                             'b:a': '128k',
                             'threads': 0,
                             'loglevel': 'error',
                             'map': '0',  # This will map all streams
                             'c:s': 'copy',  # Copy subtitle streams without re-encoding
                             'c:d': 'copy',  # Copy data streams if available
                         })
    
    # Run the compression
    stream.run(overwrite_output=True)

def check_ffmpeg() -> bool:
    """Check if FFmpeg is installed and accessible."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except FileNotFoundError:
        print("FFmpeg is not installed or not found in system PATH!")
        return False

def get_bitrate_for_resolution_and_choice(resolution: str, bitrate_choice: int) -> int:
    """Get the appropriate bitrate for the selected resolution and bitrate choice."""
    resolution_bitrates = {
        '480p': [500, 1000, 2000],
        '720p': [2500, 3000, 3500],
        '1080p': [4500, 5000, 6000],
        '2k': [8000, 10000, 12000],
        '4k': [15000, 20000, 25000]
    }
    return resolution_bitrates.get(resolution, [6000])[bitrate_choice - 1]  # Default to 6000 if invalid resolution

async def main():
    """Set up the bot and start polling for updates."""
    # Use Application instead of Updater
    application = Application.builder().token(TOKEN).build()

    # Add handlers for commands and messages
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.VIDEO , handle_video))

    # Start polling for updates
    await application.run_polling()

if __name__ == '__main__':
    # Run the main function using asyncio.run()
    asyncio.run(main())