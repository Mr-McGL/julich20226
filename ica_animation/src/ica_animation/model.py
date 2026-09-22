"""Instantaneous mixtures, independent component estimation, and diagnostics.

Arrays store samples by rows. The physical convention x(t) = A @ s(t)
therefore becomes observations = sources @ mixing.T in NumPy.
"""
from __future__ import annotations

from dataclasses import dataclass
import warnings
import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linear_sum_assignment
from sklearn.decomposition import FastICA, PCA
from sklearn.exceptions import ConvergenceWarning

FloatArray = NDArray[np.float64]


def mixing_from_positions(speakers: list[dict], microphones: list[dict], reference_distance: float = 1.0,
                          minimum_distance: float = 0.1) -> tuple[FloatArray, FloatArray]:
    source_positions = np.asarray([item["position"] for item in speakers], dtype=float)
    microphone_positions = np.asarray([item["position"] for item in microphones], dtype=float)
    distances = np.linalg.norm(microphone_positions[:, None] - source_positions[None], axis=2)
    if not np.isfinite(distances).all() or np.any(distances < minimum_distance):
        raise ValueError("All source-to-microphone distances must exceed minimum_distance.")
    return reference_distance / distances, distances


def normalize_columns(values: FloatArray) -> FloatArray:
    lengths = np.linalg.norm(values, axis=0, keepdims=True)
    if np.any(lengths < 1e-14):
        raise ValueError("Cannot normalize a zero direction.")
    return values / lengths


def cross_correlation(left: FloatArray, right: FloatArray) -> FloatArray:
    left = left - left.mean(axis=0)
    right = right - right.mean(axis=0)
    denominator = np.linalg.norm(left, axis=0)[:, None] * np.linalg.norm(right, axis=0)[None, :]
    return np.clip((left.T @ right) / np.maximum(denominator, np.finfo(float).eps), -1.0, 1.0)


def direction_angle(left: FloatArray, right: FloatArray) -> float:
    cosine = abs(float(left @ right)) / np.linalg.norm(left) / np.linalg.norm(right)
    return float(np.degrees(np.arccos(np.clip(cosine, 0.0, 1.0))))


@dataclass
class ICAResult:
    sources: FloatArray
    mixing: FloatArray
    unmixing: FloatArray
    mean: FloatArray
    iterations: int


def fit_ica(observations: FloatArray, components: int, seed: int) -> ICAResult:
    centered = observations - observations.mean(axis=0)
    rank = np.linalg.matrix_rank(centered)
    if components > rank:
        raise ValueError(f"Cannot estimate {components} components from rank-{rank} observations.")
    estimator = FastICA(n_components=components, whiten="unit-variance", whiten_solver="svd",
                        algorithm="parallel", fun="logcosh", random_state=seed,
                        max_iter=4000, tol=1e-7)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        try:
            estimated = estimator.fit_transform(observations)
        except ConvergenceWarning as error:
            raise ValueError("FastICA did not converge. Adjust the configuration or seed.") from error
    return ICAResult(estimated, estimator.mixing_, estimator.components_, estimator.mean_, estimator.n_iter_)


def align_for_display(result: ICAResult, reference: FloatArray) -> tuple[ICAResult, FloatArray]:
    """Resolve permutation, sign, and scale ONLY for simulator-side evaluation.

The reference sources never enter FastICA. This helper is not a blind
calibration procedure, and its scaling is not a recovered physical gain.
"""
    correlations = cross_correlation(reference, result.sources)
    rows, columns = linear_sum_assignment(-np.abs(correlations))
    order = columns[np.argsort(rows)]
    estimated = result.sources[:, order].copy()
    centered_reference = reference - reference.mean(axis=0)
    selected_reference = centered_reference[:, np.sort(rows)]
    scales = np.sum(estimated * selected_reference, axis=0) / np.sum(estimated ** 2, axis=0)
    if np.any(np.abs(scales) < 1e-12):
        raise ValueError("Display alignment failed because a recovered signal has zero correlation.")
    aligned = ICAResult(estimated * scales, result.mixing[:, order] / scales,
                        result.unmixing[order] * scales[:, None], result.mean, result.iterations)
    return aligned, cross_correlation(reference, aligned.sources)


@dataclass
class SceneData:
    time: FloatArray
    sources: FloatArray
    observations: FloatArray
    mixing: FloatArray
    distances: FloatArray
    pca_directions: FloatArray
    variance_ratios: FloatArray
    singular_values: FloatArray
    ica: ICAResult | None = None
    alternate_sources: FloatArray | None = None
    alternate_observations: FloatArray | None = None
    alternate_active: NDArray[np.int64] | None = None
    full_ica: ICAResult | None = None


