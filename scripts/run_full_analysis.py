"""
Complete Workflow Script: Video → Risk Report
Runs the entire analysis pipeline automatically
"""

import sys
import os
import shutil
import stat
from pathlib import Path

# Force UTF-8 output on Windows to support emoji in print statements
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path so src package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.video_processing.frame_extractor import extract_frames
from src.pose_analysis.landmark_analyzer import process_frames_directory
from src.feature_extraction.feature_extractor import extract_complete_features
from src.risk_assessment.movement_analyzer import analyze_movement
from src.risk_assessment.report_generator import generate_report, save_report
import pandas as pd


def cleanup_intermediate_files(frames_dir, landmarks_csv, features_csv, summary_csv):
    """
    Delete all intermediate files produced during the pipeline.
    Only the final risk_report.json and the output folder are kept.
    """
    print("\n[6/6] Cleaning up intermediate files...")

    # Delete extracted frames temp directory (keeps the parent temp/ folder)
    # onexc handler strips read-only flag on Windows before retrying the delete
    def _force_remove(func, path, exc):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    frames_path = Path(frames_dir)
    if frames_path.exists():
        shutil.rmtree(frames_path, onexc=_force_remove)
        print(f"   [DELETED] {frames_dir}/")
    else:
        print(f"   [SKIP] Frames dir not found: {frames_dir}")

    # Delete intermediate output files
    intermediate_files = [
        landmarks_csv,
        landmarks_csv.replace(".csv", ".json"),  # landmarks_33_data.json if present
        features_csv,
        summary_csv,
    ]

    for file_path in intermediate_files:
        p = Path(file_path)
        if p.exists():
            p.unlink()
            print(f"   [DELETED] {file_path}")

    print("   Cleanup complete. Only risk_report.json remains.")


def run_full_analysis(video_path, output_name=None, save_annotated=False):
    """
    Run complete analysis pipeline

    Args:
        video_path: Path to input video file
        output_name: Custom output folder name (optional)
        save_annotated: Whether to save annotated images (default: False)
    """

    video_file = Path(video_path)

    if not video_file.exists():
        print(f"[ERROR] Video file not found: {video_path}")
        return

    # Determine output name
    if output_name is None:
        output_name = video_file.stem

    print("="*60)
    print("ERGONOMIC RISK ANALYSIS - FULL PIPELINE")
    print("="*60)
    print(f"Video: {video_file.name}")
    print(f"Output: {output_name}")
    print("="*60)

    # Define paths
    frames_dir = f"data/temp/frames/{output_name}"
    landmarks_csv = f"data/output/{output_name}/landmarks_33_data.csv"
    features_csv = f"data/output/{output_name}/frame_features.csv"
    summary_csv = f"data/output/{output_name}/movement_summary.csv"
    report_json = f"data/output/{output_name}/risk_report.json"

    try:
        # Step 1: Extract Frames
        print("\n[1/6] Extracting frames from video...")
        extract_frames(str(video_path), frames_dir, frame_interval=1)

        # Step 2: Analyze Landmarks
        print("\n[2/6] Analyzing pose landmarks...")
        process_frames_directory(
            frames_dir,
            f"data/output/{output_name}",
            min_detection_confidence=0.5,
            save_annotated=save_annotated
        )

        # Step 3: Extract Features
        print("\n[3/6] Extracting biomechanical features...")
        extract_complete_features(landmarks_csv, features_csv)

        # Step 4: Analyze Movement
        print("\n[4/6] Analyzing movement patterns...")
        analyze_movement(features_csv, summary_csv)

        # Step 5: Generate Risk Report
        print("\n[5/6] Generating risk assessment report...")
        df = pd.read_csv(summary_csv)
        report = generate_report(df.iloc[0])
        save_report(report, report_json)

        # Step 6: Cleanup intermediate files
        cleanup_intermediate_files(frames_dir, landmarks_csv, features_csv, summary_csv)

        # Print Summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE!")
        print("="*60)
        print(f"\n[RESULT] Overall Risk Score: {report['overall_risk']}/100")
        print(f"[RESULT] Risk Level: {report['risk_level']}")
        print(f"\n[OUTPUT] Location: data/output/{output_name}/")
        print(f"   - risk_report.json  (only file retained)")

        if report['alerts']:
            print(f"\n[WARNING] {len(report['alerts'])} Alert(s) Detected")

        print("\n" + "="*60)

        return report

    except Exception as e:
        print(f"\n[ERROR] Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run complete ergonomic risk analysis")
    parser.add_argument("--video", "-v", required=True, help="Path to input video file")
    parser.add_argument("--output", "-o", default=None, help="Custom output folder name")
    parser.add_argument("--save-annotated", action="store_true", help="Save annotated images")

    args = parser.parse_args()

    run_full_analysis(args.video, args.output, args.save_annotated)
