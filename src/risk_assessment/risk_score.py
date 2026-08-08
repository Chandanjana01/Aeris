"""
Continuous Dynamic Ergonomic Risk Engine.

Calculates region risk scores (Knee, Hip, Spine, Fatigue) and composite overall
risk score using continuous scaling instead of discrete binary step functions.
"""


def knee_risk(summary: dict) -> float:
    """
    Continuous knee risk evaluation based on valgus collapse, ROM restriction,
    and landing mechanics.
    """
    peak_valgus = summary.get("peak_knee_valgus", 0.0)
    left_rom = summary.get("left_knee_rom", 60.0)
    right_rom = summary.get("right_knee_rom", 60.0)
    landing = summary.get("landing_quality", 100.0)

    avg_rom = (left_rom + right_rom) / 2.0

    # 1. Valgus contribution (0 - 45 pts)
    valgus_pts = min(45.0, max(0.0, peak_valgus * 2.5))

    # 2. ROM restriction penalty (0 - 25 pts)
    rom_penalty = min(25.0, max(0.0, (45.0 - avg_rom) * 0.6))

    # 3. Landing mechanics penalty (0 - 30 pts)
    landing_penalty = min(30.0, max(0.0, (100.0 - landing) * 0.3))

    score = valgus_pts + rom_penalty + landing_penalty
    return round(min(100.0, max(0.0, score)), 2)


def spine_risk(summary: dict) -> float:
    """
    Continuous spine risk evaluation based on peak trunk lean and posture stability.
    """
    peak_trunk = summary.get("peak_trunk_lean", 0.0)
    stability = summary.get("stability_score", 100.0)

    # 1. Trunk lean contribution (0 - 60 pts)
    trunk_pts = min(60.0, max(0.0, peak_trunk * 2.0))

    # 2. Instability penalty (0 - 40 pts)
    instability_penalty = min(40.0, max(0.0, (100.0 - stability) * 0.4))

    score = trunk_pts + instability_penalty
    return round(min(100.0, max(0.0, score)), 2)


def fatigue_risk(summary: dict) -> float:
    """
    Fatigue degradation risk score.
    """
    fatigue = summary.get("fatigue_score", 0.0)
    return round(min(100.0, max(0.0, fatigue)), 2)


def hip_risk(summary: dict) -> float:
    """
    Continuous hip risk evaluation based on bilateral symmetry and hip ROM.
    """
    avg_symmetry = summary.get("avg_symmetry", 100.0)
    left_hip_rom = summary.get("left_hip_rom", 40.0)
    right_hip_rom = summary.get("right_hip_rom", 40.0)

    avg_hip_rom = (left_hip_rom + right_hip_rom) / 2.0

    # 1. Asymmetry penalty (0 - 50 pts)
    asymmetry_penalty = min(50.0, max(0.0, (100.0 - avg_symmetry) * 1.5))

    # 2. Restricted Hip ROM penalty (0 - 50 pts)
    rom_penalty = min(50.0, max(0.0, (35.0 - avg_hip_rom) * 1.0))

    score = asymmetry_penalty + rom_penalty
    return round(min(100.0, max(0.0, score)), 2)


def overall_risk(summary: dict) -> float:
    """
    Calculates weighted composite overall risk score (0 - 100).
    Formula: Knee (40%) + Spine (25%) + Hip (20%) + Fatigue (15%)
    """
    knee = knee_risk(summary)
    hip = hip_risk(summary)
    spine = spine_risk(summary)
    fatigue = fatigue_risk(summary)

    overall = (knee * 0.40) + (spine * 0.25) + (hip * 0.20) + (fatigue * 0.15)
    return round(min(100.0, max(0.0, overall)), 2)
