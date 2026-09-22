"""Validation and translated labels."""
from copy import deepcopy
from pathlib import Path
import pytest
from ica_animation.config import load_config, validate_config, Labels

ROOT = Path(__file__).resolve().parents[1]


def test_english_is_the_default_language():
    assert Labels()("source", number=1) == "Speaker 1"
    assert load_config(ROOT / "config/default.yml")["language"] == "en"


def test_negative_duration_is_rejected():
    config = load_config(ROOT / "config/default.yml")
    config["scenes"]["1"]["duration"] = -1
    with pytest.raises(ValueError, match="duration"):
        validate_config(config)


def test_nyquist_is_checked():
    config = load_config(ROOT / "config/default.yml")
    config["signals"]["frequencies"][0] = 1000
    with pytest.raises(ValueError, match="Nyquist"):
        validate_config(config)


def test_inheritance_cycles_are_rejected(tmp_path):
    path = tmp_path / "cycle.yml"
    path.write_text("extends: cycle.yml\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Cyclic"):
        load_config(path)
