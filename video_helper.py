from ffmpeg import FFmpeg
import subprocess
import json
import numpy as np

def get_video_info(input_file):
    """
    Get video information including width, height, and frame count.
    
    Args:
        input_file: Path to input video file
        
    Returns:
        Dictionary with width, height, fps, and frame_count
    """
    probe_cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
        "-show_entries", "format=duration",
        "-of", "json", input_file
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    
    info = {}
    if "streams" in data and len(data["streams"]) > 0:
        stream = data["streams"][0]
        info["width"] = int(stream.get("width", 0))
        info["height"] = int(stream.get("height", 0))
        
        # Parse frame rate
        r_frame_rate = stream.get("r_frame_rate", "30/1")
        num, den = map(int, r_frame_rate.split("/"))
        info["fps"] = num / den if den != 0 else 30.0
        
        # Get frame count
        nb_frames = stream.get("nb_frames")
        if nb_frames:
            info["frame_count"] = int(nb_frames)
        else:
            # Calculate from duration
            duration = float(data.get("format", {}).get("duration", 0))
            info["frame_count"] = int(duration * info["fps"])
    
    return info


def read_video_frames(input_file, grayscale=False):
    """
    Read video frames from a file using ffmpeg and convert them to numpy arrays.
    
    Args:
        input_file: Path to input video file
        start_frame: Frame number to start reading from (0-indexed)
        num_frames: Number of frames to read. If None, reads all remaining frames
        grayscale: If True, convert frames to grayscale (single channel)
        
    Yields:
        numpy.ndarray: Each frame as a numpy array with shape (height, width, channels)
                       or (height, width) for grayscale
    """
    # Get video info
    info = get_video_info(input_file)
    width = info["width"]
    height = info["height"]
    fps = info["fps"]
    
    # Build ffmpeg command to output raw video
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-f", "rawvideo",  # Output raw video
        "-pix_fmt", "rgb24" if not grayscale else "gray",  # Pixel format
        "-"  # Output to stdout
    ]
    
    # Start ffmpeg process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=10**8
    )
    
    # Calculate frame size
    channels = 1 if grayscale else 3
    frame_size = width * height * channels
    
    frame_idx = 0
    while True:
        # Read raw frame data
        raw_frame = process.stdout.read(frame_size)
        
        if len(raw_frame) != frame_size:
            break  # End of video or incomplete frame
        
        # Convert to numpy array
        frame = np.frombuffer(raw_frame, dtype=np.uint8)
        frame = frame.reshape((height, width, channels)) if not grayscale else frame.reshape((height, width))
        
        yield frame
        frame_idx += 1
        
    process.stdout.close()
    process.stderr.close()
    process.wait()


def read_video_all_frames(input_file, grayscale=False):
    """
    Read all frames from a video file into a numpy array.
    
    Args:
        input_file: Path to input video file
        grayscale: If True, convert frames to grayscale
        
    Returns:
        numpy.ndarray: Array of frames with shape (num_frames, height, width, channels)
                       or (num_frames, height, width) for grayscale
    """
    frames = list(read_video_frames(input_file, grayscale=grayscale))
    return np.array(frames)



def split_video_by_duration(input_file, output_prefix, segment_duration_seconds):
    """
    Split a video file into segments of specified duration.
    
    Args:
        input_file: Path to input video file
        output_prefix: Prefix for output files (e.g., "segment" will create segment_001.mp4, segment_002.mp4, etc.)
        segment_duration_seconds: Duration of each segment in seconds
    """
    ffmpeg = (
        FFmpeg()
        .option("y")  # Overwrite output files
        .input(input_file)
        .output(
            f"{output_prefix}%d.avi",
            c="copy",  # Use copy to avoid re-encoding (faster)
            f="segment",
            r="20.02",
            segment_time=segment_duration_seconds,
            reset_timestamps=1
        )
    )
    
    @ffmpeg.on("progress")
    def on_progress(progress: dict):
        print(f"Progress: {progress}")
    
    ffmpeg.execute()
    print(f"Split complete! Segments saved as {output_prefix}_*.avi")


def split_video_by_frames(input_file, output_prefix, frames_per_segment, fps=None):
    """
    Split a video file into segments based on number of frames per segment.
    
    Args:
        input_file: Path to input video file
        output_prefix: Prefix for output files
        frames_per_segment: Number of frames per segment
        fps: Frame rate (FPS). If None, will be detected automatically from the video
    """
    # Get FPS if not provided
    if fps is None:
        info = get_video_info(input_file)
        fps = info["fps"]
        print(f"detected input fps: {info["fps"]}")
    
    # Calculate duration per segment in seconds
    segment_duration = frames_per_segment / fps
    print(f"Splitting into segments of {frames_per_segment} frames ({segment_duration:.3f} seconds each)")
    
    ffmpeg = (
        FFmpeg()
        .option("y")  # Overwrite output files
        .input(input_file)
        .output(
            f"{output_prefix}%3d.avi",
            c="copy",  # Use copy to avoid re-encoding (faster)
            f="segment",
            r=str(fps),  # Set frame rate explicitly
            segment_time=segment_duration,
            reset_timestamps=1
        )
    )
    
    @ffmpeg.on("progress")
    def on_progress(progress: dict):
        print(f"Progress: {progress}")
    
    ffmpeg.execute()
    print(f"Split complete! Segments saved as {output_prefix}*.avi")