"""The cloth, the bent ray, the apple. Connected, not three separate programs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from universe.scene import UniverseScene
from universe.templates import FallingApple, GravityWell, LightBend


class SpacetimeDemo(UniverseScene):
    def construct(self):
        (
            GravityWell(seconds=3)
            .then(LightBend(seconds=3))
            .then(FallingApple(seconds=3))
            .play(self)
        )
