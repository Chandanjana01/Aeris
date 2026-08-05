"""
Loads MediaPipe landmark CSV and groups 33 landmarks into one frame dictionary.
"""

import pandas as pd


class LandmarkLoader:

    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

        # Group rows by frame name
        self.frames = self.df.groupby("frame_name")

    def get_frame_names(self):
        """Return list of all frame names"""
        return list(self.frames.groups.keys())

    def get_frame(self, frame_name):
        """
        Returns a dictionary

        {
            "NOSE":[x,y,z],
            "LEFT_HIP":[x,y,z],
            ...
        }
        """

        frame = self.frames.get_group(frame_name)

        landmarks = {}

        for _, row in frame.iterrows():

            landmarks[row["landmark_name"]] = [
                float(row["x"]),
                float(row["y"]),
                float(row["z"])
            ]

        return landmarks

    def __iter__(self):
        """
        Allows:

        for frame_name, landmarks in loader:
            ...
        """

        for frame_name in self.get_frame_names():
            yield frame_name, self.get_frame(frame_name)
