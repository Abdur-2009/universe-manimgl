#!/bin/sh
# Agreed test quality: 30 fps, 480p, 16:9. Not HD.
cd "$(dirname "$0")/.."
export PYTHONPATH=.
exec manimgl examples/01_earth_orbit.py EarthOrbitDemo -w -r 854x480 --fps 30 -c "#000000" --video_dir videos "$@"
