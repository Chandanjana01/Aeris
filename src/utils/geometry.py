import numpy as np


def calculate_angle(a, b, c):
    """
    Calculate angle ABC in degrees.
    """

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine = np.dot(ba, bc)

    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)

    if denominator == 0:
        return 0.0

    cosine = cosine / denominator

    cosine = np.clip(cosine, -1.0, 1.0)

    angle = np.degrees(np.arccos(cosine))

    return float(angle)


def midpoint(p1, p2):
    p1 = np.array(p1)
    p2 = np.array(p2)

    return ((p1 + p2) / 2).tolist()


def distance(p1, p2):

    p1 = np.array(p1)
    p2 = np.array(p2)

    return float(np.linalg.norm(p1 - p2))


def vector(p1, p2):

    return np.array(p2) - np.array(p1)


def angle_between_vectors(v1, v2):

    v1 = np.array(v1)
    v2 = np.array(v2)

    denominator = np.linalg.norm(v1) * np.linalg.norm(v2)

    if denominator == 0:
        return 0

    cosine = np.dot(v1, v2) / denominator

    cosine = np.clip(cosine, -1, 1)

    return float(np.degrees(np.arccos(cosine)))


def velocity(previous, current, fps=30):

    previous = np.array(previous)
    current = np.array(current)

    return ((current - previous) * fps).tolist()


def acceleration(prev_velocity, current_velocity, fps=30):

    prev_velocity = np.array(prev_velocity)
    current_velocity = np.array(current_velocity)

    return ((current_velocity - prev_velocity) * fps).tolist()


def center_of_mass(left_shoulder,
                   right_shoulder,
                   left_hip,
                   right_hip):

    upper = midpoint(left_shoulder, right_shoulder)

    lower = midpoint(left_hip, right_hip)

    return midpoint(upper, lower)