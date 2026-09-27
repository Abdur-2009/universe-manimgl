"""Scene base. User scenes call templates, or talk to self.universe."""

from manimlib import ThreeDScene

from universe.engine import Universe


class UniverseScene(ThreeDScene):
    samples = 1

    def ensure_universe(self) -> Universe:
        if not hasattr(self, "universe"):
            self.universe = Universe(self)
        return self.universe

    def hold(self, seconds: float) -> None:
        self.ensure_universe()
        self.wait(seconds)
