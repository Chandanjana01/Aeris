import json

from src.risk_assessment.risk_score import (
    knee_risk,
    hip_risk,
    spine_risk,
    fatigue_risk,
    overall_risk
)

from src.risk_assessment.recommendations import generate_recommendations


def get_risk_level(score):

    if score < 25:
        return "LOW"

    elif score < 50:
        return "MODERATE"

    elif score < 75:
        return "HIGH"

    else:
        return "VERY HIGH"


def generate_report(summary):
    """
    Generate risk report from movement summary (pandas Series or dict)
    """

    knee = knee_risk(summary)
    hip = hip_risk(summary)
    spine = spine_risk(summary)
    fatigue = fatigue_risk(summary)

    overall = overall_risk(summary)

    alerts, recommendations = generate_recommendations(summary)

    report = {

        "video_name": summary["video_name"],

        "overall_risk": round(overall, 2),

        "risk_level": get_risk_level(overall),

        "body_part_risks": {

            "knee": knee,

            "hip": hip,

            "spine": spine,

            "fatigue": fatigue

        },

        "movement_scores": {

            "landing_quality": summary["landing_quality"],

            "stability_score": summary["stability_score"],

            "symmetry_score": summary["avg_symmetry"],

            "fatigue_score": summary["fatigue_score"]

        },

        "alerts": alerts,

        "recommendations": recommendations

    }

    return report


def save_report(report, output_json):
    """
    Save report to JSON file
    """
    with open(output_json, "w") as f:
        json.dump(report, f, indent=4)

    print(f"\nRisk report saved to: {output_json}")
