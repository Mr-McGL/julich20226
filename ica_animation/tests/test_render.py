"""Exercise every editorial stage, reverse seeking, and alternative geometry."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pytest
from ica_animation.config import load_config
from ica_animation.render import Storyboard, KEYFRAMES
from ica_animation.cli import main

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize("scene_id", list("1234"))
def test_all_keyframes_render_and_support_reverse_seeking(scene_id):
    config = load_config(ROOT / "config/default.yml")
    board = Storyboard(config, [scene_id], 640, 360)
    for progress in KEYFRAMES[scene_id] + list(reversed(KEYFRAMES[scene_id])):
        board.draw(progress * board.duration, fade=False)
        board.figure.canvas.draw()
        image = np.asarray(board.figure.canvas.buffer_rgba())
        assert image.shape == (360, 640, 4)
        assert np.count_nonzero(image[:, :, :3]) > 1000
    board.figure.clear()


def test_variant_renders():
    config = load_config(ROOT / "config/third_microphone.yml")
    board = Storyboard(config, ["2"], 640, 360)
    for progress in (0.29, 0.49, 0.595, 0.84, 0.955):
        board.draw(progress * board.duration, fade=False)
        board.figure.canvas.draw()


def test_cli_diagnostics(tmp_path):
    output = tmp_path / "diagnostics.json"
    assert main(["inspect", "--config", str(ROOT / "config/default.yml"), "--output", str(output)]) == 0
    assert output.is_file()


def test_cli_rejects_invalid_size(tmp_path):
    assert main(["stills", "--config", str(ROOT / "config/default.yml"), "--width", "701", "--height", "400"]) == 2
