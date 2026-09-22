"""Scientific regression tests: no hand-drawn or fabricated ICA directions."""
from pathlib import Path
import numpy as np
import pytest
from ica_animation.config import load_config
from ica_animation.model import (mixing_from_positions, make_scene_data, fit_ica,
                                  cross_correlation, direction_angle, diagnostics)

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(scope="module")
def config():
    return load_config(ROOT / "config/default.yml")


def test_inverse_distance_amplitude_and_inverse_square_intensity():
    speakers = [{"position": [0, 0]}]
    microphones = [{"position": [1, 0]}, {"position": [2, 0]}]
    matrix, distances = mixing_from_positions(speakers, microphones)
    assert matrix[1, 0] / matrix[0, 0] == pytest.approx(0.5)
    assert matrix[1, 0] ** 2 / matrix[0, 0] ** 2 == pytest.approx(0.25)
    np.testing.assert_allclose(distances[:, 0], [1, 2])


def test_collocated_devices_are_rejected():
    with pytest.raises(ValueError, match="distances"):
        mixing_from_positions([{"position": [0, 0]}], [{"position": [0, 0]}])


def test_mixture_convention(config):
    data = make_scene_data(config, "1")
    np.testing.assert_allclose(data.observations, data.sources @ data.mixing.T)
    np.testing.assert_allclose(data.observations @ np.linalg.inv(data.mixing).T, data.sources, atol=1e-12)


def test_two_sources_have_low_correlation_and_recover(config):
    data = make_scene_data(config, "2")
    assert abs(cross_correlation(data.sources, data.sources)[0, 1]) < 0.03
    assert np.abs(np.diag(cross_correlation(data.sources, data.ica.sources))).min() > 0.99
    np.testing.assert_allclose(data.ica.sources, (data.observations - data.ica.mean) @ data.ica.unmixing.T, atol=1e-10)
    np.testing.assert_allclose(data.ica.sources @ data.ica.mixing.T + data.ica.mean, data.observations, atol=1e-10)


def test_alternating_sources_never_overlap(config):
    data = make_scene_data(config, "2")
    assert np.all(np.count_nonzero(np.abs(data.alternate_sources) > 1e-12, axis=1) <= 1)


def test_three_sources_two_components_preserve_dominant_but_mix_weak(config):
    data = make_scene_data(config, "3")
    correlations = np.abs(cross_correlation(data.sources, data.ica.sources))
    assert correlations[0, 0] > 0.99
    assert 0.5 < correlations[1, 1] < 0.9
    assert 0.5 < correlations[2, 1] < 0.9
    assert data.sources[:, 0].var() > 20 * data.sources[:, 1].var()
    assert data.variance_ratios[:2].sum() > 0.99
    separation = direction_angle(data.mixing[:, 1], data.mixing[:, 2])
    assert direction_angle(data.ica.mixing[:, 1], data.mixing[:, 1]) < separation
    assert direction_angle(data.ica.mixing[:, 1], data.mixing[:, 2]) < separation
    assert np.abs(np.diag(cross_correlation(data.sources, data.full_ica.sources))).min() > 0.99


def test_identical_sources_have_rank_one_despite_invertible_mixing(config):
    data = make_scene_data(config, "4")
    np.testing.assert_array_equal(data.sources[:, 0], data.sources[:, 1])
    assert np.linalg.matrix_rank(data.mixing) == 2
    assert np.linalg.matrix_rank(data.observations) == 1
    np.testing.assert_allclose(data.observations, data.sources[:, :1] * data.mixing.sum(axis=1))
    with pytest.raises(ValueError, match="rank-1"):
        fit_ica(data.observations, 2, config["seed"])


def test_third_microphone_variant():
    config = load_config(ROOT / "config/third_microphone.yml")
    data = make_scene_data(config, "2")
    assert data.observations.shape[1] == 3
    assert data.ica.sources.shape[1] == 2
    assert np.abs(np.diag(cross_correlation(data.sources, data.ica.sources))).min() > 0.99


def test_deterministic(config):
    left = make_scene_data(config, "3")
    right = make_scene_data(config, "3")
    np.testing.assert_allclose(left.ica.mixing, right.ica.mixing, atol=1e-12)
