"""Fluent controls. Every setter writes the spec; the engine reads it each frame."""

from __future__ import annotations

from universe.model import BodySpec


class BodyHandle:
    def __init__(self, universe, name: str):
        self.universe = universe
        self.name = name

    @property
    def spec(self) -> BodySpec:
        return self.universe.bodies[self.name]

    def pause_spin(self):
        self.spec.spin_paused = True
        return self

    def resume_spin(self):
        self.spec.spin_paused = False
        return self

    def pause_orbit(self):
        self.spec.orbit_paused = True
        self.spec.frozen_years = self.universe.clock.years
        return self

    def resume_orbit(self):
        self.spec.orbit_paused = False
        return self

    def set_opacity(self, opacity: float):
        self.spec.style.opacity = opacity
        return self

    def set_color(self, color: str):
        self.spec.style.color = color
        return self

    def set_stroke(self, width: float = 1.0, color: str = "#FFFFFF", opacity: float = 1.0):
        self.spec.style.stroke_width = width
        self.spec.style.stroke_color = color
        self.spec.style.stroke_opacity = opacity
        return self

    def show_axis(self, color: str = "#E7C98A", opacity: float = 0.9, stroke_width: float = 2.0, length: float = 2.6):
        self.spec.axis.visible = True
        self.spec.axis.color = color
        self.spec.axis.opacity = opacity
        self.spec.axis.stroke_width = stroke_width
        self.spec.axis.length_scale = length
        return self

    def hide_axis(self):
        self.spec.axis.visible = False
        return self

    def trail(self, dry_time: float = 3.5, color: str | None = None, width: float = 2.2):
        self.spec.trail.enabled = True
        self.spec.trail.dry_time = dry_time
        self.spec.trail.width = width
        if color:
            self.spec.trail.color = color
        return self

    def clear_trail(self):
        self.spec.trail.enabled = False
        self.universe.drop_trail(self.name)
        return self


class CameraHandle:
    def __init__(self, universe):
        self.universe = universe

    @property
    def spec(self):
        return self.universe.camera_spec

    def wide(self, height: float = 20, phi: float = 62, theta_speed: float = 6):
        self.spec.mode = "wide"
        self.spec.target = "Sun"
        self.spec.viewpoint = None
        self.spec.height = height
        self.spec.phi = phi
        self.spec.theta_speed = theta_speed
        return self

    def top(self, target: str = "Sun", height: float = 18):
        self.spec.mode = "top"
        self.spec.target = target
        self.spec.viewpoint = None
        self.spec.height = height
        self.spec.phi = 8
        self.spec.theta_speed = 2
        return self

    def follow(self, name: str, height: float = 5.2, phi: float = 52):
        self.spec.mode = "follow"
        self.spec.target = name
        self.spec.viewpoint = None
        self.spec.height = height
        self.spec.phi = phi
        self.spec.theta_speed = 5
        return self

    def zoom_to(self, name: str, height: float = 4.0, phi: float = 50):
        self.spec.mode = "zoom"
        self.spec.target = name
        self.spec.viewpoint = None
        self.spec.height = height
        self.spec.phi = phi
        self.spec.theta_speed = 3
        return self

    def place_at(self, viewpoint: str, look_at: str, height: float = 3.2):
        """Camera sits on one body and looks at another. Moon looking at Earth."""
        self.spec.mode = "from_body"
        self.spec.viewpoint = viewpoint
        self.spec.target = look_at
        self.spec.height = height
        self.spec.theta_speed = 0
        return self

    def set_label(self, text: str | None, corner: str = "UL"):
        self.spec.label = text
        self.spec.label_corner = corner
        self.universe.refresh_label()
        return self

    def clear_label(self):
        return self.set_label(None)
