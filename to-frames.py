import os
from moviepy.editor import VideoFileClip
from PIL import Image, ImageOps
from tqdm import tqdm

# Define output resolution for your e-paper display
FRAME_WIDTH = 400
FRAME_HEIGHT = 300

def crop_image_to_proper_ratio(img, target_width, target_height):
    width, height = img.size
    target_ratio = target_width / target_height
    if (width / height) > target_ratio:
        new_width = int(target_ratio * height)
        left = (width - new_width) // 2
        right = left + new_width
        img = img.crop((left, 0, right, height))
    elif (width / height) < target_ratio:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        img = img.crop((0, top, width, bottom))
    return img

def process_frame(frame):
    img = Image.fromarray(frame)
    img = ImageOps.exif_transpose(img)
    img = ImageOps.autocontrast(img, cutoff=2)
    img = crop_image_to_proper_ratio(img, FRAME_WIDTH, FRAME_HEIGHT)
    img = img.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = img.convert("1", dither=Image.FLOYDSTEINBERG)
    return img

def extract_frames(video_path, output_folder, fps=1):
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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract frames from an MP4 file and convert them into BMP files for an e-paper display.")
    parser.add_argument("input_video", type=str, help="Path to the input MP4 video file.")
    parser.add_argument("output_folder", type=str, help="Path to the folder where frames will be saved.")
    parser.add_argument("--fps", type=int, default=1, help="Frames per second to extract (default: 1).")
    args = parser.parse_args()

    try:
        extract_frames(args.input_video, args.output_folder, args.fps)
    except Exception as e:
        print(f"An error occurred: {e}")
