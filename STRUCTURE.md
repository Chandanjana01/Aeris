# Project Structure Guide

## 📊 Visual Organization

```
risk-analyse/
│
├── 🌐 REST API LAYER (FastAPI)
│   ├── api/
│   │   ├── main.py                 # FastAPI application server entry point & CORS
│   │   ├── job_store.py            # Thread-safe in-memory job state manager
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic data schemas for requests/responses
│   │   └── routes/
│   │       ├── analyze.py          # POST /analyze (Upload & trigger background job)
│   │       ├── status.py           # GET /status/{job_id} (Poll execution status)
│   │       └── report.py           # GET /report/{job_id} (Fetch risk report JSON)
│
├── 🎬 DATA LAYER (Input/Output & Temp Cache)
│   ├── data/input_videos/          # 📥 Uploaded or input source video files
│   ├── data/temp/                  # ⏳ Temporary frame image extraction cache (Auto-purged)
│   └── data/output/                # 📤 Final analysis directory (Retains risk_report.json)
│
├── 🧠 SOURCE CODE (Modular Core Engine)
│   │
│   ├── src/video_processing/       # STEP 1: Video → Frame Extraction
│   │   └── frame_extractor.py      # Extracts image frames using OpenCV
│   │
│   ├── src/pose_analysis/          # STEP 2: Frames → 33 Pose Landmarks
│   │   ├── landmark_analyzer.py    # MediaPipe pose detector
│   │   ├── pose_landmarks_map.py   # Landmark index to body name mappings
│   │   └── pose_landmarker_full.task  # MediaPipe AI task model file
│   │
│   ├── src/feature_extraction/     # STEP 3: Landmarks → Biomechanical Features
│   │   ├── feature_extractor.py    # ⭐ Main: Extract all 15 frame features
│   │   ├── joint_angles.py         # Trigonometric calculation of 8 joint angles
│   │   ├── trunk.py                # Measures torso/trunk lean angle
│   │   ├── knee_valgus.py          # Measures inward knee collapse angle
│   │   └── symmetry.py             # Bilateral left-right symmetry balance
│   │
│   ├── src/risk_assessment/        # STEP 4 & 5: Features → Risk Scores & Report
│   │   ├── movement_analyzer.py    # Movement pattern aggregator (ROM, peak values)
│   │   ├── movement_metrics.py     # Calculates stability, fatigue, and landing scores
│   │   ├── risk_score.py           # Evaluates region risks & overall weighted risk
│   │   ├── recommendations.py      # Generates alerts & corrective advice
│   │   ├── report_generator.py     # ⭐ Main: Builds risk_report.json
│   │   └── thresholds.py           # Biomechanical risk threshold constants
│   │
│   └── src/utils/                  # SHARED UTILITIES
│       ├── geometry.py             # Math: angle, distance, velocity, COM
│       ├── landmark_loader.py      # Parses landmark CSV datasets
│       └── constants.py            # Landmark index constants
│
├── 🚀 WORKFLOW SCRIPTS & EXECUTION
│   └── scripts/
│       └── run_full_analysis.py    # ⭐ Pipeline runner with Step 6 auto-cleanup
│
└── 🔧 CONFIGURATION
    ├── .venv/                      # Python virtual environment
    ├── README.md                   # System documentation & API reference
    ├── STRUCTURE.md                # Project structure guide
    └── requirements.txt            # Python dependencies (FastAPI, MediaPipe, OpenCV, etc.)
```

---

## 🔄 Data Flow

```
INPUT                                  PROCESSING STAGES                                   OUTPUT
─────                                  ─────────────────                                   ──────

📹 Video File
    │
    │ [Step 1: src/video_processing]
    ▼
🖼️  Frames (Extracted JPG images in data/temp/frames/<name>/)
    │
    │ [Step 2: src/pose_analysis]
    ▼
📊 Landmarks CSV (33 points × N frames)
    │
    │ [Step 3: src/feature_extraction]
    ▼
📈 Features CSV (15 metrics × N frames)
    │
    │ [Step 4: src/risk_assessment]
    ▼
📋 Movement Summary (13 aggregate metrics)
    │
    │ [Step 5: src/risk_assessment]
    ▼
📄 Risk Report JSON (Saved to data/output/<name>/risk_report.json)
    │
    │ [Step 6: Automated Cleanup]
    ▼
🧹 Purges data/temp/frames/<name>/ and intermediate CSVs
    │
    ▼
✅ Final Output: data/output/<name>/risk_report.json
```

---

## 🗂️ File Purpose Guide

### Core Workflow & API Files

| File | Purpose | Input | Output |
|------|---------|-------|--------|
| **api/main.py** | FastAPI application server | HTTP Requests | JSON Responses |
| **api/routes/analyze.py** | Upload video & start job | Video file upload | `{ job_id, status }` |
| **api/routes/status.py** | Job status polling | `job_id` | `{ status, error }` |
| **api/routes/report.py** | Fetch JSON assessment | `job_id` | `risk_report.json` |
| **scripts/run_full_analysis.py** | Complete CLI pipeline | Video path | `risk_report.json` + Auto-cleanup |
| **src/video_processing/frame_extractor.py** | Frame extraction | Video | Frame images |
| **src/pose_analysis/landmark_analyzer.py** | Pose detection | Frames | `landmarks_33_data.csv` |
| **src/feature_extraction/feature_extractor.py** | Feature extraction | Landmarks CSV | `frame_features.csv` |
| **src/risk_assessment/movement_analyzer.py** | Movement aggregation | Features CSV | `movement_summary.csv` |
| **src/risk_assessment/report_generator.py** | Report builder | Summary metrics | `risk_report.json` |

---

## 🚀 Usage Patterns

### Pattern 1: REST API (Recommended for Web/Mobile Apps)
```powershell
uvicorn api.main:app --reload
```
→ Serves `POST /analyze`, `GET /status/{job_id}`, and `GET /report/{job_id}` at `http://localhost:8000`.

### Pattern 2: Complete CLI Analysis
```powershell
python scripts/run_full_analysis.py --video "data/input_videos/sample.mp4"
```
→ Automatically runs all 6 pipeline steps, cleans up temp files, and prints summary to console.
