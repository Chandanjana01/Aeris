"""
Estimate knee valgus (inward knee collapse).

Uses 2D frontal projection hip-knee-ankle alignment angle deviation from 180 degrees.
"""

import numpy as np
from src.utils.geometry import calculate_angle


def calculate_knee_valgus(landmarks):
    """
    Calculates average frontal plane knee valgus (inward collapse) in degrees.
    """
    l_hip = landmarks["LEFT_HIP"][:2]
    l_knee = landmarks["LEFT_KNEE"][:2]
    l_ankle = landmarks["LEFT_ANKLE"][:2]

    r_hip = landmarks["RIGHT_HIP"][:2]
    r_knee = landmarks["RIGHT_KNEE"][:2]
    r_ankle = landmarks["RIGHT_ANKLE"][:2]

    left_angle = calculate_angle(l_hip, l_knee, l_ankle)
    right_angle = calculate_angle(r_hip, r_knee, r_ankle)

    # Deviation from straight 180° alignment
    left_valgus = max(0.0, 180.0 - left_angle)
    right_valgus = max(0.0, 180.0 - right_angle)

    avg_valgus = (left_valgus + right_valgus) / 2.0
    return float(avg_valgus)
