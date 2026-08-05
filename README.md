# AERIS: AI-Powered Ergonomic Risk Inspection System

An AI-powered computer vision system that analyzes human movements from video recordings, detects ergonomic hazards, evaluates posture using pose estimation, calculates ergonomic risk scores (REBA/RULA), and generates actionable assessment reports.

## 📋 Features

- **Video Processing**: Extract frames from video files
- **Pose Detection**: AI-powered 33-landmark body tracking using MediaPipe
- **Biomechanical Analysis**: Calculate joint angles, trunk lean, knee valgus, symmetry
- **Risk Assessment**: Automated scoring for knee, hip, spine, and fatigue risks
- **Comprehensive Reports**: Generate detailed risk reports with recommendations

---

## 🚀 Quick Start

### 1. Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Process a Video (Complete Workflow)

#### Step 1: Extract Frames
```powershell
python opencv_extractor/extract_frames.py --video "videos/YOUR_VIDEO.mp4"
```

#### Step 2: Analyze Landmarks (WITHOUT Annotated Images - Faster & Saves Space)
```powershell
python mediapipe_analyzer/analyze_landmarks.py --input "output_frames/YOUR_VIDEO"
```

**Note**: By default, annotated images are NOT saved. This is faster and saves disk space.

#### Step 2 (Alternative): Analyze Landmarks WITH Annotated Images
```powershell
python mediapipe_analyzer/analyze_landmarks.py --input "output_frames/YOUR_VIDEO" --save-annotated
```

Use `--save-annotated` flag only if you need visual verification images.

#### Step 3: Extract Complete Features
```powershell
python -c "from risk_engine.complete_feature_extractor import extract_complete_features; extract_complete_features(r'analysis_results\YOUR_VIDEO\landmarks_33_data.csv', r'analysis_results\YOUR_VIDEO\frame_features.csv')"
```

#### Step 4: Analyze Movement
```powershell
python -c "from risk_engine.movement_analyzer import analyze_movement; analyze_movement(r'analysis_results\YOUR_VIDEO\frame_features.csv', r'analysis_results\YOUR_VIDEO\movement_summary.csv')"
```

#### Step 5: Generate Risk Report
```powershell
python -c "from risk_engine.report_generator import generate_report, save_report; import pandas as pd; df = pd.read_csv(r'analysis_results\YOUR_VIDEO\movement_summary.csv'); report = generate_report(df.iloc[0]); save_report(report, r'analysis_results\YOUR_VIDEO\risk_report.json'); print(report)"
```

---

## 📁 Output Files

After processing a video, you'll get:

### Essential Files (Always Generated)
- `landmarks_33_data.csv` - Raw 33 body landmark coordinates per frame
- `landmarks_33_data.json` - Same data in JSON format
- `frame_features.csv` - 15 biomechanical features per frame
- `movement_summary.csv` - Aggregated movement metrics
- `risk_report.json` - Final risk assessment with recommendations

### Optional Files (Only if --save-annotated flag is used)
- `annotated_frames/` - Images with landmarks drawn (for visual verification)

---

## 🎯 Annotated Images - When Do You Need Them?

### ❌ **You DON'T Need Them For:**
- Risk analysis calculations
- Feature extraction
- Movement analysis
- Report generation
- Production use

### ✅ **You NEED Them Only For:**
- Visual debugging (checking if pose detection worked)
- Quality control (verifying landmark accuracy)
- Presentations (showing clients/researchers the detected poses)
- Research publications (demonstrating the system)

---

## ⚙️ Command Options

### Extract Frames
```powershell
python opencv_extractor/extract_frames.py --video "videos/video.mp4" --interval 5 --format png
```
- `--video` or `-v`: Path to input video file
- `--interval` or `-i`: Frame interval (1=all frames, 5=every 5th frame)
- `--format` or `-f`: Output format (jpg or png)

### Analyze Landmarks
```powershell
python mediapipe_analyzer/analyze_landmarks.py --input "output_frames/video" --confidence 0.7 --save-annotated
```
- `--input` or `-i`: Directory containing extracted frames
- `--confidence` or `-c`: Min detection confidence (0.0 to 1.0, default=0.5)
- `--save-annotated`: Save annotated images (default=False, omit to skip)

---

