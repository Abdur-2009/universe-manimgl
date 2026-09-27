"""The step-1 film. Same calls in ManimGL and ManimCE.

Wide system, then Earth with a drying trail, a pause, then the Moon's view.

ManimGL, low quality:
    manimgl examples/film.py UniverseFilm -w -r 854x480 --fps 30 -c "#000000" --video_dir videos --file_name universe_film

ManimCE, OpenGL, same quality:
    manim --renderer opengl examples/film.py UniverseFilm -r 854,480 --fps 30 --format mp4 --media_dir videos --disable_caching
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from universe.scene import UniverseScene
from universe.templates import EarthOrbit, MoonViewpoint, SolarWide


class UniverseFilm(UniverseScene):
    def construct(self):
        SolarWide(seconds=4, label="সৌরজগৎ").play(self)

        EarthOrbit(seconds=5, trail=True, camera="follow", label="পৃথিবী").play(self)

        earth = self.universe.body("Earth")
        earth.pause_spin()
        earth.pause_orbit()
        self.universe.camera.set_label("থামানো")
        self.hold(2)
        earth.resume_spin()
        earth.resume_orbit()

        for name in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"):
            self.universe.body(name).set_opacity(0)
        MoonViewpoint(seconds=4, label="চাঁদ থেকে পৃথিবী").play(self)
