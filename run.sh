#!/usr/bin/env bash
set -euo pipefail

# Helper script to create a venv, install dependencies and run the app.
# Usage:
#   ./run.sh path/to/audio.mp3

VENV_DIR=".venv"
PYTHON="${PYTHON:-python3}"

if [ ! -x "$(command -v "$PYTHON")" ]; then
  echo "Error: $PYTHON not found. Install Python 3 and try again." >&2
  exit 2
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in $VENV_DIR..."
  $PYTHON -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [ "$#" -lt 1 ]; then
  echo "Usage: ./run.sh path/to/audio.mp3" >&2
  exit 2
fi

echo "Run: python app.py $@"
python app.py "$@"
