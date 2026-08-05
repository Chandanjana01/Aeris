import os
import cv2
import argparse
import json
import time
from pathlib import Path


def extract_frames(video_path: str, output_dir: str = None, frame_interval: int = 1, image_format: str = "jpg"):
    """
    Extracts frames from a video file using OpenCV.

    Args:
        video_path (str): Path to the input video file.
        output_dir (str, optional): Target directory to save extracted frames.
                                    If None, saves under 'output_frames/<video_basename>/'.
        frame_interval (int): Save every N-th frame (default=1: extract every single frame).
        image_format (str): Image format for output frames ('jpg', 'png').

    Returns:
        dict: Summary metadata about the frame extraction process.
    """
    video_file = Path(video_path)
    if not video_file.exists():
        raise FileNotFoundError(f"Input video file not found at: {video_path}")

    # Open video capture
    cap = cv2.VideoCapture(str(video_file))
    if not cap.isOpened():
        raise ValueError(f"OpenCV could not open video file: {video_path}")

    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_sec = total_frames / fps if fps > 0 else 0

    # Determine output folder
    if output_dir is None:
        video_stem = video_file.stem
        # Default to output_frames directory relative to current working directory
        output_dir = Path("output_frames") / video_stem
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"==================================================")
    print(f" OpenCV Frame Extractor")
    print(f"==================================================")
    print(f"Input Video     : {video_file.resolve()}")
    print(f"Output Directory : {output_dir.resolve()}")
    print(f"Resolution       : {width}x{height}")
    print(f"FPS              : {fps:.2f}")
    print(f"Total Frames     : {total_frames}")
    print(f"Duration         : {duration_sec:.2f} seconds")
    print(f"Frame Interval   : Every {frame_interval} frame(s)")
    print(f"--------------------------------------------------")

    frame_count = 0
    saved_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Check frame interval threshold
        if (frame_count - 1) % frame_interval == 0:
            saved_count += 1
            frame_filename = output_dir / f"frame_{saved_count:06d}.{image_format}"
            
            # Save frame image using OpenCV
            cv2.imwrite(str(frame_filename), frame)

            if saved_count % 50 == 0 or saved_count == 1:
                print(f"Saved {saved_count} frames... (Processing input frame {frame_count}/{total_frames})")

    cap.release()
    elapsed_time = time.time() - start_time

    # Save summary metadata
    metadata = {
        "video_path": str(video_file.resolve()),
        "output_directory": str(output_dir.resolve()),
        "resolution": {"width": width, "height": height},
        "fps": fps,
        "total_video_frames": total_frames,
        "extracted_frames_count": saved_count,
        "frame_interval": frame_interval,
        "processing_time_seconds": round(elapsed_time, 3),
        "duration_seconds": round(duration_sec, 2)
    }

    metadata_path = output_dir / "extraction_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"--------------------------------------------------")
    print(f"Frame Extraction Complete!")
    print(f"Total Frames Saved: {saved_count}")
    print(f"Elapsed Time      : {elapsed_time:.2f}s")
    print(f"Metadata Saved To : {metadata_path.name}")
    print(f"==================================================")

    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenCV Video Frame Extractor")
    parser.add_argument("--video", "-v", type=str, default=None, help="Path to input video file")
    parser.add_argument("--output", "-o", type=str, default=None, help="Path to output directory for frames")
    parser.add_argument("--interval", "-i", type=int, default=1, help="Frame interval rate (e.g. 1=all frames, 5=every 5th frame)")
    parser.add_argument("--format", "-f", type=str, default="jpg", choices=["jpg", "png"], help="Output image format")

    args = parser.parse_args()

    # If no video path provided, search inside videos/ folder
    video_path = args.video
    if video_path is None:
        videos_dir = Path("videos")
        video_files = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov")) + list(videos_dir.glob("*.mkv"))
        if video_files:
            video_path = str(video_files[0])
            print(f"No video path provided. Automatically selecting: {video_path}")
        else:
            print("Error: No video specified and no videos found in 'videos/' directory.")
            print("Usage example: python extract_frames.py --video ../videos/my_video.mp4")
            exit(1)

    extract_frames(
        video_path=video_path,
        output_dir=args.output,
        frame_interval=args.interval,
        image_format=args.format
    )
