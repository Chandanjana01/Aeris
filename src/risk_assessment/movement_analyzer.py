import os

import pandas as pd

from src.risk_assessment.movement_metrics import (
    calculate_rom,
    peak,
    average,
    stability_score,
    fatigue_score,
    landing_quality
)


def analyze_movement(frame_csv, output_csv):

    df = pd.read_csv(frame_csv)

    summary = {

        "video_name":

        os.path.basename(os.path.dirname(frame_csv)),

        "left_knee_rom":

        calculate_rom(df["left_knee_angle"]),

        "right_knee_rom":

        calculate_rom(df["right_knee_angle"]),

        "left_hip_rom":

        calculate_rom(df["left_hip_angle"]),

        "right_hip_rom":

        calculate_rom(df["right_hip_angle"]),

        "peak_knee_valgus":

        peak(df["knee_valgus"]),

        "avg_knee_valgus":

        average(df["knee_valgus"]),

        "peak_trunk_lean":

        peak(df["trunk_lean"]),

        "avg_trunk_lean":

        average(df["trunk_lean"]),

        "avg_symmetry":

        average(df["symmetry_score"]),

        "stability_score":

        stability_score(

            df["com_x"],

            df["com_y"]

        ),

        "landing_quality":

        landing_quality(df),

        "fatigue_score":

        fatigue_score(df)

    }

    summary_df = pd.DataFrame([summary])

    summary_df.to_csv(output_csv, index=False)

    print()

    print(summary_df)

    print()

    print("Movement summary saved.")

    return summary
