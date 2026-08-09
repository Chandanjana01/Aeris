# AERIS: AI-Powered Ergonomic Risk Inspection System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Groq LLM](https://img.shields.io/badge/Groq-Llama_3.3_70B-f55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose_33-00C7B7?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)

**AERIS** is a computer vision, biomechanical risk assessment, and AI physical therapy platform. It processes video footage to analyze human body kinematics, detect posture abnormalities, calculate dynamic joint metrics, evaluate ergonomic risk factors (knee valgus, trunk lean, symmetry, landing mechanics), and deliver personalized Groq LLM-powered corrective exercise protocols via an asynchronous REST API, interactive web dashboard, or CLI pipeline.

---

## 🌟 Key Features

- 🤖 **Groq LLM Physical Therapy Engine**: Powered by Groq's `llama-3.3-70b-versatile` model to transform raw kinematic metrics into tailored physical therapy routines, set/rep targets, coaching cues, posture fixes, and recovery protocols (with automated rule-engine fallback).
- ⚡ **Asynchronous REST API**: Powered by FastAPI with daemon thread execution and real-time job status polling (`POST /analyze`, `GET /status/{job_id}`, `GET /report/{job_id}`).
- 🔐 **User Authentication & Accounts**: SQLite database integration (`data/aeris.db`) with PBKDF2 SHA-256 password hashing for sign-up, sign-in, session state, and one-click user logout.
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
│   ├── db.py                           # SQLite DB initialization & thread-safe helper
│   ├── job_store.py                    # Thread-safe in-memory job tracker
│   ├── models/
│   │   └── schemas.py                  # Pydantic request/response schemas
│   └── routes/
│       ├── analyze.py                  # POST /analyze (Video Upload)
│       ├── auth.py                     # POST /signup, POST /login (Auth)
│       ├── recommendations.py          # POST /recommendations/generate (Groq LLM)
│       ├── report.py                   # GET /report/{job_id} (Fetch Result)
│       └── status.py                   # GET /status/{job_id} (Job Polling)
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
   │   ├── knee_valgus.py              # Inward knee collapse indicator
│   │   └── symmetry.py                 # Bilateral symmetry balance
│   ├── risk_assessment/
│   │   ├── llm_recommendations.py      # Groq LLM physical therapy recommendation engine
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
├── 🎨 frontend/                        # Web Dashboard UI
│   ├── index.html                      # Athlete Performance Dashboard
│   ├── reports.html                    # Historical Reports & Analytics
│   ├── login.html                      # Sign Up / Sign In Page
│   ├── app.js                          # Dashboard JavaScript controller & LLM renderer
│   ├── reports.js                      # Reports JavaScript controller & Modal viewer
│   └── auth.js                         # Authentication UI controller
│
├── 🚀 scripts/
│   ├── run_full_analysis.py            # Complete CLI pipeline runner with auto-cleanup
│   └── test_groq_recommendations.py    # Test script for Groq LLM integration
│
├── 🎬 data/                            # Persistent Data Layer
│   ├── aeris.db                        # SQLite user database
│   ├── input_videos/                   # Uploaded source videos
│   ├── output/                         # Analysis results (contains risk_report.json)
│   └── temp/                           # Temporary frame cache (auto-purged)
│
├── .env                                # API keys & configuration
├── requirements.txt                    # Project Python dependencies
└── README.md                           # Documentation
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

### 2. Groq LLM Configuration

Set your Groq API Key in `.env`:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Running the REST API & Dashboard

Launch the Uvicorn dev server:

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

- 🌐 **Interactive Dashboard**: [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)
- 📖 **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 REST API Workflow

### Step 1: User Authentication (Optional)

**`POST /login`** or **`POST /signup`**

```http
POST /login HTTP/1.1
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password123"
}
```

---

### Step 2: Submit Video for Analysis

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

### Step 3: Poll Execution Status

**`GET /status/{job_id}`**

```http
GET /status/c9a4b812-7f41-4b10-86b1-3e4bfa02931a HTTP/1.1
```

*Possible Status Values:* `queued` | `processing` | `done` | `failed`

---

### Step 4: Retrieve Final Risk Report with Groq LLM Recommendations

**`GET /report/{job_id}`**

```http
GET /report/c9a4b812-7f41-4b10-86b1-3e4bfa02931a HTTP/1.1
```

**Response (`200 OK`):**
```json
{
  "job_id": "c9a4b812-7f41-4b10-86b1-3e4bfa02931a",
  "video_name": "c9a4b812-7f41-4b10-86b1-3e4bfa02931a",
  "overall_risk": 46.19,
  "risk_level": "MODERATE",
  "body_part_risks": {
    "knee": 60.0,
    "hip": 30.0,
    "spine": 50.0,
    "fatigue": 34.0
  },
  "movement_scores": {
    "landing_quality": 62.5,
    "stability_score": 65.0,
    "symmetry_score": 81.2,
    "fatigue_score": 34.0
  },
  "alerts": [
    "Knee valgus collapse detected (Peak: 16.4°)."
  ],
  "recommendations": [
    "Strengthen hip abductors (gluteus medius) and focus on keeping knees aligned over toes."
  ],
  "llm_recommendations": {
    "engine": "Groq LLM (llama-3.3-70b-versatile)",
    "executive_summary": "The client's biomechanical analysis reveals a moderate risk state due to knee valgus collapse and hard landing impact. Targeted corrective exercises are recommended to prevent joint strain.",
    "corrective_exercises": [
      {
        "name": "Single-Leg Squat",
        "target_area": "Hip Abductors & Knee Stability",
        "sets_reps": "3 sets x 10 reps/side",
        "description": "Slowly lower body on one leg keeping knee aligned over second toe.",
        "coaching_cue": "Focus on maintaining stable hip alignment without inward valgus collapse."
      }
    ],
    "posture_and_ergonomics": [
      "Maintain neutral spine stack during daily activities."
    ],
    "recovery_protocol": [
      "Incorporate foam rolling and active cooldown stretching."
    ]
  }
}
```

---

### Step 5: Generate Custom AI Recommendations On Demand

**`POST /recommendations/generate`**

Trigger Groq LLM recommendation generation on demand for any job or custom metrics:

```http
POST /recommendations/generate HTTP/1.1
Content-Type: application/json

{
  "summary_override": {
    "video_name": "squat_test.mp4",
    "peak_knee_valgus": 18.2,
    "landing_quality": 60.0
  }
}
```

---

## 💻 Command Line Interface (CLI)

Run the full pipeline directly on any local video file:

```powershell
python scripts/run_full_analysis.py --video "data/input_videos/sample_workout.mp4"
```

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

- **Groq LLM API**: Apache 2.0 / Groq Terms
- **MediaPipe**: Apache License 2.0 (Google LLC)
- **OpenCV**: Apache License 2.0
- **FastAPI**: MIT License

