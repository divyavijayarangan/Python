import ffmpeg
import os
from pathlib import Path
import subprocess
import sys

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return True
    except FileNotFoundError:
        print("FFmpeg is not installed or not found in system PATH!")
        print("\nTo install FFmpeg:")
        print("1. Using Chocolatey (recommended):")
        print("   - Open PowerShell as Administrator")
        print("   - Run: choco install ffmpeg")
        print("\n2. Manual installation:")
        print("   - Download from: https://github.com/BtbN/FFmpeg-Builds/releases")
        print("   - Extract and add to system PATH")
        return False

def compress_video(input_path: str, output_path: str, target_size_mb: float = 50, 
                  min_bitrate: int = 800, max_bitrate: int = 8000) -> None:
    """
    Compress a video file to a target size while maintaining quality.
    """
    # Check if FFmpeg is installed
    if not check_ffmpeg():
        sys.exit(1)
    
    # Validate input path
    if not os.path.exists(input_path):
        print(f"\nError: Input file not found: {input_path}")
        print(f"Please check if the file exists and the path is correct.")
        print(f"Current working directory: {os.getcwd()}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    print("\nFile found! Starting compression...")
    
    # Get video information
    probe = ffmpeg.probe(input_path)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    duration = float(probe['format']['duration'])
    
    # Calculate target bitrate (in kbps)
    target_total_bitrate = (target_size_mb * 8192) / duration
    
    # Assume audio bitrate of 128k and subtract it from total bitrate
    audio_bitrate = 128
    target_video_bitrate = max(min(target_total_bitrate - audio_bitrate, max_bitrate), min_bitrate)
    
    print(f"\nCompressing: {os.path.basename(input_path)}")
    print(f"Target size: {target_size_mb} MB")
    print(f"Calculated video bitrate: {target_video_bitrate:.0f} kbps")
    
    # Set up compression parameters
    stream = ffmpeg.input(input_path)
    
    stream = ffmpeg.output(stream, output_path,
                         **{
                             'c:v': 'libx264',
                             'b:v': f'{target_video_bitrate}k',
                             'maxrate': f'{max_bitrate}k',
                             'bufsize': f'{max_bitrate*2}k',
                             'preset': 'slower',
                             'c:a': 'aac',
                             'b:a': f'{audio_bitrate}k',
                             'threads': 0,
                             'loglevel': 'error'
                         })
    
    # Run the compression
    try:
        stream.run(overwrite_output=True)
        
        # Print compression results
        original_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        compressed_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        print(f"\nCompression complete!")
        print(f"Original size: {original_size:.2f} MB")
        print(f"Compressed size: {compressed_size:.2f} MB")
        print(f"Compression ratio: {original_size/compressed_size:.2f}x")
        print(f"Saved to: {output_path}")
        
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode() if e.stderr else str(e)}")
        raise

if __name__ == "__main__":
    # Your specific video path
    input_video = r"C:\Users\magim\Downloads\Family_Guy_S11E22_No_Country_Club_for_Old_Men_Uncensored.mkv"
    output_video = r"C:\Users\magim\Downloads\FAMILY\Family_Guy_S11E22_No_Country_Club_for_Old_Men_Uncensored.mkv"
    
    try:
        print(f"Attempting to compress video:")
        print(f"Input: {input_video}")
        print(f"Output: {output_video}")
        
        # Compress the video
        compress_video(input_video, output_video, target_size_mb=50)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
