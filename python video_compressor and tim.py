import ffmpeg
import os
from pathlib import Path
import subprocess
import sys
import time  # Import the time module

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

def compress_video(input_path: str, output_path: str, target_size_mb: float = 50, 
                  resolution: str = '1080p', bitrate_choice: int = 2) -> None:
    """Compress a video file to a target size while maintaining quality."""
    # Check if FFmpeg is installed
    if not check_ffmpeg():
        sys.exit(1)
    
    # Validate input path
    if not os.path.exists(input_path):
        print(f"\nError: Input file not found: {input_path}")
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
    
    # Get the appropriate bitrate for the selected resolution and bitrate choice
    target_video_bitrate = get_bitrate_for_resolution_and_choice(resolution, bitrate_choice)
    
    print(f"\nCompressing: {os.path.basename(input_path)}")
    print(f"Target size: {target_size_mb} MB")
    print(f"Selected resolution: {resolution}")
    print(f"Selected bitrate: {target_video_bitrate} kbps")
    
    # Estimate time to compress based on duration and target bitrate (in MB per second)
    avg_bitrate = target_video_bitrate / 8  # Convert kbps to kBps
    estimated_time_sec = (os.path.getsize(input_path) / (1024 * 1024)) / avg_bitrate  # Estimate time in seconds
    estimated_time_min = estimated_time_sec / 60  # Convert to minutes
    
    print(f"Estimated compression time: {estimated_time_min:.2f} minutes")

    # Start the timer
    start_time = time.time()

    # Set up compression parameters
    stream = ffmpeg.input(input_path)
    
    # Map all streams (audio, video, subtitles)
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
                             'map': '0',  # This will map all streams (video, audio, subtitles)
                             'c:s': 'copy',  # Copy subtitle streams without re-encoding
                             'c:d': 'copy',  # Copy data streams (like chapters) if available
                         })
    
    # Run the compression
    try:
        print("Running compression...")  # Debugging message
        stream.run(overwrite_output=True)
        
        # Record the end time
        end_time = time.time()
        elapsed_time = end_time - start_time  # Calculate elapsed time
        
        # Print compression results
        original_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        compressed_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        print(f"\nCompression complete!")
        print(f"Original size: {original_size:.2f} MB")
        print(f"Compressed size: {compressed_size:.2f} MB")
        print(f"Compression ratio: {original_size/compressed_size:.2f}x")
        print(f"Saved to: {output_path}")
        
        # Print the elapsed time
        print(f"\nElapsed time: {elapsed_time:.2f} seconds")
        print(f"Estimated time: {estimated_time_min:.2f} minutes")

    except ffmpeg.Error as e:
        print(f"An error occurred during compression: {e.stderr.decode() if e.stderr else str(e)}")
        raise

if __name__ == "__main__":
    # Your specific video path
    input_video = r"C:\Users\magim\Downloads\Family_Guy_S11E22_No_Country_Club_for_Old_Men_Uncensored.mkv"
    output_video = r"C:\Users\magim\Downloads\FAMILY\Family_Guy_S11E22_No_Country_Club_for_Old_Men_Uncensored_compressed.mkv"
    
    # Allow user to select resolution
    print("Select a resolution:")
    print("1. 480p")
    print("2. 720p")
    print("3. 1080p")
    print("4. 2k")
    print("5. 4k")
    resolution_choice = input("Enter your resolution choice (1-5): ")
    
    resolution_map = {'1': '480p', '2': '720p', '3': '1080p', '4': '2k', '5': '4k'}
    resolution = resolution_map.get(resolution_choice, '1080p')  # Default to 1080p if invalid choice
    
    # Allow user to select bitrate based on selected resolution
    print(f"\nSelect a bitrate for {resolution}:")
    if resolution == '480p':
        print("1. 500 kbps")
        print("2. 1000 kbps")
        print("3. 2000 kbps")
    elif resolution == '720p':
        print("1. 2500 kbps")
        print("2. 3000 kbps")
        print("3. 3500 kbps")
    elif resolution == '1080p':
        print("1. 4500 kbps")
        print("2. 5000 kbps")
        print("3. 6000 kbps")
    elif resolution == '2k':
        print("1. 8000 kbps")
        print("2. 10000 kbps")
        print("3. 12000 kbps")
    elif resolution == '4k':
        print("1. 15000 kbps")
        print("2. 20000 kbps")
        print("3. 25000 kbps")
    
    bitrate_choice = int(input("Enter your bitrate choice (1-3): "))
    
    try:
        print(f"Attempting to compress video:")
        print(f"Input: {input_video}")
        print(f"Output: {output_video}")
        
        # Compress the video
        compress_video(input_video, output_video, target_size_mb=50, resolution=resolution, bitrate_choice=bitrate_choice)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
