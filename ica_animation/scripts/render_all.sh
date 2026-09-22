#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python run.py render --scene all --preset full --output output/ica_animation.mp4 "$@"
