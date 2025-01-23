#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import subprocess
import tempfile
from moviepy.editor import VideoFileClip
from PIL import Image, ImageOps
from tqdm import tqdm

def check_ffmpeg():
    """
    Verify FFmpeg is installed and available.
    
    Raises:
        SystemExit: If FFmpeg is not found in system PATH
    """
    if not shutil.which("ffmpeg"):
        print("Error: FFmpeg is not installed or not in system PATH.")
        print("Please install FFmpeg and ensure it's accessible in your system's PATH.")
        sys.exit(1)

def resize_video(input_path, output_path, width=400, height=300):
    """
    Resize video with automatic resource management.
    
    Args:
        input_path (str): Path to input video
        output_path (str): Path for output video
        width (int): Desired width
        height (int): Desired height
    
    Returns:
        str: Path to resized video
    """
    try:
        with VideoFileClip(input_path) as clip:
            resized_clip = clip.resize(newsize=(width, height))
            resized_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                logger=None  # Suppress verbose output
            )
        return output_path
    except Exception as e:
        print(f"Error resizing video: {e}")
        return input_path

def hardcode_subtitles(video_path, subtitle_path, output_path):
    """
    Hardcode subtitles with improved error handling.
    
    Args:
        video_path (str): Path to input video
        subtitle_path (str): Path to subtitle file
        output_path (str): Path for output video
    
    Returns:
        str: Path to video with subtitles
    """
    if not os.path.exists(subtitle_path):
        print(f"Warning: Subtitle file not found: {subtitle_path}")
        print("Continuing without subtitles.")
        return video_path

    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={subtitle_path}",
        "-c:a", "copy",
        output_path
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"Subtitles added successfully to: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error adding subtitles: {e.stderr.decode()}")
        return video_path

def process_frame(frame, width=400, height=300):
    """
    Process a single video frame for e-paper display.
    
    Args:
        frame (numpy.ndarray): Video frame
        width (int): Target width
        height (int): Target height
    
    Returns:
        PIL.Image: Processed image
    """
    img = Image.fromarray(frame)
    img = ImageOps.exif_transpose(img)
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.resize((width, height), Image.LANCZOS)
    img = img.convert("1", dither=Image.FLOYDSTEINBERG)
    return img

def extract_frames(video_path, output_folder, fps=1, width=400, height=300):
    """
    Extract frames from video with progress tracking.
    
    Args:
        video_path (str): Path to input video
        output_folder (str): Folder to save frames
        fps (float): Frames per second to extract
        width (int): Frame width
        height (int): Frame height
    """
    if fps <= 0:
        raise ValueError("FPS must be positive")
    
    os.makedirs(output_folder, exist_ok=True)
    
    with VideoFileClip(video_path) as clip:
        duration = int(clip.duration)
        frame_count = 0
        
        with tqdm(total=duration // fps, desc="Processing Frames") as pbar:
            for second in range(0, duration, max(1, int(1/fps))):
                try:
                    frame = clip.get_frame(second)
                    img = process_frame(frame, width, height)
                    
                    output_path = os.path.join(output_folder, f"frame_{frame_count:04d}.bmp")
                    img.save(output_path, format="BMP")
                    
                    frame_count += 1
                    pbar.update(1)
                except Exception as e:
                    print(f"Error processing frame at {second}s: {e}")

def process_video(input_video, output_prefix, subtitle_file=None, fps=1, width=400, height=300, keep_intermediate=False):
    """
    Comprehensive video processing workflow.
    
    Args:
        input_video (str): Path to input video
        output_prefix (str): Output file prefix
        subtitle_file (str, optional): Path to subtitle file
        fps (float): Frames per second
        width (int): Output frame width
        height (int): Output frame height
        keep_intermediate (bool): Retain intermediate files
    """
    # Check FFmpeg availability
    check_ffmpeg()
    
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Resize video
        resized_video = os.path.join(tmpdir, "resized.mp4")
        resized_video = resize_video(input_video, resized_video, width, height)
        
        # Add subtitles if available
        video_with_subtitles = resized_video
        if subtitle_file:
            video_with_subtitles = os.path.join(tmpdir, "subtitled.mp4")
            video_with_subtitles = hardcode_subtitles(resized_video, subtitle_file, video_with_subtitles)
        
        # Extract frames
        output_frames_folder = f"{output_prefix}_frames"
        extract_frames(video_with_subtitles, output_frames_folder, fps, width, height)
        
        # Optional: Copy intermediate files if requested
        if keep_intermediate:
            intermediate_dir = f"{output_prefix}_intermediate"
            os.makedirs(intermediate_dir, exist_ok=True)
            if resized_video != input_video:
                shutil.copy(resized_video, os.path.join(intermediate_dir, "resized.mp4"))
            if video_with_subtitles != resized_video:
                shutil.copy(video_with_subtitles, os.path.join(intermediate_dir, "subtitled.mp4"))

def main():
    """Command-line interface for video processing."""
    parser = argparse.ArgumentParser(description="Process video for e-paper display")
    parser.add_argument("input_video", help="Path to input video file")
    parser.add_argument("output_prefix", help="Prefix for output files")
    parser.add_argument("--subtitle", help="Optional subtitle file path")
    parser.add_argument("--fps", type=float, default=1, help="Frames per second (default: 1)")
    parser.add_argument("--width", type=int, default=400, help="Output frame width (default: 400)")
    parser.add_argument("--height", type=int, default=300, help="Output frame height (default: 300)")
    parser.add_argument("--keep-intermediate", action="store_true", help="Keep intermediate files")
    
    args = parser.parse_args()

    try:
        process_video(
            args.input_video, 
            args.output_prefix, 
            subtitle_file=args.subtitle, 
            fps=args.fps,
            width=args.width,
            height=args.height,
            keep_intermediate=args.keep_intermediate
        )
    except Exception as e:
        print(f"Processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()