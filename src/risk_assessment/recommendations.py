def generate_recommendations(summary):

    alerts = []

    recommendations = []

    if summary["peak_knee_valgus"] > 12:
        alerts.append("High knee valgus detected.")
        recommendations.append(
            "Strengthen hip abductors and improve knee alignment."
        )

    if summary["landing_quality"] < 75:
        alerts.append("Poor landing mechanics.")
        recommendations.append(
            "Practice soft two-leg landing drills."
        )

    if summary["peak_trunk_lean"] > 20:
        alerts.append("Excessive trunk lean.")
        recommendations.append(
            "Improve core stability."
        )

    if summary["fatigue_score"] > 40:
        alerts.append("Possible fatigue detected.")
        recommendations.append(
            "Increase recovery and monitor workload."
        )

    return alerts, recommendations
