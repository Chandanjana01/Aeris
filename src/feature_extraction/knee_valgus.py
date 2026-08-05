"""
Estimate knee valgus.

Uses hip-knee-ankle alignment.
"""

from src.utils.geometry import calculate_angle


def calculate_knee_valgus(landmarks):

    left = calculate_angle(

        landmarks["LEFT_HIP"],

        landmarks["LEFT_KNEE"],

        landmarks["LEFT_ANKLE"]

    )

    right = calculate_angle(

        landmarks["RIGHT_HIP"],

        landmarks["RIGHT_KNEE"],

        landmarks["RIGHT_ANKLE"]

    )

    valgus = 180 - ((left + right) / 2)

    return float(max(0, valgus))
