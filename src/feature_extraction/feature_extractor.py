"""
Extract complete frame-wise biomechanical features including risk metrics.
"""

import os
import pandas as pd

from src.utils.landmark_loader import LandmarkLoader
from src.feature_extraction.joint_angles import calculate_joint_angles
from src.feature_extraction.trunk import calculate_trunk_lean
from src.feature_extraction.knee_valgus import calculate_knee_valgus
from src.feature_extraction.symmetry import calculate_symmetry
from src.utils.geometry import center_of_mass


def extract_complete_features(csv_path, output_csv):

    loader = LandmarkLoader(csv_path)

    rows = []

    print(f"Processing {len(loader.get_frame_names())} frames...")

    for frame_name, landmarks in loader:

        angles = calculate_joint_angles(landmarks)
        
        trunk_lean = calculate_trunk_lean(landmarks)
        
        valgus = calculate_knee_valgus(landmarks)
        
        symmetry = calculate_symmetry(angles)
        
        # Calculate center of mass
        com = center_of_mass(
            landmarks["LEFT_SHOULDER"],
            landmarks["RIGHT_SHOULDER"],
            landmarks["LEFT_HIP"],
            landmarks["RIGHT_HIP"]
        )

        row = {
            "frame_name": frame_name,
            **angles,
            "trunk_lean": trunk_lean,
            "knee_valgus": valgus,
            "symmetry_score": symmetry,
            "com_x": com[0],
            "com_y": com[1],
            "com_z": com[2]
        }

        rows.append(row)

    df = pd.DataFrame(rows)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    df.to_csv(output_csv, index=False)

    print(f"\nSaved complete feature CSV:")
    print(output_csv)

    print(f"\nTotal Frames Processed: {len(df)}")
    print(f"Features per frame: {len(df.columns)}")
