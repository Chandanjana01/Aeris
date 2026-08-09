"""
Dynamic Posture Alerts & Corrective Recommendation Engine.

Generates custom alerts and advice targeted to specific biomechanical deviations.
"""


def generate_recommendations(summary: dict):
    alerts = []
    recommendations = []

    peak_valgus = summary.get("peak_knee_valgus", 0.0)
    landing = summary.get("landing_quality", 100.0)
    peak_trunk = summary.get("peak_trunk_lean", 0.0)
    symmetry = summary.get("avg_symmetry", 100.0)
    fatigue = summary.get("fatigue_score", 0.0)
    stability = summary.get("stability_score", 100.0)

    # 1. Knee Valgus Alert
    if peak_valgus > 12.0:
        alerts.append(f"Knee valgus collapse detected (Peak: {peak_valgus:.1f}°).")
        recommendations.append("Strengthen hip abductors (gluteus medius) and focus on keeping knees aligned over toes.")

    # 2. Landing Mechanics Alert
    if landing < 75.0:
        alerts.append(f"Hard landing / landing deceleration strain (Quality: {landing:.1f}/100).")
        recommendations.append("Practice soft two-leg landing drills with toe-to-heel roll and deep knee flexion absorption.")

    # 3. Torso / Spine Lean Alert
    if peak_trunk > 18.0:
        alerts.append(f"Excessive forward/lateral torso lean (Peak: {peak_trunk:.1f}°).")
        recommendations.append("Perform core stabilization exercises (planks, anti-rotation presses) to maintain upright spinal posture.")

    # 4. Bilateral Asymmetry Alert
    if symmetry < 88.0:
        alerts.append(f"Bilateral movement asymmetry detected (Symmetry: {symmetry:.1f}%).")
        recommendations.append("Incorporate single-leg unilateral exercises (split squats, single-leg deadlifts) to balance strength.")

    # 5. Stability & Balance Alert
    if stability < 70.0:
        alerts.append(f"Center-of-mass sway / balance instability detected (Stability: {stability:.1f}/100).")
        recommendations.append("Add proprioceptive balance training (single-leg stance on foam/bosu ball).")

    # 6. Fatigue Flag
    if fatigue > 30.0:
        alerts.append(f"Movement form degradation / fatigue detected ({fatigue:.1f}% drop).")
        recommendations.append("Increase rest intervals between sets and monitor cumulative training workload.")

    # Fallback optimal mechanics message if no alerts triggered
    if not alerts:
        recommendations.append("Postural mechanics and joint alignment are optimal. Maintain current conditioning.")

    return alerts, recommendations


from src.risk_assessment.llm_recommendations import generate_llm_recommendations

