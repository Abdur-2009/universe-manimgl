"""ManimGL drawing. The spec in model.py is the source of truth each frame."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from manimlib import (
    DEGREES,
    ORIGIN,
    OUT,
    RIGHT,
    TAU,
    Circle,
    GlowDot,
    Group,
    Line,
    Sphere,
    Surface,
    Text,
    TexturedSurface,
    UL,
    VGroup,
    VMobject,
)

from universe.handles import BodyHandle, CameraHandle
from universe.model import (
    BodySpec,
    CameraSpec,
    Clock,
    copy_spec,
    font_for,
    pole_of,
    position_at,
    solar_catalog,
)

TEXTURES = Path(__file__).resolve().parent / "assets" / "textures"
SPHERE_RESOLUTION = (32, 16)


class Well(Surface):
    def __init__(self, span: float = 6.0, depth: float = 1.4, sigma: float = 0.8, resolution=(41, 41)):
        self.span = span
        self.depth = depth
        self.sigma = sigma
        super().__init__(u_range=(0, 1), v_range=(0, 1), resolution=resolution, color="#1C3A66")

    def uv_func(self, u: float, v: float) -> np.ndarray:
        x = (u - 0.5) * self.span
        y = (v - 0.5) * self.span
        dent = self.depth / (1.0 + (x * x + y * y) / self.sigma)
        return np.array([x, y, -dent])


class Universe:
    def __init__(self, scene: ThreeDScene):
        self.scene = scene
        self.clock = Clock()
        self.bodies: dict[str, BodySpec] = {}
        self.camera_spec = CameraSpec()
        self.camera = CameraHandle(self)
        self._mobs: dict[str, object] = {}
        self._orbits: dict[str, Circle] = {}
        self._axes: dict[str, Line] = {}
        self._trails: dict[str, list] = {}
        self._trail_group = VGroup()
        self._label = None
        self._extras = Group()
        self._apple_t = 0.0
        self.scene.camera.light_source.move_to(ORIGIN)
        self.scene.add(self._trail_group, self._extras)
        driver = VMobject()
        driver.add_updater(self._tick)
        self.scene.add(driver)

    def ensure(self, name: str) -> BodyHandle:
        if name not in self.bodies:
            spec = copy_spec(solar_catalog()[name])
            self.bodies[name] = spec
            self._build_body(spec)
        return BodyHandle(self, name)

    def body(self, name: str) -> BodyHandle:
        return self.ensure(name)

    def drop_trail(self, name: str) -> None:
        self._trails.pop(name, None)

    def _texture(self, name: str | None) -> str | None:
        if not name:
            return None
        path = TEXTURES / name
        return str(path) if path.exists() else None

    def _sphere(self, spec: BodySpec):
        image = self._texture(spec.texture)
        night = self._texture(spec.night_texture)
        base = Sphere(radius=spec.radius, resolution=SPHERE_RESOLUTION)
        if image:
            surface = TexturedSurface(base, image, night)
            if spec.kind == "star":
                surface.set_shading(0.0, 0.0, 0.0)
            else:
                surface.set_shading(0.4, 0.08, 0.6)
            return surface
        base.set_color(spec.style.color)
        return base

    def _build_body(self, spec: BodySpec) -> None:
        surface = self._sphere(spec)
        if spec.has_rings:
            ring = _Ring(spec.radius * spec.ring_inner, spec.radius * spec.ring_outer)
            ring.set_color(spec.ring_color)
            ring.set_opacity(0.85)
            mob = Group(surface, ring)
        else:
            mob = surface
        tilt = spec.tilt_deg * DEGREES
        mob.rotate(tilt, axis=RIGHT)
        self._mobs[spec.name] = mob
        self.scene.add(mob)
        if spec.kind == "star":
            self.scene.add(GlowDot(radius=0.4, color="#FFE6B0", glow_factor=3.0))
        if spec.kind == "planet":
            orbit = Circle(radius=spec.orbit_radius)
            orbit.set_stroke("#9BB0C8", width=1.1, opacity=0.18)
            self._orbits[spec.name] = orbit
            self.scene.add(orbit)
        axis = Line(ORIGIN, OUT)
        axis.set_stroke(spec.axis.color, width=spec.axis.stroke_width, opacity=0)
        self._axes[spec.name] = axis
        self.scene.add(axis)

    def position_of(self, name: str) -> np.ndarray:
        spec = self.bodies[name]
        parent = None
        if spec.parent and spec.parent in self.bodies:
            parent = self.position_of(spec.parent)
        return position_at(spec, self.clock.years, parent)

    def _tick(self, _mob, dt: float) -> None:
        self.clock.advance(dt)
        self._apple_t += dt
        years = self.clock.years
        for name, spec in self.bodies.items():
            self._place(name, spec, years, dt)
        self._aim(dt)
        self._draw_trails()
        self._place_apple()

    def _place(self, name: str, spec: BodySpec, years: float, dt: float) -> None:
        mob = self._mobs[name]
        point = self.position_of(name)
        if not spec.spin_paused and spec.spin_hours != 0:
            delta = 0.7 * dt * (1 if spec.spin_hours > 0 else -1)
            spec.spin_angle += delta
            mob.rotate(delta, axis=pole_of(spec), about_point=mob.get_center())
        mob.move_to(point)
        try:
            mob.set_opacity(spec.style.opacity)
        except Exception:
            pass
        axis = self._axes[name]
        if spec.axis.visible:
            pole = pole_of(spec) * spec.radius * spec.axis.length_scale
            axis.put_start_and_end_on(point - pole, point + pole)
            axis.set_stroke(spec.axis.color, width=spec.axis.stroke_width, opacity=spec.axis.opacity)
        else:
            axis.set_stroke(opacity=0)
        if spec.style.stroke_width > 0:
            try:
                mob.set_stroke(
                    spec.style.stroke_color,
                    width=spec.style.stroke_width,
                    opacity=spec.style.stroke_opacity * spec.style.opacity,
                )
            except Exception:
                pass
        if not spec.texture:
            try:
                mob.set_color(spec.style.color)
            except Exception:
                pass
        if spec.trail.enabled:
            samples = self._trails.setdefault(name, [])
            if not samples or self.clock.t - samples[-1][0] >= 0.05:
                samples.append((self.clock.t, np.array(point)))
            dry = spec.trail.dry_time
            self._trails[name] = [(t, p) for t, p in samples if self.clock.t - t <= dry]

    def _draw_trails(self) -> None:
        pieces = VGroup()
        for name, samples in self._trails.items():
            spec = self.bodies[name]
            if not spec.trail.enabled or len(samples) < 2:
                continue
            for (t0, p0), (t1, p1) in zip(samples, samples[1:]):
                age = self.clock.t - t1
                fade = max(spec.trail.min_opacity, 1.0 - age / max(spec.trail.dry_time, 1e-3))
                if fade <= 0.02:
                    continue
                segment = Line(p0, p1)
                segment.set_stroke(spec.trail.color, width=spec.trail.width * fade, opacity=fade * spec.style.opacity)
                pieces.add(segment)
        self.scene.remove(self._trail_group)
        self._trail_group = pieces
        self.scene.add(self._trail_group)

    def _aim(self, dt: float) -> None:
        spec = self.camera_spec
        spec.theta += spec.theta_speed * dt
        target_name = spec.target if spec.target in self.bodies else "Sun"
        target = self.position_of(target_name) if target_name in self.bodies else np.zeros(3)
        if spec.mode == "wide":
            center, height, phi, theta = np.zeros(3), spec.height, spec.phi, spec.theta
        elif spec.mode == "top":
            center, height, phi, theta = target, spec.height, 8.0, spec.theta
        elif spec.mode == "from_body" and spec.viewpoint in self.bodies:
            origin = self.position_of(spec.viewpoint)
            delta = target - origin
            norm = np.linalg.norm(delta) or 1.0
            raw = float(np.degrees(np.arccos(np.clip(delta[2] / norm, -1.0, 1.0))))
            # Keep the Moon's direction, but do not drop to a pure edge-on line.
            phi = 0.35 * raw + 0.65 * 52.0
            theta = float(np.degrees(np.arctan2(delta[1], delta[0])))
            center, height = target, spec.height
        else:
            center, height, phi, theta = target, spec.height, spec.phi, spec.theta
        self.scene.frame.reorient(theta, phi, 0, center, height)
        close = height < 8
        for name, orbit in self._orbits.items():
            body_opacity = self.bodies[name].style.opacity
            base = 0.05 if close else 0.18
            orbit.set_stroke(opacity=base * body_opacity)

    def refresh_label(self) -> None:
        if self._label is not None:
            self.scene.remove(self._label)
            self._label = None
        text = self.camera_spec.label
        if not text:
            return
        label = Text(text, font=font_for(text), font_size=36).set_color("#F6E7C1")
        label.to_corner(UL, buff=0.35)
        label.fix_in_frame()
        self._label = label
        self.scene.add(label)

    def show_fabric(self, depth: float = 1.4) -> None:
        well = Well(depth=depth)
        well.set_shading(0.3, 0.05, 0.4)
        mass = Sphere(radius=0.28, resolution=(24, 12)).set_color("#F4E8C8")
        mass.move_to(0.15 * OUT)
        self._extras.add(well, mass)

    def show_light_bend(self) -> None:
        mass = Sphere(radius=0.35, resolution=(24, 12)).set_color("#F6E7C1")
        points = []
        for x in np.linspace(-4.5, 4.5, 60):
            bend = 0.85 / (1.0 + x * x)
            points.append(np.array([x, 0.15 + bend, 0.0]))
        ray = VMobject()
        ray.set_points_as_corners(points)
        ray.set_stroke("#FFE08A", width=3, opacity=0.95)
        self._extras.add(mass, ray)

    def show_apple(self) -> None:
        self._apple = Sphere(radius=0.16, resolution=(20, 10)).set_color("#C0392B")
        self._apple_t = 0.0
        self._extras.add(self._apple)

    def _place_apple(self) -> None:
        apple = getattr(self, "_apple", None)
        if apple is None:
            return
        fall = min(1.6, 0.5 * 2.2 * self._apple_t * self._apple_t)
        apple.move_to(np.array([0.8, 0.0, 1.8 - fall]))


class _Ring(Surface):
    def __init__(self, inner: float, outer: float):
        self.inner = inner
        self.outer = outer
        super().__init__(u_range=(0, TAU), v_range=(0, 1), resolution=(72, 4))

    def uv_func(self, u: float, v: float) -> np.ndarray:
        radius = self.inner + (self.outer - self.inner) * v
        return np.array([radius * np.cos(u), radius * np.sin(u), 0.0])
