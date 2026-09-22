"""Pure timeline functions shared by the renderer and optional sonification."""
from __future__ import annotations

import numpy as np


# One source of truth for visual timing, audio timing, and tests.
SCENE2 = {
    "alternate_start": 0.08,
    "alternate_end": 0.34,
    "project_first_start": 0.34,
    "project_first_end": 0.415,
    "project_second_start": 0.435,
    "project_second_end": 0.510,
    "top_view_start": 0.510,
    "top_view_end": 0.552,
    "basis_start": 0.57,
    "basis_end": 0.65,
    "simultaneous_start": 0.65,
    "simultaneous_end": 0.83,
    "joint_projection_end": 0.875,
    "ica_start": 0.92,
}


def ramp(value: float, start: float, end: float) -> float:
    if end <= start:
        raise ValueError("A ramp must have positive duration.")
    return float(np.clip((value - start) / (end - start), 0.0, 1.0))


def smooth(value: float, start: float = 0.0, end: float = 1.0) -> float:
    fraction = ramp(value, start, end)
    return fraction * fraction * (3.0 - 2.0 * fraction)


def scene2_phase(progress: float) -> str:
    if progress < SCENE2["alternate_start"]:
        return "transition"
    if progress < SCENE2["alternate_end"]:
        return "alternate"
    if progress < SCENE2["basis_start"]:
        return "directions"
    if progress < SCENE2["simultaneous_start"]:
        return "basis"
    if progress < SCENE2["simultaneous_end"]:
        return "simultaneous"
    if progress < SCENE2["ica_start"]:
        return "pca"
    return "ica"
