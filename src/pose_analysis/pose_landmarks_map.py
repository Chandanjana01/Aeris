"""
MediaPipe 33 Pose Landmarks Mapping Dictionary & Helpers.

MediaPipe Pose tracks 33 body pose landmark positions.
Each landmark has a unique integer ID (0 to 32) corresponding to a named anatomical location.
"""

# Complete dictionary mapping integer ID (0 to 32) to official MediaPipe landmark name
POSE_LANDMARKS_33 = {
    0:  "NOSE",
    1:  "LEFT_EYE_INNER",
    2:  "LEFT_EYE",
    3:  "LEFT_EYE_OUTER",
    4:  "RIGHT_EYE_INNER",
    5:  "RIGHT_EYE",
    6:  "RIGHT_EYE_OUTER",
    7:  "LEFT_EAR",
    8:  "RIGHT_EAR",
    9:  "MOUTH_LEFT",
    10: "MOUTH_RIGHT",
    11: "LEFT_SHOULDER",
    12: "RIGHT_SHOULDER",
    13: "LEFT_ELBOW",
    14: "RIGHT_ELBOW",
    15: "LEFT_WRIST",
    16: "RIGHT_WRIST",
    17: "LEFT_PINKY",
    18: "RIGHT_PINKY",
    19: "LEFT_INDEX",
    20: "RIGHT_INDEX",
    21: "LEFT_THUMB",
    22: "RIGHT_THUMB",
    23: "LEFT_HIP",
    24: "RIGHT_HIP",
    25: "LEFT_KNEE",
    26: "RIGHT_KNEE",
    27: "LEFT_ANKLE",
    28: "RIGHT_ANKLE",
    29: "LEFT_HEEL",
    30: "RIGHT_HEEL",
    31: "LEFT_FOOT_INDEX",
    32: "RIGHT_FOOT_INDEX"
}

# Categorized landmark groups for anatomical analysis
BODY_GROUPS = {
    "FACE": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "UPPER_BODY": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
    "LOWER_BODY": [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
}


def get_landmark_name(landmark_id: int) -> str:
    """Returns the landmark name given its integer ID (0-32)."""
    return POSE_LANDMARKS_33.get(landmark_id, f"UNKNOWN_LANDMARK_{landmark_id}")


def get_landmark_id(landmark_name: str) -> int:
    """Returns the landmark integer ID given its string name."""
    name_upper = landmark_name.upper()
    for id_val, name in POSE_LANDMARKS_33.items():
        if name == name_upper:
            return id_val
    raise KeyError(f"Landmark '{landmark_name}' not found in 33 MediaPipe Pose Landmarks.")


def print_landmark_catalog():
    """Prints a clean tabular list of all 33 pose landmarks."""
    print("=" * 60)
    print("      MediaPipe 33 Pose Landmarks Catalog")
    print("=" * 60)
    print(f"{'ID':<6} {'Landmark Name':<25} {'Category':<15}")
    print("-" * 60)
    
    for landmark_id, name in POSE_LANDMARKS_33.items():
        category = "FACE" if landmark_id in BODY_GROUPS["FACE"] else (
            "UPPER_BODY" if landmark_id in BODY_GROUPS["UPPER_BODY"] else "LOWER_BODY"
        )
        print(f"{landmark_id:<6} {name:<25} {category:<15}")
    
    print("=" * 60)


if __name__ == "__main__":
    print_landmark_catalog()
