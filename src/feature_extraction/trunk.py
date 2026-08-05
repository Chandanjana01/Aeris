"""
Calculate trunk lean.

Angle between torso and vertical axis.
"""

import numpy as np


def calculate_trunk_lean(landmarks):

    left_shoulder = np.array(landmarks["LEFT_SHOULDER"][:2])
    right_shoulder = np.array(landmarks["RIGHT_SHOULDER"][:2])

    left_hip = np.array(landmarks["LEFT_HIP"][:2])
    right_hip = np.array(landmarks["RIGHT_HIP"][:2])

    shoulder_mid = (left_shoulder + right_shoulder) / 2

    hip_mid = (left_hip + right_hip) / 2

    torso = shoulder_mid - hip_mid

    vertical = np.array([0, -1])

    denominator = np.linalg.norm(torso) * np.linalg.norm(vertical)

    if denominator == 0:
        return 0

    cosine = np.dot(torso, vertical) / denominator

    cosine = np.clip(cosine, -1, 1)

    angle = np.degrees(np.arccos(cosine))

    return float(angle)
