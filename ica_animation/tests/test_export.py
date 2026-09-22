"""Tiny end-to-end exports exercise the video and audio tool chain."""
from pathlib import Path
import json
import shutil
import subprocess
import numpy as np
import pytest
from scipy.io import wavfile
from ica_animation.config import load_config
from ica_animation.render import render_video
from ica_animation.audio import create_sonification

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.skipif(shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
                    reason="FFmpeg and FFprobe are required for this integration test.")
def test_mp4_with_audio(tmp_path):
    config = load_config(ROOT / "config/default.yml")
    path = tmp_path / "smoke.mp4"
    render_video(config, list("1234"), path, 640, 360, 3, duration_scale=0.03, audio=True)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)],
                            text=True, capture_output=True, check=True)
    streams = json.loads(probe.stdout)["streams"]
    assert {stream["codec_type"] for stream in streams} == {"video", "audio"}
    video = next(stream for stream in streams if stream["codec_type"] == "video")
    assert (video["width"], video["height"]) == (640, 360)
    with pytest.raises(FileExistsError):
        render_video(config, ["1"], path, 640, 360, 3)


def test_gif_export(tmp_path):
    config = load_config(ROOT / "config/default.yml")
    path = tmp_path / "smoke.gif"
    render_video(config, ["1"], path, 320, 180, 3, duration_scale=0.03)
    assert path.read_bytes().startswith(b"GIF8")


def test_sonification_is_stereo_and_not_clipped(tmp_path):
    config = load_config(ROOT / "config/default.yml")
    path = tmp_path / "audio.wav"
    create_sonification(config, ["4"], 0.03, path)
    rate, samples = wavfile.read(path)
    assert rate == 24000
    assert samples.shape[1] == 2
    assert 0 < np.abs(samples.astype(float)).max() < 32767
