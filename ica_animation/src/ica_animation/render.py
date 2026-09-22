"""Video, still-frame, and interactive rendering front ends."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import math
import shutil
import subprocess
import sys
import time
import numpy as np
from matplotlib.animation import FFMpegWriter, PillowWriter
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from .graphics import apply_style
from .model import make_scene_data
from .scenes import SCENES

KEYFRAMES = {
    "1": [0.09, 0.28, 0.47, 0.66, 0.90],
    "2": [0.05, 0.22, 0.37, 0.415, 0.47, 0.52, 0.558, 0.64, 0.75, 0.85, 0.90, 0.965],
    "3": [0.22, 0.49, 0.75, 0.92],
    "4": [0.38, 0.74, 0.95],
}


class Storyboard:
    """A single figure shared by all scenes; all animation state is seekable."""

    def __init__(self, config: dict, scene_ids: list[str], width: int, height: int,
                 duration_scale: float = 1.0, figure: Figure | None = None) -> None:
        apply_style(config)
        self.config, self.scene_ids = config, scene_ids
        self.width, self.height = width, height
        self.dpi = width / 16
        self.figure = figure or Figure(figsize=(16, 16 * height / width), dpi=self.dpi)
        if figure is None:
            FigureCanvasAgg(self.figure)
        self.durations = np.array([config["scenes"][key]["duration"] * duration_scale for key in scene_ids])
        self.edges = np.r_[0, np.cumsum(self.durations)]
        self.duration = float(self.edges[-1])
        self.data = {key: make_scene_data(config, key) for key in scene_ids}
        self.current_index = None
        self.scene = None

    def draw(self, seconds: float, fade: bool = True) -> None:
        seconds = float(np.clip(seconds, 0, self.duration - 1e-9))
        index = min(int(np.searchsorted(self.edges[1:], seconds, side="right")), len(self.scene_ids) - 1)
        if self.current_index != index:
            self.current_index = index
            key = self.scene_ids[index]
            self.scene = SCENES[key](self.figure, self.config, self.data[key])
        progress = (seconds - self.edges[index]) / self.durations[index]
        self.scene.update(float(progress), fade=fade)


def render_video(config: dict, scene_ids: list[str], output: Path, width: int, height: int,
                 fps: int, duration_scale: float = 1.0, audio: bool = False,
                 overwrite: bool = False) -> dict:
    if output.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output}. Pass --overwrite to replace it.")
    suffix = output.suffix.lower()
    if suffix not in (".mp4", ".gif"):
        raise ValueError("Output must end in .mp4 or .gif.")
    if audio and suffix != ".mp4":
        raise ValueError("Audio is supported only for MP4 output.")
    if suffix == ".mp4" and shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg was not found. Activate the supplied Conda environment or install ffmpeg.")
    board = Storyboard(config, scene_ids, width, height, duration_scale)
    frame_count = int(math.ceil(board.duration * fps))
    if suffix == ".gif" and frame_count * width * height > 150_000_000:
        raise ValueError("This GIF would use too much memory. Use --preset draft with --scene 1, or export MP4.")
    output.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    last_report = -10.0
    with TemporaryDirectory(prefix="ica-render-", dir=output.parent) as temp:
        temporary = Path(temp)
        silent_path = temporary / ("silent" + suffix)
        if suffix == ".mp4":
            writer = FFMpegWriter(fps=fps, codec="libx264", bitrate=config["render"]["bitrate"],
                                  extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
                                  metadata={"title": "Blind source separation with ICA", "artist": "ICA animation project"})
        else:
            writer = PillowWriter(fps=fps)
        with writer.saving(board.figure, str(silent_path), dpi=board.dpi):
            for frame in range(frame_count):
                board.draw(frame / fps, fade=True)
                writer.grab_frame(facecolor=config["style"]["background"])
                elapsed = time.monotonic() - start
                if elapsed - last_report > 5 or frame == frame_count - 1:
                    print(f"Rendering frame {frame + 1}/{frame_count} ({100 * (frame + 1) / frame_count:.1f}%)", file=sys.stderr, flush=True)
                    last_report = elapsed
        if audio:
            from .audio import create_sonification
            wav_path = temporary / "sonification.wav"
            create_sonification(config, scene_ids, duration_scale, wav_path)
            complete_path = temporary / "complete.mp4"
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(silent_path),
                            "-i", str(wav_path), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                            "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(complete_path)], check=True)
            shutil.move(str(complete_path), str(output))
        else:
            shutil.move(str(silent_path), str(output))
    metadata = {"output": output.name, "scenes": scene_ids, "width": width, "height": height,
                "fps": fps, "frames": frame_count, "duration_seconds": frame_count / fps,
                "duration_scale": duration_scale, "audio": audio,
                "audio_note": "Sonification: visual frequencies multiplied by 180, first two microphones in stereo." if audio else None}
    output.with_suffix(output.suffix + ".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def render_stills(config: dict, scene_ids: list[str], output: Path, width: int, height: int,
                  progress: float | None = None) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    board = Storyboard(config, scene_ids, width, height)
    paths = []
    for index, key in enumerate(scene_ids):
        positions = [progress] if progress is not None else KEYFRAMES[key]
        for position in positions:
            board.draw(float(board.edges[index] + position * board.durations[index]), fade=False)
            path = output / f"scene_{key}_{int(round(position * 1000)):03d}.png"
            board.figure.savefig(path, dpi=board.dpi, facecolor=config["style"]["background"])
            paths.append(path)
    return paths


def play(config: dict, scene_ids: list[str], width: int, height: int, fps: int,
         duration_scale: float = 1.0) -> None:
    import matplotlib.pyplot as plt
    apply_style(config)
    figure = plt.figure(figsize=(16, 16 * height / width), dpi=width / 16)
    board = Storyboard(config, scene_ids, width, height, duration_scale, figure=figure)
    state = {"position": 0.0, "paused": False}
    timer = figure.canvas.new_timer(interval=round(1000 / fps))

    def tick() -> None:
        if not state["paused"]:
            board.draw(state["position"], fade=True)
            state["position"] = min(board.duration - 1e-6, state["position"] + 1 / fps)
            if state["position"] >= board.duration - 1e-6:
                state["paused"] = True
            figure.canvas.draw_idle()

    def on_key(event) -> None:
        if event.key in (" ", "space"):
            state["paused"] = not state["paused"]
        elif event.key in ("left", "right"):
            state["position"] = float(np.clip(state["position"] + (-2 if event.key == "left" else 2), 0, board.duration - 1e-6))
            board.draw(state["position"], fade=False)
            figure.canvas.draw_idle()
        elif event.key == "r":
            state["position"] = 0.0
            state["paused"] = False
        elif event.key == "escape":
            plt.close(figure)

    figure.canvas.mpl_connect("key_press_event", on_key)
    timer.add_callback(tick)
    board.draw(0, fade=False)
    timer.start()
    plt.show()
