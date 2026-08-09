import json

from src.risk_assessment.risk_score import (
    knee_risk,
    hip_risk,
    spine_risk,
    fatigue_risk,
    overall_risk
)

from src.risk_assessment.recommendations import generate_recommendations, generate_llm_recommendations


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
    risk_lvl = get_risk_level(overall)

    alerts, recommendations = generate_recommendations(summary)

    # Enrich summary with computed scores for LLM context
    enriched_summary = dict(summary) if isinstance(summary, dict) else summary.to_dict()
    enriched_summary.update({
        "knee_risk": knee,
        "hip_risk": hip,
        "spine_risk": spine,
        "fatigue_risk": fatigue,
        "overall_risk": round(overall, 2),
        "risk_level": risk_lvl
    })

    llm_recs = generate_llm_recommendations(enriched_summary, alerts)

    report = {

        "video_name": summary["video_name"],

        "overall_risk": round(overall, 2),

        "risk_level": risk_lvl,

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

        "recommendations": recommendations,

        "llm_recommendations": llm_recs

    }

    return report



def save_report(report, output_json):
    """
    Save report to JSON file
    """
    with open(output_json, "w") as f:
        json.dump(report, f, indent=4)

    print(f"\nRisk report saved to: {output_json}")
