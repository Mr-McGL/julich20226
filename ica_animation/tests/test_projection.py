"""Regression tests for the visible correspondence between paths and mixing lines."""
from pathlib import Path

import numpy as np
import pytest

from ica_animation.config import load_config, Labels
from ica_animation.model import make_scene_data
from ica_animation.projection import flatten_points, projection_guides, mixing_coordinates
from ica_animation.render import Storyboard

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def config():
    return load_config(ROOT / "config/default.yml")


@pytest.mark.parametrize("amount", [0.0, 0.35, 1.0])
def test_projection_never_changes_microphone_coordinates(amount):
    points = np.array([[0.5, -0.3, 8.0], [1.2, 2.1, -4.0]])
    original = points.copy()
    projected = flatten_points(points, amount)
    np.testing.assert_array_equal(projected[:, :2], points[:, :2])
    np.testing.assert_allclose(projected[:, 2], points[:, 2] * (1 - amount))
    np.testing.assert_array_equal(points, original)


def test_guides_connect_each_point_to_its_exact_floor_projection():
    points = np.array([[0.2, 0.5, 3.0], [-0.7, 0.6, 10.0]])
    segments = projection_guides(points)
    np.testing.assert_array_equal(segments[:, 0], points)
    np.testing.assert_array_equal(segments[:, 1, :2], points[:, :2])
    np.testing.assert_array_equal(segments[:, 1, 2], 0.0)


@pytest.mark.parametrize("source", [0, 1])
def test_single_source_points_lie_on_the_matching_column(config, source):
    data = make_scene_data(config, "2")
    active = data.alternate_active == source
    points = data.alternate_observations[active, :2]
    direction = data.mixing[:2, source]
    determinant = points[:, 0] * direction[1] - points[:, 1] * direction[0]
    np.testing.assert_allclose(determinant, 0.0, atol=1e-14)


@pytest.mark.parametrize("progress,source", [(0.37, 0), (0.47, 1)])
def test_highlight_and_cross_view_arrow_follow_the_same_sample(config, progress, source):
    board = Storyboard(config, ["2"], 640, 360)
    board.draw(progress * board.duration, fade=False)
    scene = board.scene
    moving = np.array(scene.moving_markers[source].get_data_3d()).T
    floor = np.array(scene.floor_markers[source].get_data_3d()).T
    right = np.column_stack(scene.focus2[source].get_data())
    np.testing.assert_allclose(moving[:, :2], floor[:, :2])
    np.testing.assert_allclose(floor[:, :2], right)
    np.testing.assert_allclose(scene.links[source].xy2, right[0])
    assert floor[0, 2] == 0
    assert scene.links[source].get_visible()


def test_top_view_shows_identical_mixing_lines_in_both_panels(config):
    board = Storyboard(config, ["2"], 640, 360)
    board.draw(0.558 * board.duration, fade=False)
    scene = board.scene
    for source in range(2):
        floor_line = np.array(scene.axes3[source].get_data_3d()).T
        right_line = np.column_stack(scene.basis2[source].get_data())
        floor_points = np.array(scene.landing_lines[source].get_data_3d()).T
        right_points = np.column_stack(scene.dots2[source].get_data())
        np.testing.assert_allclose(floor_line[:, :2], right_line)
        np.testing.assert_allclose(floor_points[:, :2], right_points)
        np.testing.assert_array_equal(floor_points[:, 2], 0.0)
    assert len(scene.ax3.get_zticks()) == 0
    assert scene.ax3.get_zlabel() == ""
    board.draw(0.22 * board.duration, fade=False)
    assert len(scene.ax3.get_zticks()) > 0
    assert scene.ax3.get_zlabel() == "Time"


def test_coordinate_change_is_distinct_from_floor_projection(config):
    data = make_scene_data(config, "2")
    np.testing.assert_allclose(mixing_coordinates(data.mixing[:2], 0), np.eye(2))
    transform = mixing_coordinates(data.mixing[:2], 1)
    np.testing.assert_allclose(transform @ data.mixing[:2], np.eye(2), atol=1e-12)
    sources = data.alternate_observations[:, :2] @ transform.T
    np.testing.assert_allclose(sources, data.alternate_sources, atol=1e-12)
    board = Storyboard(config, ["2"], 640, 360)
    board.draw(0.64 * board.duration, fade=False)
    scene = board.scene
    assert not any(link.get_visible() for link in scene.links)
    for source in range(2):
        points = np.column_stack(scene.dots2[source].get_data())
        np.testing.assert_allclose(points[:, 1 - source], 0.0, atol=1e-12)


def test_singular_microphone_pair_is_rejected():
    with pytest.raises(ValueError, match="invertible"):
        mixing_coordinates(np.ones((2, 2)), 1)


def test_caption_catalog_excludes_signal_generation_details():
    text = " ".join(Labels().values.values()).lower()
    for phrase in ("yaml", "frequency", "random seed", "generated", "pitch", "simulated"):
        assert phrase not in text
