"""
Complete Workflow Script: Video → Risk Report
Runs the entire analysis pipeline automatically
"""

import sys
import os
from pathlib import Path

# Add project root to path so src package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.video_processing.frame_extractor import extract_frames
from src.pose_analysis.landmark_analyzer import process_frames_directory
from src.feature_extraction.feature_extractor import extract_complete_features
from src.risk_assessment.movement_analyzer import analyze_movement
from src.risk_assessment.report_generator import generate_report, save_report
import pandas as pd


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
        print(f"❌ Error: Video file not found: {video_path}")
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
        print("\n[1/5] Extracting frames from video...")
        extract_frames(str(video_path), frames_dir, frame_interval=1)
        
        # Step 2: Analyze Landmarks
        print("\n[2/5] Analyzing pose landmarks...")
        process_frames_directory(
            frames_dir, 
            f"data/output/{output_name}",
            min_detection_confidence=0.5,
            save_annotated=save_annotated
        )
        
        # Step 3: Extract Features
        print("\n[3/5] Extracting biomechanical features...")
        extract_complete_features(landmarks_csv, features_csv)
        
        # Step 4: Analyze Movement
        print("\n[4/5] Analyzing movement patterns...")
        analyze_movement(features_csv, summary_csv)
        
        # Step 5: Generate Risk Report
        print("\n[5/5] Generating risk assessment report...")
        df = pd.read_csv(summary_csv)
        report = generate_report(df.iloc[0])
        save_report(report, report_json)
        
        # Print Summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE!")
        print("="*60)
        print(f"\n📊 Overall Risk Score: {report['overall_risk']}/100")
        print(f"🎯 Risk Level: {report['risk_level']}")
        print(f"\n📁 Output Location: data/output/{output_name}/")
        print(f"   - landmarks_33_data.csv")
        print(f"   - frame_features.csv")
        print(f"   - movement_summary.csv")
        print(f"   - risk_report.json")
        
        if report['alerts']:
            print(f"\n⚠️  {len(report['alerts'])} Alert(s) Detected")
        
        print("\n" + "="*60)
        
        return report
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
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
