import subprocess
import os

def hardcode_subtitles(video_path, subtitle_path, output_path):
    """
    Hardcodes subtitles into a video using FFmpeg.

    Args:
        video_path (str): Path to the input video file (e.g., video.mp4).
        subtitle_path (str): Path to the subtitle file (e.g., subtitles.srt).
        output_path (str): Path for the output video file with hardcoded subtitles.
    """
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return

    if not os.path.exists(subtitle_path):
        print(f"Subtitle file not found: {subtitle_path}")
        return

    # FFmpeg command to hardcode subtitles
    command = [
        "ffmpeg",
        "-i", video_path,  # Input video
        "-vf", f"subtitles={subtitle_path}",  # Subtitle filter
        "-c:a", "copy",  # Copy the audio as-is
        output_path  # Output file
    ]

    try:
        # Run the FFmpeg command
        subprocess.run(command, check=True)
        print(f"Subtitles hardcoded successfully. Output saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing: {e}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")

# File paths
video_file = "/Users/jonaskjeldmand/Desktop/movie.mp4"
subtitle_file = "/Users/jonaskjeldmand/Downloads/Embrace.of.the.Serpent.2015.1080p.BRRip.x264.Spanish.AAC-ETRG/English.srt"
output_file = "/Users/jonaskjeldmand/Desktop/movie_with_subtitles.mp4"

hardcode_subtitles(video_file, subtitle_file, output_file)
