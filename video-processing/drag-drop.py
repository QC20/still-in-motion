import os
import sys
import shutil
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy.editor import VideoFileClip
from PIL import Image, ImageOps
from tqdm import tqdm

class VideoProcessorApp:
    def __init__(self, master):
        self.master = master
        master.title("E-Paper Video Processor")
        master.geometry("500x600")
        
        self.create_widgets()

    def create_widgets(self):
        # Input Video
        tk.Label(self.master, text="Input Video:").pack(pady=(10,0))
        self.input_video_path = tk.StringVar()
        input_frame = tk.Frame(self.master)
        input_frame.pack(pady=5)
        
        tk.Entry(input_frame, textvariable=self.input_video_path, width=50).pack(side=tk.LEFT, padx=(0,5))
        tk.Button(input_frame, text="Browse", command=self.browse_input_video).pack(side=tk.LEFT)

        # Subtitle File (Optional)
        tk.Label(self.master, text="Subtitle File (Optional):").pack(pady=(10,0))
        self.subtitle_path = tk.StringVar()
        subtitle_frame = tk.Frame(self.master)
        subtitle_frame.pack(pady=5)
        
        tk.Entry(subtitle_frame, textvariable=self.subtitle_path, width=50).pack(side=tk.LEFT, padx=(0,5))
        tk.Button(subtitle_frame, text="Browse", command=self.browse_subtitle).pack(side=tk.LEFT)

        # Configuration Frame
        config_frame = tk.Frame(self.master)
        config_frame.pack(pady=10)

        # FPS
        tk.Label(config_frame, text="Frames per Second:").grid(row=0, column=0, padx=5)
        self.fps = tk.DoubleVar(value=1)
        tk.Entry(config_frame, textvariable=self.fps, width=10).grid(row=0, column=1, padx=5)

        # Width
        tk.Label(config_frame, text="Frame Width:").grid(row=1, column=0, padx=5)
        self.width = tk.IntVar(value=400)
        tk.Entry(config_frame, textvariable=self.width, width=10).grid(row=1, column=1, padx=5)

        # Height
        tk.Label(config_frame, text="Frame Height:").grid(row=2, column=0, padx=5)
        self.height = tk.IntVar(value=300)
        tk.Entry(config_frame, textvariable=self.height, width=10).grid(row=2, column=1, padx=5)

        # Keep Intermediate Files
        self.keep_intermediate = tk.BooleanVar(value=False)
        tk.Checkbutton(self.master, text="Keep Intermediate Files", variable=self.keep_intermediate).pack(pady=5)

        # Process Button
        tk.Button(self.master, text="Process Video", command=self.process_video, width=20).pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.master, orient="horizontal", length=400, mode="indeterminate")
        self.progress.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(self.master, text="", wraplength=400)
        self.status_label.pack(pady=10)

    def check_ffmpeg(self):
        """Verify FFmpeg is installed and available."""
        if not shutil.which("ffmpeg"):
            raise SystemExit("FFmpeg is not installed or not in system PATH.")

    def resize_video(self, input_path, output_path, width=400, height=300):
        """Resize video with automatic resource management."""
        try:
            with VideoFileClip(input_path) as clip:
                resized_clip = clip.resize(newsize=(width, height))
                resized_clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    logger=None
                )
            return output_path
        except Exception as e:
            print(f"Error resizing video: {e}")
            return input_path

    def hardcode_subtitles(self, video_path, subtitle_path, output_path):
        """Hardcode subtitles with improved error handling."""
        if not os.path.exists(subtitle_path):
            print(f"Warning: Subtitle file not found: {subtitle_path}")
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
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error adding subtitles: {e.stderr.decode()}")
            return video_path

    def process_frame(self, frame, width=400, height=300):
        """Process a single video frame for e-paper display."""
        img = Image.fromarray(frame)
        img = ImageOps.exif_transpose(img)
        img = ImageOps.autocontrast(img, cutoff=2)
        img = img.resize((width, height), Image.LANCZOS)
        img = img.convert("1", dither=Image.FLOYDSTEINBERG)
        return img

    def extract_frames(self, video_path, output_folder, fps=1, width=400, height=300):
        """Extract frames from video with progress tracking."""
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
                        img = self.process_frame(frame, width, height)
                        
                        output_path = os.path.join(output_folder, f"frame_{frame_count:04d}.bmp")
                        img.save(output_path, format="BMP")
                        
                        frame_count += 1
                        pbar.update(1)
                    except Exception as e:
                        print(f"Error processing frame at {second}s: {e}")

    def browse_input_video(self):
        filename = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
        self.input_video_path.set(filename)

    def browse_subtitle(self):
        filename = filedialog.askopenfilename(filetypes=[("Subtitle Files", "*.srt *.vtt *.ass")])
        self.subtitle_path.set(filename)

    def process_video(self):
        input_video = self.input_video_path.get()
        subtitle = self.subtitle_path.get() or None
        
        if not input_video:
            messagebox.showerror("Error", "Please select an input video")
            return

        # Generate output prefix from input video name
        output_prefix = os.path.splitext(os.path.basename(input_video))[0]

        # Start progress
        self.progress.start()
        self.status_label.config(text="Processing video...")
        self.master.update_idletasks()

        try:
            # Check FFmpeg
            self.check_ffmpeg()
            
            # Create temporary directory for intermediate files
            with tempfile.TemporaryDirectory() as tmpdir:
                # Resize video
                resized_video = os.path.join(tmpdir, "resized.mp4")
                resized_video = self.resize_video(input_video, resized_video, self.width.get(), self.height.get())
                
                # Add subtitles if available
                video_with_subtitles = resized_video
                if subtitle:
                    video_with_subtitles = os.path.join(tmpdir, "subtitled.mp4")
                    video_with_subtitles = self.hardcode_subtitles(resized_video, subtitle, video_with_subtitles)
                
                # Extract frames
                output_frames_folder = f"{output_prefix}_frames"
                self.extract_frames(video_with_subtitles, output_frames_folder, 
                                    self.fps.get(), self.width.get(), self.height.get())
                
                # Optional: Copy intermediate files if requested
                if self.keep_intermediate.get():
                    intermediate_dir = f"{output_prefix}_intermediate"
                    os.makedirs(intermediate_dir, exist_ok=True)
                    if resized_video != input_video:
                        shutil.copy(resized_video, os.path.join(intermediate_dir, "resized.mp4"))
                    if video_with_subtitles != resized_video:
                        shutil.copy(video_with_subtitles, os.path.join(intermediate_dir, "subtitled.mp4"))
            
            # Stop progress and show success
            self.progress.stop()
            self.status_label.config(text="Video processed successfully!")
            messagebox.showinfo("Success", "Video processing completed.")
        
        except Exception as e:
            # Stop progress and show error
            self.progress.stop()
            self.status_label.config(text="Processing failed.")
            messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    app = VideoProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()