"""Exact geometry shared by the explanatory animation and regression tests."""
from __future__ import annotations

import numpy as np


def flatten_points(points: np.ndarray, amount: float) -> np.ndarray:
    """Project toward z=0 without ever changing either microphone coordinate."""
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("Expected an array with shape (samples, 3).")
    result = points.copy()
    result[:, 2] *= 1.0 - float(np.clip(amount, 0.0, 1.0))
    return result


def projection_guides(points: np.ndarray) -> np.ndarray:
    """Return vertical segments joining observations to their exact floor points."""
    return np.stack((points, flatten_points(points, 1.0)), axis=1)


def mixing_coordinates(matrix: np.ndarray, amount: float) -> np.ndarray:
    """Interpolate an actual inverse coordinate map, not an orthogonal projection."""
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (2, 2) or np.linalg.matrix_rank(matrix) < 2:
        raise ValueError("The first two microphones must define an invertible 2x2 mixing matrix.")
    amount = float(np.clip(amount, 0.0, 1.0))
    return (1.0 - amount) * np.eye(2) + amount * np.linalg.inv(matrix)
