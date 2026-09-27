"""Connected templates. One plays, then the next, on the same universe."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Template:
    seconds: float = 5.0
    _next: "Template | None" = field(default=None, repr=False)

    def then(self, other: "Template") -> "Template":
        tail = self
        while tail._next is not None:
            tail = tail._next
        tail._next = other
        return self

    def play(self, scene) -> None:
        universe = scene.ensure_universe()
        self.apply(universe)
        scene.hold(self.seconds)
        if self._next is not None:
            self._next.play(scene)

    def apply(self, universe) -> None:
        raise NotImplementedError


class SolarWide(Template):
    """The whole system, slow orbit of the camera, title optional."""

    def __init__(self, seconds: float = 6.0, label: str = "সৌরজগৎ", theta_speed: float = 6.0):
        super().__init__(seconds=seconds)
        self.label = label
        self.theta_speed = theta_speed

    def apply(self, universe) -> None:
        for name in ("Sun", "Mercury", "Venus", "Earth", "Moon", "Mars",
                     "Jupiter", "Saturn", "Uranus", "Neptune"):
            universe.ensure(name)
        universe.camera.wide(height=20, phi=62, theta_speed=self.theta_speed)
        if self.label:
            universe.camera.set_label(self.label)


class EarthOrbit(Template):
    """Only the Sun, Earth and Moon. Camera can follow Earth."""

    def __init__(
        self,
        seconds: float = 6.0,
        camera: str = "follow",
        trail: bool = True,
        dry_time: float = 3.5,
        show_axis: bool = True,
        label: str = "পৃথিবী",
        seconds_per_year: float = 10.0,
    ):
        super().__init__(seconds=seconds)
        self.camera_mode = camera
        self.trail = trail
        self.dry_time = dry_time
        self.show_axis = show_axis
        self.label = label
        self.seconds_per_year = seconds_per_year

    def apply(self, universe) -> None:
        universe.clock.seconds_per_year = self.seconds_per_year
        universe.ensure("Sun")
        earth = universe.ensure("Earth")
        universe.ensure("Moon")
        if self.trail:
            earth.trail(dry_time=self.dry_time, color="#7EB6FF")
        if self.show_axis:
            earth.show_axis(color="#E7C98A", opacity=0.85, stroke_width=2.0)
        if self.camera_mode == "follow":
            universe.camera.follow("Earth", height=5.2, phi=52)
        elif self.camera_mode == "top":
            universe.camera.top("Earth", height=8)
        else:
            universe.camera.zoom_to("Earth", height=4.2, phi=50)
        if self.label:
            universe.camera.set_label(self.label)


class MoonViewpoint(Template):
    """Put the camera at the Moon and look back at Earth."""

    def __init__(self, seconds: float = 5.0, label: str = "চাঁদ থেকে পৃথিবী"):
        super().__init__(seconds=seconds)
        self.label = label

    def apply(self, universe) -> None:
        universe.ensure("Sun")
        universe.ensure("Earth")
        universe.ensure("Moon")
        universe.camera.place_at("Moon", look_at="Earth", height=1.2)
        if self.label:
            universe.camera.set_label(self.label)


class GravityWell(Template):
    """Cloth with a mass in the middle. The spacetime dent."""

    def __init__(self, seconds: float = 5.0, depth: float = 1.4, label: str = "মাধ্যাকর্ষণ"):
        super().__init__(seconds=seconds)
        self.depth = depth
        self.label = label

    def apply(self, universe) -> None:
        universe.show_fabric(depth=self.depth)
        universe.camera.wide(height=8, phi=55, theta_speed=4)
        if self.label:
            universe.camera.set_label(self.label)


class LightBend(Template):
    """A ray that bends as it passes a mass. A teaching sketch, not full GR."""

    def __init__(self, seconds: float = 5.0, label: str = "আলোর বাঁক"):
        super().__init__(seconds=seconds)
        self.label = label

    def apply(self, universe) -> None:
        universe.show_light_bend()
        universe.camera.wide(height=8, phi=70, theta_speed=0)
        if self.label:
            universe.camera.set_label(self.label)


class FallingApple(Template):
    """Newton's apple, falling toward a mass."""

    def __init__(self, seconds: float = 4.0, label: str = "আপেল"):
        super().__init__(seconds=seconds)
        self.label = label

    def apply(self, universe) -> None:
        universe.show_apple()
        universe.camera.wide(height=7, phi=72, theta_speed=0)
        if self.label:
            universe.camera.set_label(self.label)