## 📊 Risk Assessment Categories

### Overall Risk Score (0-100)
- **0-25**: Low Risk ✅
- **25-50**: Moderate Risk ⚠️
- **50-75**: High Risk 🔴
- **75-100**: Very High Risk 🚨

### Body Part Risks
- **Knee Risk**: Based on knee valgus, ROM, and landing quality
- **Hip Risk**: Based on symmetry and hip ROM
- **Spine Risk**: Based on trunk lean and stability
- **Fatigue Risk**: Based on performance degradation over time

---

## 🔧 System Requirements

- Python 3.10+
- Windows OS (current setup)
- Webcam or video files
- Minimum 4GB RAM
- MediaPipe-compatible CPU

---

## 📦 Dependencies

All dependencies are pre-installed in `.venv`:
- opencv-python >= 4.8.0
- mediapipe >= 0.10.0
- numpy >= 1.24.0
- pandas >= 2.0.0
- Pillow >= 10.0.0
- openpyxl >= 3.1.0

---

## 💡 Performance Tips

### Faster Processing (Recommended for Production)
```powershell
# Skip annotated images (default behavior)
python mediapipe_analyzer/analyze_landmarks.py --input "output_frames/video"
```
**Benefits:**
- ✅ 2-3x faster processing
- ✅ Saves 100-500 MB disk space per video
- ✅ No quality loss in analysis

### Extract Fewer Frames
```powershell
# Extract every 5th frame instead of all frames
python opencv_extractor/extract_frames.py --video "videos/video.mp4" --interval 5
```
**Benefits:**
- ✅ 5x faster processing
- ✅ 5x less disk space
- ⚠️ Lower temporal resolution

---

## 📝 Example Usage

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Process a workout video (FAST - no annotated images)
python opencv_extractor/extract_frames.py --video "videos/workout.mp4"
python mediapipe_analyzer/analyze_landmarks.py --input "output_frames/workout"

# Extract features and analyze
python test_feature_extractor.py    # (modify paths in file)
python test_movement_analyzer.py    # (modify paths in file)
python test_risk_engine.py          # (modify paths in file)
```

---

## 🎓 Use Cases

- **Ergonomic Assessments**: Workplace movement analysis
- **Sports Performance**: Athletic technique evaluation
- **Physical Therapy**: Rehabilitation progress tracking
- **Injury Prevention**: Risk identification and monitoring
- **Research**: Biomechanical studies

---

## 🆘 Troubleshooting

### "No module named 'cv2'" Error
```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1
```

### "No video specified" Error
```powershell
# Make sure video file exists in videos/ folder
dir videos\
```

### Slow Processing
```powershell
# Skip annotated images (default)
python mediapipe_analyzer/analyze_landmarks.py --input "output_frames/video"

# OR extract fewer frames
python opencv_extractor/extract_frames.py --video "videos/video.mp4" --interval 5
```

---

## 📂 Project Structure

```
risk analyse/
├── videos/                          # Input videos
├── output_frames/                   # Extracted frames (temporary)
├── analysis_results/                # Final outputs
│   └── VIDEO_NAME/
│       ├── landmarks_33_data.csv   # Raw landmarks
│       ├── frame_features.csv      # Biomechanical features
│       ├── movement_summary.csv    # Movement metrics
│       ├── risk_report.json        # Risk assessment
│       └── annotated_frames/       # (Optional) Visual verification
├── opencv_extractor/                # Video → Frames
├── mediapipe_analyzer/              # Frames → Landmarks
├── risk_engine/                     # Analysis & Risk Assessment
├── test_*.py                        # Test scripts
└── .venv/                          # Python environment
```

---

## ✅ Best Practices

1. **For Production**: Always run WITHOUT --save-annotated flag
2. **For Debugging**: Use --save-annotated only when troubleshooting
3. **For Research**: Save annotated images for documentation
4. **For Speed**: Extract every 3-5 frames instead of all frames
5. **For Accuracy**: Use --confidence 0.7 or higher

---

## 📄 License

This project uses:
- MediaPipe (Apache 2.0)
- OpenCV (Apache 2.0)
- Pandas, NumPy (BSD)

---

## 🎉 Ready to Use!

The system is fully configured and ready for production use. All changes are permanent and work in any Python IDE or environment.
