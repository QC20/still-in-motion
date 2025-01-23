#!/usr/bin/env python3
import os
import argparse
import subprocess
from moviepy.editor import VideoFileClip
from PIL import Image, ImageOps
from tqdm import tqdm

# Define output resolution for e-paper display
FRAME_WIDTH = 400
FRAME_HEIGHT = 300

def resize_video(input_path, output_path, width=FRAME_WIDTH, height=FRAME_HEIGHT):
    """
    Resize the video to the specified dimensions, maintaining full frame.
    
    Args:
        input_path (str): Path to the input video file.
        output_path (str): Path for the output resized video file.
        width (int, optional): Desired width. Defaults to 400.
        height (int, optional): Desired height. Defaults to 300.
    """
    try:
        # Load the video file
        clip = VideoFileClip(input_path)
        
        # Resize the video to the desired resolution, allowing stretching
        resized_clip = clip.resize(newsize=(width, height))
        
        # Write the resized video to the output file with a progress bar
        resized_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            logger='bar'  # Enables the progress bar
        )
        
        # Close the clip to release resources
        clip.close()
        return output_path
    except Exception as e:
        print(f"Error resizing video: {e}")
        return None

def hardcode_subtitles(video_path, subtitle_path, output_path):
    """
    Hardcodes subtitles into a video using FFmpeg.

    Args:
        video_path (str): Path to the input video file.
        subtitle_path (str): Path to the subtitle file.
        output_path (str): Path for the output video file with hardcoded subtitles.
    
    Returns:
        str: Path to the output video, or input video path if subtitling fails.
    """
    # If subtitle file doesn't exist, return the original video path
    if not os.path.exists(subtitle_path):
        print(f"Subtitle file not found: {subtitle_path}")
        return video_path

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
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing subtitles: {e}")
        return video_path
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        return video_path

def process_frame(frame):
    """
    Process a single video frame for e-paper display.
    
    Args:
        frame (numpy.ndarray): Video frame.
    
    Returns:
        PIL.Image: Processed image.
    """
    img = Image.fromarray(frame)
    img = ImageOps.exif_transpose(img)
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = img.convert("1", dither=Image.FLOYDSTEINBERG)
    return img

def extract_frames(video_path, output_folder, fps=1):
    """
    Extract and process frames from a video.
    
    Args:
        video_path (str): Path to the input video file.
        output_folder (str): Folder to save processed frames.
        fps (int, optional): Frames per second to extract. Defaults to 1.
    """
    if fps <= 0:
        raise ValueError("FPS must be a positive integer.")
    
    # Load the video
    with VideoFileClip(video_path) as clip:
        duration = int(clip.duration)
        os.makedirs(output_folder, exist_ok=True)
        with tqdm(total=duration // fps, desc="Processing frames", unit="frame") as pbar:
            for second in range(0, duration, fps):
                try:
                    frame = clip.get_frame(second)
                    img = process_frame(frame)
                    output_path = os.path.join(output_folder, f"frame_{second:04d}.bmp")
                    img.save(output_path, format="BMP")
                    pbar.update(1)
                except Exception as e:
                    print(f"Error processing frame at {second}s: {e}")
    print(f"Frame extraction complete! Frames saved in '{output_folder}'.")

def process_video(input_video, output_prefix, subtitle_file=None, fps=1):
    """
    Main processing function to handle entire video workflow.
    
    Args:
        input_video (str): Path to the input video file.
        output_prefix (str): Prefix for output files.
        subtitle_file (str, optional): Path to subtitle file.
        fps (int, optional): Frames per second to extract. Defaults to 1.
    """
    # Resize video
    resized_video = f"{output_prefix}_resized.mp4"
    resize_video(input_video, resized_video)

    # Hardcode subtitles if provided
    video_with_subtitles = resized_video
    if subtitle_file:
        video_with_subtitles = f"{output_prefix}_subtitled.mp4"
        video_with_subtitles = hardcode_subtitles(resized_video, subtitle_file, video_with_subtitles)

    # Extract frames
    output_frames_folder = f"{output_prefix}_frames"
    extract_frames(video_with_subtitles, output_frames_folder, fps)

def main():
    """
    Command-line interface for video processing.
    """
    parser = argparse.ArgumentParser(description="Process video for e-paper display.")
    parser.add_argument("input_video", type=str, help="Path to the input video file.")
    parser.add_argument("output_prefix", type=str, help="Prefix for output files.")
    parser.add_argument("--subtitle", type=str, help="Optional path to subtitle file.", default=None)
    parser.add_argument("--fps", type=int, default=1, help="Frames per second to extract (default: 1).")
    
    args = parser.parse_args()

    try:
        process_video(
            args.input_video, 
            args.output_prefix, 
            subtitle_file=args.subtitle, 
            fps=args.fps
        )
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()