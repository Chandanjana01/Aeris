"""
Groq LLM-Powered Biomechanical & Ergonomic Recommendation Engine.

Leverages Groq's high-speed inference API to generate personalized physical therapy,
exercise routines, posture corrections, and recovery protocols based on extracted body metrics.
"""

import json
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_default_llm_fallback(summary: Dict[str, Any], alerts: List[str]) -> Dict[str, Any]:
    """
    Dynamic fallback structured recommendation object when LLM API is unavailable.
    Tailors exercises dynamically based on video metrics and primary risk drivers.
    """
    video_name = summary.get("video_name", "Movement Analysis Video")
    overall_risk = summary.get("overall_risk", 0.0)
    risk_level = summary.get("risk_level", "LOW")
    
    knee_risk = summary.get("knee_risk", summary.get("knee", 0.0))
    spine_risk = summary.get("spine_risk", summary.get("spine", 0.0))
    hip_risk = summary.get("hip_risk", summary.get("hip", 0.0))
    fatigue_risk = summary.get("fatigue_risk", summary.get("fatigue", 0.0))

    exercises = []
    posture_tips = []
    recovery = []
    
    # Knee Risk Protocols
    if knee_risk > 30.0 or summary.get("peak_knee_valgus", 0.0) > 12.0:
        exercises.append({
            "name": f"Targeted Knee Stabilizing Clamshells ({video_name})",
            "target_area": "Gluteus Medius & Lateral Knee Alignment",
            "sets_reps": "3 sets x 15 reps per side",
            "description": f"Strengthen hip abductors to counteract the {knee_risk:.1f}% knee valgus stress detected in {video_name}.",
            "coaching_cue": "Focus on driving knee outward over second toe during knee flexion."
        })
        posture_tips.append("Avoid medial knee collapse during squatting, jumping, or direction changes.")

    # Spine Risk Protocols
    if spine_risk > 30.0 or summary.get("peak_trunk_lean", 0.0) > 18.0:
        exercises.append({
            "name": "Anti-Flexion Pallof Press & Core Bracing",
            "target_area": "Lumbar Spine & Deep Abdominals",
            "sets_reps": "3 sets x 30s holds",
            "description": f"Counteract trunk lean and lumbar flexion ({spine_risk:.1f}% spine risk factor).",
            "coaching_cue": "Maintain tall neutral spine stack without forward chest dipping."
        })
        posture_tips.append("Maintain an upright neutral spine stack during heavy load absorption.")

    # Hip Risk Protocols
    if hip_risk > 30.0 or summary.get("avg_symmetry", 100.0) < 88.0:
        exercises.append({
            "name": "Unilateral Bulgarian Split Squats",
            "target_area": "Hip Gluteal Complex & Pelvic Symmetry",
            "sets_reps": "3 sets x 10 reps/leg",
            "description": f"Address asymmetric weight bearing ({hip_risk:.1f}% hip stress factor).",
            "coaching_cue": "Distribute weight evenly across tripod foot contact without hip hiking."
        })

    # Fatigue Risk Protocols
    if fatigue_risk > 30.0 or summary.get("fatigue_score", 0.0) > 35.0:
        recovery.append(f"High fatigue accumulation detected ({fatigue_risk:.1f}%). Prioritize 8+ hours sleep and active cooldown.")

    if not exercises:
        exercises.append({
            "name": f"Maintenance Mobility Flow ({video_name})",
            "target_area": "Full Body Movement Patterns",
            "sets_reps": "10-minute daily warm-up flow",
            "description": f"Maintain optimal movement mechanics observed in {video_name}.",
            "coaching_cue": "Maintain consistent joint stacking and fluid movement pacing."
        })
        posture_tips.append("Continue current solid movement posture and joint alignment.")
        recovery.append("Follow standard hydration, sleep, and progressive overload principles.")

    return {
        "engine": "AERIS Heuristic Rule Engine",
        "executive_summary": f"Biomechanical assessment for '{video_name}' scored overall risk at {overall_risk:.1f}/100 ({risk_level} level). Primary risk driver: Knee ({knee_risk:.1f}%), Spine ({spine_risk:.1f}%), Hip ({hip_risk:.1f}%).",
        "corrective_exercises": exercises,
        "posture_and_ergonomics": posture_tips if posture_tips else ["Maintain upright posture with shoulders relaxed and core engaged."],
        "recovery_protocol": recovery if recovery else ["Perform 5-10 minutes of active cooldown stretching after training."],
        "actionable_tips": alerts if alerts else [f"Movement form for {video_name} is within healthy range."]
    }


