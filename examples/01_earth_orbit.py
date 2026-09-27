"""Sun, Earth, Moon. Camera follows Earth. Trail dries like water.

Low quality, as agreed:
    manimgl examples/01_earth_orbit.py EarthOrbitDemo -w -r 854x480 --fps 30 -c "#000000" --video_dir videos
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from universe.scene import UniverseScene
from universe.templates import EarthOrbit


class EarthOrbitDemo(UniverseScene):
    def construct(self):
        EarthOrbit(seconds=4, trail=True, camera="follow", label="পৃথিবী").play(self)
