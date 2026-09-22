"""Command-line entry point with validation and actionable error messages."""
from __future__ import annotations

import argparse
from pathlib import Path
import json
import sys

from .config import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render the four blind source separation animations.")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("render", "stills", "play", "inspect"):
        child = commands.add_parser(command)
        child.add_argument("--config", type=Path, default=Path("config/default.yml"))
        if command != "inspect":
            child.add_argument("--scene", choices=["all", "1", "2", "3", "4"], default="all")
            child.add_argument("--preset", choices=["draft", "preview", "full"], default=None)
            child.add_argument("--width", type=int)
            child.add_argument("--height", type=int)
            if command in ("render", "play"):
                child.add_argument("--fps", type=int)
                child.add_argument("--duration-scale", type=float, default=1.0)
        if command == "render":
            child.add_argument("--output", type=Path, default=Path("output/ica_animation.mp4"))
            child.add_argument("--audio", action="store_true", help="Add pitch-shifted stereo sonification, not speech.")
            child.add_argument("--overwrite", action="store_true")
        elif command == "stills":
            child.add_argument("--output", type=Path, default=Path("output/stills"))
            child.add_argument("--progress", type=float, help="One relative scene position in [0,1), instead of keyframes.")
        elif command == "inspect":
            child.add_argument("--output", type=Path, default=Path("output/diagnostics.json"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "inspect":
            from .model import diagnostics
            report = diagnostics(config)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
            print(f"Diagnostics written to {args.output}")
            return 0
        scene_ids = list("1234") if args.scene == "all" else [args.scene]
        preset_name = args.preset or config["render"]["preset"]
        preset = config["render"]["presets"][preset_name]
        if (args.width is None) != (args.height is None):
            raise ValueError("Provide both --width and --height, or neither.")
        width = args.width if args.width is not None else preset["width"]
        height = args.height if args.height is not None else preset["height"]
        if width < 320 or height < 180 or width % 2 or height % 2:
            raise ValueError("Dimensions must be even integers, at least 320 x 180.")
        # The editorial layout is designed for 16:9, not arbitrary aspect ratios.
        if abs(width / height - 16 / 9) > 0.015:
            raise ValueError("Use a 16:9 aspect ratio to preserve the animation layout.")
        if args.command != "play":
            import matplotlib
            matplotlib.use("Agg")
        from .render import play, render_stills, render_video
        if args.command == "stills":
            if args.progress is not None and not 0 <= args.progress < 1:
                raise ValueError("--progress must be in [0,1).")
            paths = render_stills(config, scene_ids, args.output, width, height, args.progress)
            print(f"Saved {len(paths)} still frames to {args.output}")
        else:
            fps = args.fps if args.fps is not None else preset["fps"]
            import math
            if fps <= 0 or not math.isfinite(args.duration_scale) or args.duration_scale <= 0:
                raise ValueError("Frame rate and duration scale must be positive and finite.")
            if args.command == "play":
                play(config, scene_ids, width, height, fps, args.duration_scale)
            else:
                render_video(config, scene_ids, args.output, width, height, fps, args.duration_scale,
                             args.audio, args.overwrite)
                print(f"Video written to {args.output}")
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0
