"""
Calculate biomechanical joint angles from one frame.
"""

from src.utils.geometry import calculate_angle


def calculate_joint_angles(landmarks):
    """
    Input:
        landmarks = {
            "LEFT_HIP":[x,y,z],
            ...
        }

    Returns:
        dict of joint angles
    """

    angles = {}

    try:
        # LEFT ELBOW
        angles["left_elbow_angle"] = calculate_angle(
            landmarks["LEFT_SHOULDER"],
            landmarks["LEFT_ELBOW"],
            landmarks["LEFT_WRIST"]
        )

        # RIGHT ELBOW
        angles["right_elbow_angle"] = calculate_angle(
            landmarks["RIGHT_SHOULDER"],
            landmarks["RIGHT_ELBOW"],
            landmarks["RIGHT_WRIST"]
        )

        # LEFT KNEE
        angles["left_knee_angle"] = calculate_angle(
            landmarks["LEFT_HIP"],
            landmarks["LEFT_KNEE"],
            landmarks["LEFT_ANKLE"]
        )

        # RIGHT KNEE
        angles["right_knee_angle"] = calculate_angle(
            landmarks["RIGHT_HIP"],
            landmarks["RIGHT_KNEE"],
            landmarks["RIGHT_ANKLE"]
        )

        # LEFT HIP
        angles["left_hip_angle"] = calculate_angle(
            landmarks["LEFT_SHOULDER"],
            landmarks["LEFT_HIP"],
            landmarks["LEFT_KNEE"]
        )

        # RIGHT HIP
        angles["right_hip_angle"] = calculate_angle(
            landmarks["RIGHT_SHOULDER"],
            landmarks["RIGHT_HIP"],
            landmarks["RIGHT_KNEE"]
        )

        # LEFT SHOULDER
        angles["left_shoulder_angle"] = calculate_angle(
            landmarks["LEFT_ELBOW"],
            landmarks["LEFT_SHOULDER"],
            landmarks["LEFT_HIP"]
        )

        # RIGHT SHOULDER
        angles["right_shoulder_angle"] = calculate_angle(
            landmarks["RIGHT_ELBOW"],
            landmarks["RIGHT_SHOULDER"],
            landmarks["RIGHT_HIP"]
        )

    except KeyError as e:
        raise ValueError(f"Missing landmark: {e}")

    return angles
