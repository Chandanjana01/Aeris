"""
Test script for Groq LLM Recommendation Engine.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.risk_assessment.llm_recommendations import generate_llm_recommendations
from src.risk_assessment.report_generator import generate_report


def main():
    print("==================================================")
    print("[TEST] Testing Groq LLM Recommendation Engine")
    print("==================================================")

    sample_summary = {
        "video_name": "test_squat_jump.mp4",
        "peak_knee_valgus": 16.4,
        "landing_quality": 62.5,
        "peak_trunk_lean": 22.1,
        "avg_symmetry": 81.2,
        "fatigue_score": 34.0,
        "stability_score": 65.0,
    }

    alerts = [
        "Knee valgus collapse detected (Peak: 16.4 degrees).",
        "Hard landing / landing deceleration strain (Quality: 62.5/100).",
        "Excessive forward/lateral torso lean (Peak: 22.1 degrees).",
        "Bilateral movement asymmetry detected (Symmetry: 81.2%).",
    ]

    print("\n1. Generating direct Groq LLM recommendations...")
    llm_result = generate_llm_recommendations(sample_summary, alerts)
    
    print("\n[Engine Used]:", llm_result.get("engine"))
    print("\n[Executive Summary]:")
    print(llm_result.get("executive_summary"))
    
    print("\n[Corrective Exercises]:")
    for ex in llm_result.get("corrective_exercises", []):
        print(f" - {ex.get('name')} [{ex.get('sets_reps')}]: {ex.get('description')} (Cue: {ex.get('coaching_cue')})")

    print("\n[Posture & Ergonomics]:")
    for p in llm_result.get("posture_and_ergonomics", []):
        print(f" - {p}")

    print("\n[Recovery Protocol]:")
    for r in llm_result.get("recovery_protocol", []):
        print(f" - {r}")

    print("\n2. Testing report_generator integration...")
    report = generate_report(sample_summary)
    assert "llm_recommendations" in report
    print("SUCCESS: Full Report generation successful!")
    print(f"   Overall Risk: {report['overall_risk']} ({report['risk_level']})")
    print(f"   Report contains llm_recommendations key with engine: '{report['llm_recommendations'].get('engine')}'")

    print("\n==================================================")
    print("SUCCESS: ALL GROQ LLM RECOMMENDATION TESTS PASSED!")
    print("==================================================")



if __name__ == "__main__":
    main()
