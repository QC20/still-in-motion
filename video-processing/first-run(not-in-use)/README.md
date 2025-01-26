# Video to E-Paper Frame Processor

## Overview

This script processes video files for e-paper display, performing three key operations:
- Resize video to a fixed resolution (400x300)
- Optionally hardcode subtitles
- Extract frames as BMP files for e-paper display

## Prerequisites

### Software Requirements
- Python 3.7+
- FFmpeg installed on your system
- pip package manager

### Installation

1. Clone the repository
2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure FFmpeg is installed:
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- Windows: Download from FFmpeg official website and add to system PATH

## Usage

### Basic Command

```bash
python video_processor.py <input_video_path> <output_prefix>
```

### Advanced Options

```bash
python video_processor.py <input_video_path> <output_prefix> --subtitle <subtitles_path> --fps <frames_per_second>
```

### Parameters

- `<input_video_path>`: Full path to your source video file
- `<output_prefix>`: Prefix for output files and folders
- `--subtitle`: (Optional) Path to SRT subtitle file
- `--fps`: (Optional) Frames extracted per second (default: 1)

## Example

```bash
# Process movie without subtitles
python video_processor.py /path/to/movie.mp4 my_movie_output

# Process movie with subtitles at 2 frames per second
python video_processor.py /path/to/movie.mp4 my_movie_output --subtitle /path/to/subtitles.srt --fps 2
```

## Output

The script will generate:
- Resized video file
- Optional subtitled video file
- Folder with BMP frames processed for e-paper display

## Troubleshooting

- Ensure all file paths are correct and absolute
- Check that input video and optional subtitle files exist
- Verify FFmpeg is installed and accessible in system PATH
- Confirm all Python dependencies are installed