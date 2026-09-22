"""Optional audible sonification, explicitly separate from the plotted time scale."""
from __future__ import annotations
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.ndimage import gaussian_filter1d
from .model import mixing_from_positions
from .timeline import SCENE2


def create_sonification(config: dict, scene_ids: list[str], duration_scale: float,
                         output: Path, sample_rate: int = 24000, pitch_scale: float = 180.0) -> None:
    """Write a stereo mixture of the first two microphones, not speech audio.

Visual frequencies are sub-audible. A fixed frequency multiplier makes
these illustrative signals audible; this is not a physical audio simulation.
Global normalization preserves all relative channel/source gains.
"""
    clips = []
    for scene_id in scene_ids:
        scene = config["scenes"][scene_id]
        duration = scene["duration"] * duration_scale
        count = int(round(duration * sample_rate))
        time = np.arange(count) / sample_rate
        progress = time / duration
        source_count = len(scene["speakers"])
        amplitudes = np.asarray(scene.get("amplitudes", config["signals"]["amplitudes"])[:source_count])
        frequencies = np.asarray(config["signals"]["frequencies"][:source_count]) * pitch_scale
        phases = np.asarray(config["signals"]["phases"][:source_count])
        if np.max(frequencies) >= sample_rate / 2:
            raise ValueError("Sonification frequencies exceed the audio Nyquist limit.")
        signals = amplitudes * np.sin(2 * np.pi * time[:, None] * frequencies + phases)
        activity = np.zeros((count, source_count))
        if scene_id == "1":
            activity[progress >= 0.13] = 1
        elif scene_id == "2":
            alternating = (progress >= SCENE2["alternate_start"]) & (progress < SCENE2["alternate_end"])
            active = (np.clip((progress - SCENE2["alternate_start"]) / (SCENE2["alternate_end"] - SCENE2["alternate_start"]), 0, 1) * scene["alternate_bursts"]).astype(int) % 2
            for j in range(source_count):
                activity[alternating & (active == j), j] = 1
            activity[(progress >= SCENE2["simultaneous_start"]) & (progress < SCENE2["simultaneous_end"])] = 1
        elif scene_id == "3":
            # The timeless dataset intentionally has no moving playback cursor.
            activity[:] = 0
        else:
            signals[:, 1] = signals[:, 0]
            activity[(progress >= 0.03) & (progress < 0.58)] = 1
        activity = gaussian_filter1d(activity, sigma=max(1, int(sample_rate * 0.008)), axis=0)
        edge = np.minimum(np.minimum(time / 0.05, (duration - time) / 0.05), 1)
        signals *= activity * np.clip(edge[:, None], 0, 1)
        matrix, _ = mixing_from_positions(scene["speakers"], scene["microphones"], **config["physics"])
        stereo = signals @ matrix[:2].T
        if stereo.shape[1] == 1:
            stereo = np.repeat(stereo, 2, axis=1)
        clips.append(stereo.astype(np.float32))
    audio = np.concatenate(clips)
    peak = max(float(np.max(np.abs(audio))), 1e-8)
    audio = np.clip(audio / peak * 0.78, -1, 1)
    output.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(output, sample_rate, (audio * 32767).astype(np.int16))
