import subprocess
import os
from pathlib import Path

def combine_video_and_subtitles(video_path, srt_path, output_path=None):
    """
    Combines a video file with an SRT subtitle file using FFmpeg.
    """
    # Validate input files
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"Subtitle file not found: {srt_path}")
    
    # Create output path if not provided
    if output_path is None:
        video_filename = Path(video_path).stem
        output_path = f"{video_filename}_with_subtitles.mp4"  # Force MP4 extension
    
    # Ensure output path has an extension
    if not Path(output_path).suffix:
        output_path += '.mp4'
    
    try:
        # Simpler FFmpeg command with more compatible parameters
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', srt_path,
            '-c:v', 'copy',              # Copy video stream exactly
            '-c:a', 'copy',              # Copy audio stream exactly
            '-scodec', 'mov_text',       # More compatible subtitle codec
            '-metadata:s:s:0', 'language=eng',
            output_path
        ]
        
        print("\nProcessing video...")
        print("Command:", ' '.join(cmd))  # Print command for debugging
        
        # Run FFmpeg with full error output
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("\nFFmpeg Error Output:")
            print(result.stderr)
            
            # Try alternative method if first method fails
            print("\nTrying alternative method...")
            cmd_alt = [
                'ffmpeg',
                '-i', video_path,
                '-i', srt_path,
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-c:s', 'srt',           # Try with SRT subtitle codec
                output_path
            ]
            
            result_alt = subprocess.run(cmd_alt, capture_output=True, text=True)
            
            if result_alt.returncode != 0:
                print("\nAlternative method also failed. FFmpeg Error Output:")
                print(result_alt.stderr)
                raise Exception("Both subtitle embedding methods failed")
        
        print(f"\nSuccessfully combined video and subtitles to: {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        print("\nError occurred while combining video and subtitles:")
        print(f"FFmpeg error output: {e.stderr}")
        raise
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        raise

def main():
    print("Video and Subtitle Merger")
    print("========================")
    print("Note: This program will maintain original video quality\n")
    
    try:
        # Get paths directly from user input
        video_path = input("Enter the path to your video file: ").strip('"').strip("'")
        srt_path = input("Enter the path to your subtitle file: ").strip('"').strip("'")
        
        # Ask for output filename only (not full path)
        print("\nWould you like to specify an output filename?")
        output_choice = input("Enter filename (or press Enter to use default): ").strip()
        
        output_path = None
        if output_choice:
            # Place output in same directory as input video
            output_path = str(Path(video_path).parent / output_choice)
        
        # Combine video and subtitles
        output_file = combine_video_and_subtitles(video_path, srt_path, output_path)
        print(f"\nProcess completed successfully!")
        print(f"Output file: {output_file}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure FFmpeg is properly installed and in your system PATH")
        print("2. Check if the video and subtitle files are not corrupted")
        print("3. Try placing all files in a path without special characters")
        print("4. Ensure you have write permissions in the output directory")

if __name__ == "__main__":
    main()
