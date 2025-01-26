from moviepy.editor import VideoFileClip

def resize_video_with_progress(input_path, output_path, width=400, height=300):
    # Load the video file
    clip = VideoFileClip("C:/Users/HCC Developer/Downloads/Fantastic.Planet.1973.FRENCH.REMASTERED.1080p.BluRay.DDP2.0.x265.10bit-GalaxyRG265[TGx]/Fantastic.Planet.1973.FRENCH.REMASTERED.1080p.BluRay.DDP2.0.x265.10bit-GalaxyRG265.mkv")
    
    # Resize the video to the desired resolution
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

# Example usage
if __name__ == "__main__":
    input_video = "C:/Users/HCC Developer/Downloads/Fantastic.Planet.1973.FRENCH.REMASTERED.1080p.BluRay.DDP2.0.x265.10bit-GalaxyRG265[TGx]/Fantastic.Planet.1973.FRENCH.REMASTERED.1080p.BluRay.DDP2.0.x265.10bit-GalaxyRG265.mkv"  # Replace with the path to your input video file
    output_video = "/Users/HCC Developer/Desktop/output_film"  # Replace with the desired output file path
    resize_video_with_progress(input_video, output_video)
