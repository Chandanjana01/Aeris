def knee_risk(summary):

    score = 0

    if summary["peak_knee_valgus"] > 15:
        score += 40

    elif summary["peak_knee_valgus"] > 10:
        score += 25

    if summary["left_knee_rom"] < 45:
        score += 20

    if summary["right_knee_rom"] < 45:
        score += 20

    if summary["landing_quality"] < 75:
        score += 20

    return min(score,100)

def spine_risk(summary):

    score = 0

    if summary["peak_trunk_lean"] > 25:
        score += 40

    elif summary["peak_trunk_lean"] > 15:
        score += 20

    if summary["stability_score"] < 75:
        score += 30

    return min(score,100)

def fatigue_risk(summary):

    return min(summary["fatigue_score"],100)

def hip_risk(summary):

    score = 0

    if summary["avg_symmetry"] < 90:
        score += 30

    if summary["left_hip_rom"] < 35:
        score += 20

    if summary["right_hip_rom"] < 35:
        score += 20

    return min(score,100)

def overall_risk(summary):

    knee = knee_risk(summary)

    hip = hip_risk(summary)

    spine = spine_risk(summary)

    fatigue = fatigue_risk(summary)

    overall = (
        knee*0.40 +
        hip*0.20 +
        spine*0.25 +
        fatigue*0.15
    )

    return round(overall,2)
