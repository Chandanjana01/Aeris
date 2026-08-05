import os
# pyrefly: ignore [missing-import]
import cv2
import json
import argparse
from pathlib import Path
import pandas as pd
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

from src.pose_analysis.pose_landmarks_map import (
    POSE_LANDMARKS_33,
    get_landmark_name,
)

def analyze_pose_on_image(image, detector):
    """
    Runs MediaPipe pose estimation on an in-memory BGR image using the new tasks API.

    Returns:
        tuple: (pose_landmarks, list_of_landmark_dicts)
    """
    # Convert BGR to RGB for MediaPipe
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    
    detection_result = detector.detect(mp_image)

    landmarks_list = []
    pose_landmarks = None
    
    if detection_result.pose_landmarks:
        pose_landmarks = detection_result.pose_landmarks[0]  # Get first detected pose
        for idx, landmark in enumerate(pose_landmarks):
            name = get_landmark_name(idx)
            landmarks_list.append({
                "id": idx,
                "name": name,
                "x": round(landmark.x, 5),
                "y": round(landmark.y, 5),
                "z": round(landmark.z, 5),
                "visibility": round(landmark.visibility, 5)
            })

    return pose_landmarks, landmarks_list


def draw_landmarks_with_names(image, pose_landmarks, show_names=True):
    """
    Draws pose landmarks on the image along with text labels for key landmark names.
    """
    annotated_image = image.copy()
    h, w, _ = annotated_image.shape

    if pose_landmarks:
        # Draw connections manually
        connections = vision.PoseLandmarksConnections.POSE_LANDMARKS
        
        # Draw connections (lines between landmarks)
        for connection in connections:
            start_idx = connection.start
            end_idx = connection.end
            if start_idx < len(pose_landmarks) and end_idx < len(pose_landmarks):
                start_landmark = pose_landmarks[start_idx]
                end_landmark = pose_landmarks[end_idx]
                
                start_point = (int(start_landmark.x * w), int(start_landmark.y * h))
                end_point = (int(end_landmark.x * w), int(end_landmark.y * h))
                
                cv2.line(annotated_image, start_point, end_point, (0, 255, 0), 2)
        
        # Draw landmark points
        for idx, landmark in enumerate(pose_landmarks):
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(annotated_image, (cx, cy), 4, (0, 0, 255), -1)
            cv2.circle(annotated_image, (cx, cy), 6, (255, 255, 255), 1)
            
            if show_names and landmark.visibility > 0.5:
                name = get_landmark_name(idx)
                # Draw a small text tag next to the landmark point
                cv2.putText(
                    annotated_image,
                    f"{idx}:{name}",
                    (cx + 4, cy - 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    (0, 255, 255),  # Yellow color
                    1,
                    cv2.LINE_AA
                )

    return annotated_image


def process_frames_directory(input_dir: str, output_dir: str = None, min_detection_confidence: float = 0.5, save_annotated: bool = False):
    """
    Processes all extracted image frames in a folder, detecting 33 pose landmarks,
    generating annotated output images (optional), and exporting JSON/CSV data.
    
    Args:
        input_dir: Directory containing extracted frames
        output_dir: Output directory for results
        min_detection_confidence: Minimum confidence threshold for pose detection
        save_annotated: If True, saves annotated images. If False, skips annotation (faster, saves space)
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    # Collect image files
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    image_files = sorted([f for f in input_path.iterdir() if f.suffix.lower() in valid_extensions])

    if not image_files:
        print(f"No image frames found in directory: {input_dir}")
        return

    # Setup output paths
    if output_dir is None:
        output_path = Path("analysis_results") / input_path.name
    else:
        output_path = Path(output_dir)

    # Only create annotated_frames directory if needed
    if save_annotated:
        annotated_dir = output_path / "annotated_frames"
        annotated_dir.mkdir(parents=True, exist_ok=True)
    else:
        # Just create the output directory
        output_path.mkdir(parents=True, exist_ok=True)

    print(f"==================================================")
    print(f" MediaPipe 33 Landmark Analyzer")
    print(f"==================================================")
    print(f"Input Folder     : {input_path.resolve()}")
    print(f"Output Folder    : {output_path.resolve()}")
    print(f"Frames Found     : {len(image_files)}")
    print(f"--------------------------------------------------")

    # Check for model file
    model_path = Path(__file__).parent / "pose_landmarker_full.task"
    if not model_path.exists():
        print(f"ERROR: Model file not found at {model_path}")
        print("Please download pose_landmarker_full.task from MediaPipe")
        return

    # Initialize MediaPipe Pose Landmarker with new tasks API
    base_options = python.BaseOptions(model_asset_path=str(model_path))
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        min_pose_detection_confidence=min_detection_confidence
    )
    detector = vision.PoseLandmarker.create_from_options(options)

    all_frames_data = []
    csv_rows = []

    for idx, img_file in enumerate(image_files, 1):
        image = cv2.imread(str(img_file))
        if image is None:
            continue

        pose_landmarks, landmarks_list = analyze_pose_on_image(image, detector)

        # Record JSON structure
        frame_entry = {
            "frame_name": img_file.name,
            "landmarks_detected_count": len(landmarks_list),
            "landmarks": landmarks_list
        }
        all_frames_data.append(frame_entry)

        # Record CSV rows
        for lm in landmarks_list:
            csv_rows.append({
                "frame_name": img_file.name,
                "landmark_id": lm["id"],
                "landmark_name": lm["name"],
                "x": lm["x"],
                "y": lm["y"],
                "z": lm["z"],
                "visibility": lm["visibility"]
            })

        # Draw annotations (only if requested)
        if save_annotated:
            annotated_img = draw_landmarks_with_names(image, pose_landmarks)
            cv2.imwrite(str(annotated_dir / img_file.name), annotated_img)

        if idx % 20 == 0 or idx == len(image_files):
            detected_text = f"{len(landmarks_list)} landmarks" if landmarks_list else "No pose detected"
            print(f"Processed frame [{idx}/{len(image_files)}] - {img_file.name}: {detected_text}")

    detector.close()

    # Export JSON
    json_path = output_path / "landmarks_33_data.json"
    with open(json_path, "w") as f:
        json.dump(all_frames_data, f, indent=4)

    # Export CSV
    csv_path = output_path / "landmarks_33_data.csv"
    df = pd.DataFrame(csv_rows)
    df.to_csv(csv_path, index=False)

    print(f"--------------------------------------------------")
    print(f"Analysis Complete!")
    if save_annotated:
        print(f"Annotated Frames Saved To : {annotated_dir.resolve()}")
    else:
        print(f"Annotated frames: SKIPPED (save_annotated=False)")
    print(f"JSON Landmark Data Saved  : {json_path.name}")
    print(f"CSV Landmark Data Saved   : {csv_path.name}")
    print(f"==================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MediaPipe 33 Landmark Pose Analyzer")
    parser.add_argument("--input", "-i", type=str, default=None, help="Input directory containing extracted frames")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output directory for annotated frames and data")
    parser.add_argument("--confidence", "-c", type=float, default=0.5, help="Min detection confidence threshold (0.0 to 1.0)")
    parser.add_argument("--save-annotated", action="store_true", help="Save annotated images with landmarks drawn (default: False)")

    args = parser.parse_args()

    input_dir = args.input
    if input_dir is None:
        # Search for any frame subfolder inside output_frames/
        frames_base = Path("output_frames")
        if frames_base.exists():
            subdirs = [d for d in frames_base.iterdir() if d.is_dir()]
            if subdirs:
                input_dir = str(subdirs[0])
                print(f"No input folder specified. Automatically selecting: {input_dir}")
        
        if input_dir is None:
            print("Error: No input frames directory specified.")
            print("Usage example: python analyze_landmarks.py --input output_frames/sample_video")
            exit(1)

    process_frames_directory(
        input_dir=input_dir,
        output_dir=args.output,
        min_detection_confidence=args.confidence,
        save_annotated=args.save_annotated
    )