def generate_llm_recommendations(summary: Dict[str, Any], alerts: List[str]) -> Dict[str, Any]:
    """
    Generate Groq LLM-powered ergonomic and biomechanical recommendations.
    Uses video-specific metadata, higher sampling temperature, and dynamic prompt enrichment.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        print("[Groq LLM] No API key found. Using dynamic fallback recommendation engine.")
        return get_default_llm_fallback(summary, alerts)

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        video_name = summary.get('video_name', summary.get('filename', 'Video Analysis'))
        overall_risk = summary.get('overall_risk', 0.0)
        risk_level = summary.get('risk_level', 'UNKNOWN')
        knee_risk = summary.get('knee_risk', summary.get('knee', 0.0))
        hip_risk = summary.get('hip_risk', summary.get('hip', 0.0))
        spine_risk = summary.get('spine_risk', summary.get('spine', 0.0))
        fatigue_risk = summary.get('fatigue_risk', summary.get('fatigue', 0.0))

        prompt = f"""
You are a Doctor of Physical Therapy, Elite Strength & Conditioning Coach, and Biomechanical Specialist.
Analyze the following movement risk analysis data for video "{video_name}" and generate UNIQUE, CUSTOMIZED, and CLINICALLY PRECISE physical therapy recommendations.

CRITICAL INSTRUCTIONS:
- You must generate SPECIFIC, DISTINCT recommendations tailored to this EXACT video ("{video_name}") and its unique risk profile.
- Do NOT return generic boilerplate exercises. Tailor exercise choices directly to the dominant risk driver (Knee: {knee_risk:.1f}%, Spine: {spine_risk:.1f}%, Hip: {hip_risk:.1f}%, Fatigue: {fatigue_risk:.1f}%).

=== SPECIFIC VIDEO METRICS ===
- Video File: {video_name}
- Overall Risk Score: {overall_risk:.1f} / 100 (Risk Level: {risk_level})
- Detailed Joint Risk Breakdown:
  * Knee Stress Index: {knee_risk:.1f} / 100
  * Lumbar Spine Index: {spine_risk:.1f} / 100
  * Hip & Pelvic Asymmetry: {hip_risk:.1f} / 100
  * Fatigue Accumulation: {fatigue_risk:.1f} / 100
- Kinematic Tracking Highlights:
  * Landing Quality: {summary.get('landing_quality', 100.0):.1f} / 100
  * Stability Score: {summary.get('stability_score', 100.0):.1f} / 100
  * Bilateral Symmetry: {summary.get('avg_symmetry', 100.0):.1f}%
  * Peak Knee Valgus Inward Collapse: {summary.get('peak_knee_valgus', 0.0):.1f}°
  * Peak Trunk Forward/Lateral Lean: {summary.get('peak_trunk_lean', 0.0):.1f}°
- Active System Alerts: {json.dumps(alerts)}

=== REQUIRED JSON OUTPUT FORMAT ===
Provide your response strictly in raw JSON (no markdown formatting, no codeblocks) with this structure:
{{
  "engine": "Groq LLM (llama-3.3-70b-versatile)",
  "executive_summary": "<Professional 2-3 sentence clinical summary specifically referencing {video_name} and its primary joint risk driver>",
  "corrective_exercises": [
    {{
      "name": "<Specific Exercise Name>",
      "target_area": "<Target muscle / joint group>",
      "sets_reps": "<Sets & reps / duration>",
      "description": "<Detailed execution instructions>",
      "coaching_cue": "<Key mental or posture cue>"
    }}
  ],
  "posture_and_ergonomics": [
    "<Specific posture or daily movement tip tailored to this video's mechanics>"
  ],
  "recovery_protocol": [
    "<Targeted recovery or fatigue mitigation strategy>"
  ],
  "actionable_tips": [
    "<3-4 high-priority action items specifically addressing the highest risk score>"
  ]
}}
"""

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a world-class biomechanics and physical therapy AI assistant. Return ONLY valid raw JSON without markdown codeblocks or conversational text. Always provide unique, video-tailored protocols."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1600,
        )

        response_content = completion.choices[0].message.content.strip()

        # Clean JSON response if wrapped in markdown block
        if response_content.startswith("```json"):
            response_content = response_content[7:]
        if response_content.startswith("```"):
            response_content = response_content[3:]
        if response_content.endswith("```"):
            response_content = response_content[:-3]
        response_content = response_content.strip()

        parsed_json = json.loads(response_content)
        parsed_json["engine"] = f"Groq LLM ({GROQ_MODEL})"
        return parsed_json

    except Exception as exc:
        print(f"[Groq LLM Error] Exception during LLM generation: {exc}")
        return get_default_llm_fallback(summary, alerts)
