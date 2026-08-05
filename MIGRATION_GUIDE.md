# Migration Guide: Old → New Structure

## 📋 What Changed?

### ✅ Benefits of New Structure
- **Clearer Organization**: Files grouped by feature, not type
- **Easier Navigation**: Find files by what they do
- **Better Workflow**: Structure mirrors the analysis pipeline
- **Single Command**: Run everything with one script
- **Professional**: Industry-standard project layout

---

## 📂 File Location Changes

### Old Location → New Location

#### Video Processing
```
opencv_extractor/extract_frames.py
    → src/video_processing/frame_extractor.py
```

#### Pose Analysis
```
mediapipe_analyzer/analyze_landmarks.py
    → src/pose_analysis/landmark_analyzer.py

mediapipe_analyzer/pose_landmarks_map.py
    → src/pose_analysis/pose_landmarks_map.py

mediapipe_analyzer/pose_landmarker_full.task
    → src/pose_analysis/pose_landmarker_full.task
```

#### Feature Extraction
```
risk_engine/complete_feature_extractor.py
    → src/feature_extraction/feature_extractor.py

risk_engine/joint_angles.py
    → src/feature_extraction/joint_angles.py

risk_engine/trunk.py
    → src/feature_extraction/trunk.py

risk_engine/knee_valgus.py
    → src/feature_extraction/knee_valgus.py

risk_engine/symmetry.py
    → src/feature_extraction/symmetry.py
```

#### Risk Assessment
```
risk_engine/movement_analyzer.py
    → src/risk_assessment/movement_analyzer.py

risk_engine/movement_metrics.py
    → src/risk_assessment/movement_metrics.py

risk_engine/risk_score.py
    → src/risk_assessment/risk_score.py

risk_engine/recommendations.py
    → src/risk_assessment/recommendations.py

risk_engine/report_generator.py
    → src/risk_assessment/report_generator.py

risk_engine/thresholds.py
    → src/risk_assessment/thresholds.py
```

#### Utilities
```
risk_engine/geometry.py
    → src/utils/geometry.py

risk_engine/landmark_loader.py
    → src/utils/landmark_loader.py

risk_engine/constants.py
    → src/utils/constants.py
```

#### Data Folders
```
videos/
    → data/input_videos/

analysis_results/
    → data/output/

output_frames/
    → data/temp/frames/
```

---

## 🔄 How to Use the New Structure

### Old Way (Multiple Commands)
```powershell
# Step 1
python opencv_extractor/extract_frames.py --video "videos/video.mp4"

# Step 2
python mediapipe_analyzer/analyze_landmarks.py --input "output_frames/video"

# Step 3
python test_feature_extractor.py

# Step 4
python test_movement_analyzer.py

# Step 5
python test_risk_engine.py
```

### New Way (Single Command) ⭐
```powershell
python scripts/run_full_analysis.py --video "data/input_videos/video.mp4"
```

**That's it!** One command does everything.

---

## 📝 Import Statement Changes

### Old Imports
```python
from risk_engine.landmark_loader import LandmarkLoader
from risk_engine.joint_angles import calculate_joint_angles
from risk_engine.trunk import calculate_trunk_lean
```

### New Imports
```python
from src.utils.landmark_loader import LandmarkLoader
from src.feature_extraction.joint_angles import calculate_joint_angles
from src.feature_extraction.trunk import calculate_trunk_lean
```

---

## 🗂️ Old vs New Structure Comparison

### OLD STRUCTURE ❌
```
risk-analyse/
├── opencv_extractor/           # Mixed with other folders
├── mediapipe_analyzer/         # Scattered organization
├── risk_engine/                # Everything in one folder
├── videos/                     # Mixed with code
├── output_frames/              # Temporary files mixed
├── analysis_results/           # Output mixed
└── test_*.py                   # Tests at root
```
**Problems:**
- ❌ Hard to find files
- ❌ Unclear purpose
- ❌ Mixed data and code
- ❌ No clear workflow

### NEW STRUCTURE ✅
```
risk-analyse/
├── src/                        # All source code
│   ├── video_processing/       # Clear: handles videos
│   ├── pose_analysis/          # Clear: analyzes poses
│   ├── feature_extraction/     # Clear: extracts features
│   ├── risk_assessment/        # Clear: assesses risk
│   └── utils/                  # Clear: shared utilities
├── scripts/                    # Workflow scripts
│   └── run_full_analysis.py    # One command to rule them all
└── data/                       # All data separate
    ├── input_videos/           # Input
    ├── temp/                   # Processing
    └── output/                 # Results
```
**Benefits:**
- ✅ Easy navigation
- ✅ Clear purpose per folder
- ✅ Separated data and code
- ✅ Workflow-oriented

---

## 🚀 Migration Checklist

If you have custom scripts using the old structure:

- [ ] Update import statements (see above)
- [ ] Move videos to `data/input_videos/`
- [ ] Update file paths in custom scripts
- [ ] Use new `scripts/run_full_analysis.py` script
- [ ] Delete old folder structure (after backup!)

---

## 📌 Important Notes

### Both Structures Work!
- ✅ Old structure still functional (backward compatible)
- ✅ New structure is cleaner and recommended
- ✅ Choose what works for you

### Gradual Migration
You can:
1. Keep using old structure
2. Migrate gradually (folder by folder)
3. Switch completely to new structure

### No Data Loss
- All original files are **copied**, not moved
- Old structure remains intact
- Safe to test new structure

---

## 🎯 Recommendation

**For new projects**: Use the new structure from the start

**For existing projects**: 
1. Test the new `scripts/run_full_analysis.py` script
2. If it works, gradually migrate
3. Keep old structure as backup until confident

---

## 💡 Quick Tips

### Find a File Quickly
**Old way**: Search through multiple folders
**New way**: Go to the feature folder

Example:
- Need risk calculation? → `src/risk_assessment/risk_score.py`
- Need geometry math? → `src/utils/geometry.py`
- Need landmark detection? → `src/pose_analysis/landmark_analyzer.py`

### Run Analysis
**Old way**: Run 5 separate scripts
**New way**: One command
```powershell
python scripts/run_full_analysis.py --video "data/input_videos/video.mp4"
```

---

## ✨ Summary

The new structure is:
- 🎯 **Clearer** - Know what each folder does
- ⚡ **Faster** - One-command execution
- 📊 **Professional** - Industry-standard layout
- 🔧 **Maintainable** - Easy to update and extend
- 👥 **Collaborative** - Easy for teams to work on

**Bottom Line**: Same functionality, better organization! 🎉
