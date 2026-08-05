"""
Movement metric calculations.
"""

import numpy as np


def calculate_rom(series):
    """
    Range of Motion
    """
    return float(series.max() - series.min())


def peak(series):
    return float(series.max())


def average(series):
    return float(series.mean())


def minimum(series):
    return float(series.min())


def stability_score(com_x, com_y):
    """
    Estimate stability from COM movement.
    Less COM movement = higher stability.
    """

    x_std = np.std(com_x)

    y_std = np.std(com_y)

    movement = np.sqrt(x_std**2 + y_std**2)

    score = 100 - movement * 500

    score = max(0, min(100, score))

    return float(score)


def fatigue_score(df):
    """
    Compare first 20% vs last 20%.
    """

    n = len(df)

    section = max(1, int(n * 0.2))

    first = df.iloc[:section]

    last = df.iloc[-section:]

    first_sym = first["symmetry_score"].mean()
    last_sym = last["symmetry_score"].mean()

    drop = first_sym - last_sym

    fatigue = drop * 4

    fatigue = max(0, min(100, fatigue))

    return float(fatigue)


def landing_quality(df):
    """
    Simple landing quality score.
    """

    valgus = df["knee_valgus"].max()

    trunk = df["trunk_lean"].max()

    score = 100

    score -= valgus * 2

    score -= trunk * 1.2

    score = max(0, min(100, score))

    return float(score)
