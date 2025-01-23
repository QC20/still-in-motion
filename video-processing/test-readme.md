# Advanced Video to E-Paper Frame Processor

## Features

- Resize videos to custom dimensions
- Optional subtitle hardcoding
- Frame extraction with advanced processing
- Flexible command-line interface
- Robust error handling

## Prerequisites

### Requirements
- Python 3.7+
- FFmpeg installed and accessible in system PATH
- pip package manager

## Installation

1. Clone repository
2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Basic Command
```bash
python video_processor.py <input_video> <output_prefix>
```

### Advanced Options
```bash
python video_processor.py <input_video> <output_prefix> 
    [--subtitle SUBTITLE] 
    [--fps FPS] 
    [--width WIDTH] 
    [--height HEIGHT] 
    [--keep-intermediate]
```

### Parameters

| Option | Description | Default |
|--------|-------------|---------|
| `input_video` | Source video file | Required |
| `output_prefix` | Output files prefix | Required |
| `--subtitle` | Optional subtitle file path | None |
| `--fps` | Frames per second | 1 |
| `--width` | Output frame width | 400 |
| `--height` | Output frame height | 300 |
| `--keep-intermediate` | Retain intermediate files | False |

## Examples

```bash
# Basic video processing
python video_processor.py movie.mp4 output

# With subtitles and custom resolution
python video_processor.py movie.mp4 output \
    --subtitle english.srt \
    --width 800 \
    --height 600 \
    --fps 2

# Preserve intermediate files for debugging
python video_processor.py movie.mp4 output --keep-intermediate
```

## New Improvements

### Error Handling
- Comprehensive FFmpeg availability check
- Detailed error messages
- Graceful handling of missing subtitle files

### Flexibility
- Custom output resolution
- Configurable frame extraction rate
- Optional intermediate file preservation

### Performance
- Efficient resource management
- Temporary file handling
- Minimal system footprint

## Troubleshooting
- Ensure FFmpeg is installed and in system PATH
- Verify input video and subtitle file paths
- Check file permissions
- Use `--keep-intermediate` for debugging

## Requirements
- Python dependencies managed via `requirements.txt`
- System-level FFmpeg dependency

## Compatibility
- Cross-platform support (Windows, macOS, Linux)
- Tested with various video formats and resolutions