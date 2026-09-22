"""Configuration loading, inheritance, localization, and validation."""
from __future__ import annotations

from copy import deepcopy
from importlib.resources import files
from pathlib import Path
from typing import Any
import math
import numpy as np
import yaml


def merge(base: dict, override: dict) -> dict:
    """Recursively merge dictionaries, replacing complete lists."""
    result = deepcopy(base)
    for key, value in override.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else deepcopy(value)
    return result


def load_config(path: str | Path, _seen: set[Path] | None = None) -> dict[str, Any]:
    path = Path(path).resolve()
    seen = set() if _seen is None else set(_seen)
    if path in seen:
        raise ValueError(f"Cyclic configuration inheritance: {path}")
    seen.add(path)
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a YAML mapping.")
    parent = config.pop("extends", None)
    if parent is not None:
        config = merge(load_config(path.parent / parent, seen), config)
    validate_config(config)
    return config


def validate_config(config: dict) -> None:
    for key in ("physics", "signals", "style", "render", "scenes"):
        if key not in config:
            raise ValueError(f"Missing configuration section: {key}")
    signals = config["signals"]
    if not isinstance(signals["samples"], int) or signals["samples"] < 200:
        raise ValueError("signals.samples must be an integer of at least 200.")
    if not math.isfinite(signals["duration"]) or signals["duration"] <= 0:
        raise ValueError("signals.duration must be positive and finite.")
    for key in ("reference_distance", "minimum_distance"):
        value = config["physics"][key]
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"physics.{key} must be positive and finite.")
    max_count = 0
    for scene_id in ("1", "2", "3", "4"):
        scene = config["scenes"][scene_id]
        if not math.isfinite(scene["duration"]) or scene["duration"] <= 0:
            raise ValueError(f"Scene {scene_id}: duration must be positive.")
        for kind in ("speakers", "microphones"):
            items = scene[kind]
            if not 1 <= len(items) <= 6:
                raise ValueError(f"Scene {scene_id}: use between 1 and 6 {kind}.")
            if len({item['id'] for item in items}) != len(items):
                raise ValueError(f"Scene {scene_id}: duplicate {kind} IDs.")
            points = np.asarray([item["position"] for item in items], dtype=float)
            if points.shape != (len(items), 2) or not np.isfinite(points).all():
                raise ValueError(f"Scene {scene_id}: positions must be finite [x, y] pairs.")
        sp = np.asarray([item["position"] for item in scene["speakers"]])
        mi = np.asarray([item["position"] for item in scene["microphones"]])
        if np.any(np.linalg.norm(mi[:, None] - sp[None], axis=2) < config["physics"]["minimum_distance"]):
            raise ValueError(f"Scene {scene_id}: a microphone is too close to a speaker.")
        max_count = max(max_count, len(sp))
    for key in ("frequencies", "amplitudes", "phases"):
        values = np.asarray(signals[key], dtype=float)
        if len(values) < max_count or not np.isfinite(values).all():
            raise ValueError(f"signals.{key} must have a finite value for every speaker.")
    if min(signals["frequencies"]) <= 0 or min(signals["amplitudes"]) <= 0:
        raise ValueError("Frequencies and amplitudes must be positive.")
    if max(signals["frequencies"]) >= signals["samples"] / signals["duration"] / 2:
        raise ValueError("The signal sampling rate violates the Nyquist limit.")
    second = config["scenes"]["2"]
    if second["third_axis"] not in ("time", "microphone_3"):
        raise ValueError("third_axis must be 'time' or 'microphone_3'.")
    expected_mics = 2 if second["third_axis"] == "time" else 3
    if len(second["speakers"]) != 2 or len(second["microphones"]) != expected_mics:
        raise ValueError(f"Scene 2 requires 2 speakers and {expected_mics} microphones.")
    if not isinstance(second["alternate_bursts"], int) or second["alternate_bursts"] < 2:
        raise ValueError("alternate_bursts must be an integer of at least 2.")
    third = config["scenes"]["3"]
    if len(third["speakers"]) != 3 or len(third["microphones"]) != 3 or third["components"] != 2:
        raise ValueError("Scene 3 requires 3 speakers, 3 microphones, and 2 components.")
    if len(third["amplitudes"]) != 3 or not np.isfinite(third["amplitudes"]).all() or min(third["amplitudes"]) <= 0:
        raise ValueError("Scene 3 requires three positive, finite amplitudes.")
    fourth = config["scenes"]["4"]
    if len(fourth["speakers"]) != 2 or len(fourth["microphones"]) != 2:
        raise ValueError("Scene 4 requires 2 speakers and 2 microphones.")
    if len(config["style"]["source_colors"]) < max_count:
        raise ValueError("Provide a source color for every speaker.")
    for name, preset in config["render"]["presets"].items():
        if any(not isinstance(preset[k], int) or preset[k] <= 0 for k in ("width", "height", "fps")):
            raise ValueError(f"Invalid dimensions or frame rate in preset: {name}")
        if preset["width"] % 2 or preset["height"] % 2:
            raise ValueError("Video dimensions must be even for H.264.")


class Labels:
    """Keep translated text out of the rendering code."""

    def __init__(self, language: str = "en") -> None:
        resource = files("ica_animation").joinpath("locales", f"{language}.yml")
        try:
            self.values = yaml.safe_load(resource.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise ValueError(f"Unsupported language: {language}") from error

    def __call__(self, key: str, **kwargs: Any) -> str:
        text = self.values[key].replace("\\n", "\n")
        return text.format(**kwargs) if kwargs else text
