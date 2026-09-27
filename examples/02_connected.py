"""Templates joined in one shot. Wide system, then Earth, then the Moon's view."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from universe.scene import UniverseScene
from universe.templates import EarthOrbit, MoonViewpoint, SolarWide


class ConnectedDemo(UniverseScene):
    def construct(self):
        (
            SolarWide(seconds=3, label="সৌরজগৎ")
            .then(EarthOrbit(seconds=3, label="পৃথিবী"))
            .then(MoonViewpoint(seconds=3))
            .play(self)
        )
