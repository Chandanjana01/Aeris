"""
Left-right symmetry score.
"""

import numpy as np


def calculate_symmetry(angles):

    pairs = [

        (
            angles["left_knee_angle"],
            angles["right_knee_angle"]
        ),

        (
            angles["left_hip_angle"],
            angles["right_hip_angle"]
        ),

        (
            angles["left_elbow_angle"],
            angles["right_elbow_angle"]
        ),

        (
            angles["left_shoulder_angle"],
            angles["right_shoulder_angle"]
        )

    ]

    scores = []

    for left, right in pairs:

        difference = abs(left - right)

        score = max(0, 100 - difference)

        scores.append(score)

    return float(np.mean(scores))