def make_scene_data(config: dict, scene_id: str) -> SceneData:
    scene = config["scenes"][scene_id]
    settings = config["signals"]
    count = len(scene["speakers"])
    time = np.linspace(0.0, settings["duration"], settings["samples"], endpoint=False)
    amplitudes = np.asarray(scene.get("amplitudes", settings["amplitudes"])[:count])
    frequencies = np.asarray(settings["frequencies"][:count])
    phases = np.asarray(settings["phases"][:count])
    sources = amplitudes * np.sin(2 * np.pi * time[:, None] * frequencies + phases)
    if scene_id == "4":
        sources[:, 1] = sources[:, 0]
    mixing, distances = mixing_from_positions(scene["speakers"], scene["microphones"], **config["physics"])
    observations = sources @ mixing.T
    pca = PCA(svd_solver="full").fit(observations)
    singular_values = np.linalg.svd(observations - observations.mean(axis=0), compute_uv=False)
    result = SceneData(time, sources, observations, mixing, distances, pca.components_.T,
                       pca.explained_variance_ratio_, singular_values)
    if scene_id == "2":
        if np.linalg.matrix_rank(mixing[:2, :]) < 2:
            raise ValueError("Scene 2 requires independent first-two-microphone mixtures for the displayed 2D change of basis.")
        correlation = abs(float(cross_correlation(sources, sources)[0, 1]))
        if correlation > scene["correlation_limit"]:
            raise ValueError(f"Source correlation {correlation:.4f} exceeds correlation_limit. Adjust frequencies/duration.")
        result.ica, _ = align_for_display(fit_ica(observations, 2, config["seed"]), sources)
        burst_index = np.minimum((time / settings["duration"] * scene["alternate_bursts"]).astype(int),
                                 scene["alternate_bursts"] - 1)
        active = burst_index % 2
        gate = (np.arange(2)[None, :] == active[:, None]).astype(float)
        # A short cosine taper removes discontinuities at burst boundaries.
        phase = time / settings["duration"] * scene["alternate_bursts"] % 1.0
        envelope = np.minimum(np.minimum(phase / 0.06, (1.0 - phase) / 0.06), 1.0)
        envelope = np.sin(np.clip(envelope, 0.0, 1.0) * np.pi / 2) ** 2
        result.alternate_active = active
        result.alternate_sources = sources * gate * envelope[:, None]
        result.alternate_observations = result.alternate_sources @ mixing.T
    elif scene_id == "3":
        result.ica = fit_ica(observations, scene["components"], config["seed"])
        # Order the displayed components by similarity to the dominant source.
        correlations = cross_correlation(sources, result.ica.sources)
        primary = int(np.argmax(np.abs(correlations[0])))
        order = np.asarray([primary, 1 - primary])
        signs = np.sign(np.asarray([correlations[0, primary], correlations[1:, 1 - primary].sum()]))
        signs[signs == 0] = 1
        raw = result.ica
        result.ica = ICAResult(raw.sources[:, order] * signs, raw.mixing[:, order] * signs,
                               raw.unmixing[order] * signs[:, None], raw.mean, raw.iterations)
        result.full_ica, _ = align_for_display(fit_ica(observations, 3, config["seed"]), sources)
    return result


def diagnostics(config: dict) -> dict:
    report: dict = {"seed": config["seed"], "model": "instantaneous, noiseless, amplitude proportional to 1/d", "scenes": {}}
    for scene_id in ("1", "2", "3", "4"):
        data = make_scene_data(config, scene_id)
        entry = {"mixing_matrix": data.mixing.tolist(), "distances": data.distances.tolist(),
                 "mixing_rank": int(np.linalg.matrix_rank(data.mixing)),
                 "mixing_condition_number": float(np.linalg.cond(data.mixing)),
                 "observation_rank": int(np.linalg.matrix_rank(data.observations - data.observations.mean(axis=0))),
                 "source_variances": data.sources.var(axis=0).tolist(),
                 "source_correlations": cross_correlation(data.sources, data.sources).tolist(),
                 "pca_explained_variance_ratios": data.variance_ratios.tolist(),
                 "singular_values": data.singular_values.tolist()}
        if data.ica is not None:
            entry.update({"ica_iterations": data.ica.iterations,
                          "source_recovery_correlations": cross_correlation(data.sources, data.ica.sources).tolist(),
                          "estimated_mixing": data.ica.mixing.tolist(),
                          "unmixing": data.ica.unmixing.tolist()})
        if scene_id == "3":
            entry["retained_variance_fraction"] = float(data.variance_ratios[:2].sum())
            entry["full_ica_recovery_correlations"] = cross_correlation(data.sources, data.full_ica.sources).tolist()
            entry["weak_axis_angles_degrees"] = [direction_angle(data.ica.mixing[:, 1], data.mixing[:, j]) for j in (1, 2)]
            entry["true_weak_axes_angle_degrees"] = direction_angle(data.mixing[:, 1], data.mixing[:, 2])
        if scene_id == "4":
            entry["ica_skipped_reason"] = "Two identical sources produce rank-one observations; two-source ICA is not identifiable."
        report["scenes"][scene_id] = entry
    return report
