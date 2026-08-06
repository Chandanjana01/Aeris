# AERIS: AI-Powered Ergonomic Risk Inspection System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose_33-00C7B7?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)

**AERIS** is a computer vision and biomechanical risk assessment platform. It processes video footage to analyze human body kinematics, detect posture abnormalities, calculate dynamic joint metrics, evaluate ergonomic risk factors (knee valgus, trunk lean, symmetry, landing mechanics), and deliver structured risk reports via an asynchronous REST API or CLI pipeline.

---

## 🌟 Key Features

- ⚡ **Asynchronous REST API**: Powered by FastAPI with daemon thread execution and real-time job status polling (`POST /analyze`, `GET /status/{job_id}`, `GET /report/{job_id}`).
- 🎯 **33-Landmark AI Tracking**: Leverages MediaPipe's high-precision Pose Landmarker model to capture spatial body coordinates frame-by-frame.
- 📐 **Biomechanical Feature Extraction**: Calculates 15 real-time metrics per frame including 8 joint angles, trunk lean angle, knee valgus collapse, left-right symmetry, and 3D Center of Mass (COM).
- ⚖️ **Weighted Risk Engine**: Evaluates joint Range of Motion (ROM), stability, and form degradation to compute weighted risk scores across body regions (Knee, Spine, Hip, Fatigue).
- 🧹 **Automated Data Lifecycle**: Automatically cleans up temporary frame directories and intermediate raw CSVs post-analysis, preserving only the final structured `risk_report.json`.

---

## 🏗️ Project Architecture & Structure

```
risk-analyse/
│
├── 🌐 api/                             # REST API Layer (FastAPI)
│   ├── main.py                         # Application entry point & CORS setup
│   ├── job_store.py                    # Thread-safe in-memory job tracker
│   ├── models/
│   │   └── schemas.py                  # Pydantic request/response schemas
│   └── routes/
│       ├── analyze.py                  # POST /analyze (Video Upload)
│       ├── status.py                   # GET /status/{job_id} (Job Polling)
│       └── report.py                   # GET /report/{job_id} (Fetch Result)
│
├── 🧠 src/                             # Core Biomechanical & Vision Modules
│   ├── video_processing/
│   │   └── frame_extractor.py          # OpenCV frame extraction
│   ├── pose_analysis/
│   │   ├── landmark_analyzer.py        # MediaPipe 33-landmark detector
│   │   ├── pose_landmarks_map.py       # Body keypoint mapping definitions
│   │   └── pose_landmarker_full.task   # MediaPipe AI task model binary
│   ├── feature_extraction/
│   │   ├── feature_extractor.py        # Frame-wise feature extraction orchestrator
│   │   ├── joint_angles.py             # 8-Joint angle trigonometry
│   │   ├── trunk.py                    # Trunk lean angle calculator
│   │   ├── knee_valgus.py              # Inward knee collapse indicator
│   │   └── symmetry.py                 # Bilateral symmetry balance
│   ├── risk_assessment/
│   │   ├── movement_analyzer.py        # Movement summary & ROM calculator
│   │   ├── movement_metrics.py         # Stability, fatigue, and landing metrics
│   │   ├── risk_score.py               # Body zone risk scoring & weighted overall risk
│   │   ├── recommendations.py          # Dynamic recommendation & alert generator
│   │   ├── report_generator.py         # Report JSON formatter
│   │   └── thresholds.py               # Biomechanical risk thresholds
│   └── utils/
│       ├── geometry.py                 # Vector math, angles, COM, distance
│       ├── landmark_loader.py          # CSV landmark dataset loader
│       └── constants.py                # MediaPipe landmark indices
│
├── 🚀 scripts/
│   └── run_full_analysis.py            # Complete CLI pipeline runner with auto-cleanup
│
├── 🎬 data/                            # Persistent Data Layer
│   ├── input_videos/                   # Uploaded source videos
│   ├── output/                         # Analysis results (contains risk_report.json)
│   └── temp/                           # Temporary frame cache (auto-purged)
│
├── MIGRATION_GUIDE.md                  # System architecture migration history
├── STRUCTURE.md                        # Developer structural reference
├── README.md                           # Documentation
└── requirements.txt                    # Project Python dependencies
```

---

## ⚡ Quick Start

