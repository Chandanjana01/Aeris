# Project Structure Guide

## 📊 Visual Organization

```
risk-analyse/
│
├── 🎬 DATA LAYER (Input/Output)
│   ├── data/input_videos/          # 📥 Place videos here
│   ├── data/temp/                  # ⏳ Temporary processing files
│   └── data/output/                # 📤 Final analysis results
│
├── 🧠 SOURCE CODE (Organized by Workflow)
│   │
│   ├── src/video_processing/       # STEP 1: Video → Frames
│   │   └── frame_extractor.py      # Extract frames from video
│   │
│   ├── src/pose_analysis/          # STEP 2: Frames → Landmarks
│   │   ├── landmark_analyzer.py    # Detect 33 body landmarks
│   │   ├── pose_landmarks_map.py   # Landmark name mappings
│   │   └── pose_landmarker_full.task  # AI model file
│   │
│   ├── src/feature_extraction/     # STEP 3: Landmarks → Features
│   │   ├── feature_extractor.py    # ⭐ Main: Extract all 15 features
│   │   ├── joint_angles.py         # Calculate 8 joint angles
│   │   ├── trunk.py                # Measure trunk lean
│   │   ├── knee_valgus.py          # Measure knee alignment
│   │   └── symmetry.py             # Calculate left-right balance
│   │
│   ├── src/risk_assessment/        # STEP 4: Features → Risk Scores
│   │   ├── movement_analyzer.py    # Analyze movement patterns
│   │   ├── movement_metrics.py     # Calculate ROM, stability, etc.
│   │   ├── risk_score.py           # Calculate risk scores
│   │   ├── recommendations.py      # Generate improvement tips
│   │   ├── report_generator.py     # ⭐ Main: Generate final report
│   │   └── thresholds.py           # Risk threshold values
│   │
│   └── src/utils/                  # SHARED UTILITIES
│       ├── geometry.py             # Math: angles, distances, vectors
│       ├── landmark_loader.py      # Load landmarks from CSV
│       └── constants.py            # Landmark index constants
│
├── 🚀 WORKFLOW SCRIPTS (Easy Execution)
│   └── scripts/
│       └── run_full_analysis.py    # ⭐ ONE-COMMAND: Video → Report
│
└── 🔧 CONFIGURATION
    ├── .venv/                      # Python virtual environment
    ├── README.md                   # Documentation
    └── requirements.txt            # Python dependencies
```

---

## 🔄 Data Flow

```
INPUT                    PROCESSING STAGES                    OUTPUT
─────                    ─────────────────                    ──────

📹 Video File
    │
    │ [Step 1: video_processing]
    ▼
🖼️  Frames (312 images)
    │
    │ [Step 2: pose_analysis]
    ▼
📊 Landmarks CSV (33 points × 312 frames)
    │
    │ [Step 3: feature_extraction]
    ▼
📈 Features CSV (15 metrics × 258 frames)
    │
    │ [Step 4: risk_assessment]
    ▼
📋 Movement Summary (13 aggregate metrics)
    │
    │ [Step 5: risk_assessment]
    ▼
📄 Risk Report JSON (scores + recommendations)
```

---

## 🗂️ File Purpose Guide

### Core Workflow Files (⭐ Most Important)

| File | Purpose | Input | Output |
|------|---------|-------|--------|
| **scripts/run_full_analysis.py** | Complete pipeline | Video | Risk Report |
| **src/video_processing/frame_extractor.py** | Extract frames | Video | Frame images |
| **src/pose_analysis/landmark_analyzer.py** | Detect landmarks | Frames | landmarks_33_data.csv |
| **src/feature_extraction/feature_extractor.py** | Extract features | Landmarks CSV | frame_features.csv |
| **src/risk_assessment/movement_analyzer.py** | Analyze movement | Features CSV | movement_summary.csv |
| **src/risk_assessment/report_generator.py** | Generate report | Summary CSV | risk_report.json |

### Supporting Files

| File | Purpose | Used By |
|------|---------|---------|
| **src/feature_extraction/joint_angles.py** | Calculate 8 joint angles | feature_extractor.py |
| **src/feature_extraction/trunk.py** | Measure trunk lean | feature_extractor.py |
| **src/feature_extraction/knee_valgus.py** | Measure knee valgus | feature_extractor.py |
| **src/feature_extraction/symmetry.py** | Calculate symmetry score | feature_extractor.py |
| **src/risk_assessment/risk_score.py** | Calculate risk scores | report_generator.py |
| **src/risk_assessment/recommendations.py** | Generate tips | report_generator.py |
| **src/utils/geometry.py** | Math functions | Multiple modules |
| **src/utils/landmark_loader.py** | Load CSV data | feature_extractor.py |

---

## 📝 Naming Conventions

### Folders
- `snake_case` for all folder names
- Feature-based grouping (not by file type)

### Files
- `snake_case.py` for Python files
- Descriptive names indicating function

### Modules
- Each feature has its own folder
- Main functionality in primary file
- Supporting functions in separate files

---

## 🎯 Quick Reference

### Where to Find Things:

**Need to modify video extraction?**
→ `src/video_processing/frame_extractor.py`

**Need to adjust pose detection?**
→ `src/pose_analysis/landmark_analyzer.py`

**Need to add new biomechanical feature?**
→ `src/feature_extraction/` (create new file, update feature_extractor.py)

**Need to change risk thresholds?**
→ `src/risk_assessment/thresholds.py`

**Need to modify recommendations?**
→ `src/risk_assessment/recommendations.py`

**Need to run complete analysis?**
→ `scripts/run_full_analysis.py`

---

## 🚀 Usage Patterns

### Pattern 1: Complete Analysis (Recommended)
```powershell
python scripts/run_full_analysis.py --video "data/input_videos/video.mp4"
```
→ Runs everything automatically

### Pattern 2: Step-by-Step (For Debugging)
```powershell
# Manually run each step
python -c "from src.video_processing... # Step 1
python -c "from src.pose_analysis... # Step 2
# etc.
```
→ Run individual steps with full control

### Pattern 3: Batch Processing (Multiple Videos)
```powershell
foreach ($video in Get-ChildItem "data/input_videos/*.mp4") {
    python scripts/run_full_analysis.py --video $video.FullName
}
```
→ Process all videos in a folder

---

## ✨ Design Principles

1. **Feature-Based Organization**: Code grouped by what it does, not file type
2. **Workflow Clarity**: Folders follow the analysis pipeline
3. **Single Responsibility**: Each file has one clear purpose
4. **Easy Discovery**: Intuitive naming and structure
5. **Production Ready**: Optimized defaults, optional debugging features

---

This structure makes the codebase:
- ✅ Easier to understand
- ✅ Simpler to maintain
- ✅ More professional
- ✅ Ready for team collaboration
- ✅ Scalable for future features
