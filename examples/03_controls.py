"""Direct control: axis color, opacity, stroke, pause the spin, drying trail."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from universe.scene import UniverseScene


class ControlsDemo(UniverseScene):
    def construct(self):
        universe = self.ensure_universe()
        universe.ensure("Sun")
        earth = universe.ensure("Earth")
        earth.show_axis(color="#E7C98A", opacity=0.9, stroke_width=3)
        earth.set_stroke(width=1.5, color="#FFFFFF", opacity=0.4)
        earth.trail(dry_time=2.5, color="#7EB6FF")
        universe.camera.follow("Earth", height=5)
        universe.camera.set_label("অক্ষ")
        self.hold(2)
        earth.pause_spin()
        earth.set_opacity(0.55)
        self.hold(2)