### 1. Environment Setup

```powershell
# Activate Virtual Environment
.\.venv\Scripts\Activate.ps1

# Install Dependencies
pip install -r requirements.txt
```

### 2. Running the REST API

Launch the Uvicorn dev server:

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

- 📌 **API Root**: `http://localhost:8000/`
- 📖 **Interactive Swagger Docs**: `http://localhost:8000/docs`

---

## 📡 REST API Workflow

### Step 1: Submit Video for Analysis

**`POST /analyze`** (Multipart Form Upload)

Upload a `.mp4`, `.avi`, `.mov`, `.mkv`, or `.wmv` video file.

```http
POST /analyze HTTP/1.1
Content-Type: multipart/form-data
```

**Response (`200 OK`):**
```json
{
  "job_id": "c9a4b812-7f41-4b10-86b1-3e4bfa02931a",
  "status": "queued",
  "message": "Analysis queued. Poll GET /status/c9a4b812-7f41-4b10-86b1-3e4bfa02931a to track progress."
}
```

---

### Step 2: Poll Execution Status

**`GET /status/{job_id}`**

```http
GET /status/c9a4b812-7f41-4b10-86b1-3e4bfa02931a HTTP/1.1
```

**Response (`200 OK`):**
```json
{
  "job_id": "c9a4b812-7f41-4b10-86b1-3e4bfa02931a",
  "status": "processing",
  "video_name": "c9a4b812-7f41-4b10-86b1-3e4bfa02931a",
  "error": null
}
```
*Possible Status Values:* `queued` | `processing` | `done` | `failed`

---

### Step 3: Retrieve Final Risk Report

**`GET /report/{job_id}`**

Fetch the generated assessment report once status reaches `done`.

```http
GET /report/c9a4b812-7f41-4b10-86b1-3e4bfa02931a HTTP/1.1
```

**Response (`200 OK`):**
```json
{
  "job_id": "c9a4b812-7f41-4b10-86b1-3e4bfa02931a",
  "video_name": "c9a4b812-7f41-4b10-86b1-3e4bfa02931a",
  "overall_risk": 47.5,
  "risk_level": "MODERATE",
  "body_part_risks": {
    "knee": 60.0,
    "hip": 30.0,
    "spine": 50.0,
    "fatigue": 0.0
  },
  "movement_scores": {
    "landing_quality": 63.4,
    "stability_score": 91.2,
    "symmetry_score": 96.1,
    "fatigue_score": 0.0
  },
  "alerts": [
    "High knee valgus detected.",
    "Poor landing mechanics."
  ],
  "recommendations": [
    "Strengthen hip abductors and improve knee alignment.",
    "Practice soft two-leg landing drills."
  ]
}
```

---

## 💻 Command Line Interface (CLI)

Run the full pipeline directly on any local video file:

```powershell
python scripts/run_full_analysis.py --video "data/input_videos/sample_workout.mp4"
```

### Optional Arguments:
- `--video`, `-v`: Path to input video file (*Required*)
- `--output`, `-o`: Custom output folder name (*Optional*)
- `--save-annotated`: Save landmark-annotated images for visual debugging (*Optional*)

---

## 📊 Biomechanical Risk Evaluation Model

### Overall Risk Score Formula

The system computes a weighted composite risk index ($0 - 100$):

$$\text{Overall Risk} = (0.40 \times \text{Knee}) + (0.25 \times \text{Spine}) + (0.20 \times \text{Hip}) + (0.15 \times \text{Fatigue})$$

### Risk Classifications

| Score Range | Risk Level | Status | Action Required |
|:---:|:---:|:---:|:---|
| **0 – 24.9** | **LOW** | 🟢 | Safe posture mechanics; minimal intervention needed |
| **25 – 49.9** | **MODERATE** | 🟡 | Minor postural deviations; preventative care advised |
| **50 – 74.9** | **HIGH** | 🟠 | High risk of mechanical strain; posture correction required |
| **75 – 100** | **VERY HIGH** | 🔴 | Severe injury hazard; immediate ergonomic intervention mandatory |

---

## 📄 License & Attribution

- **MediaPipe**: Apache License 2.0 (Google LLC)
- **OpenCV**: Apache License 2.0
- **FastAPI**: MIT License
