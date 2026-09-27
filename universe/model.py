"""Pure data for the universe. No Manim imports.

Both engine repos keep this file identical. Drawing lives in engine.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np

TAU = 2.0 * np.pi
DEG = TAU / 360.0


def font_for(text: str) -> str:
    """English uses Computer Modern. Bangla uses Noto Serif Bengali."""
    if any("\u0980" <= ch <= "\u09ff" for ch in text):
        return "Noto Serif Bengali"
    return "CMU Serif"


@dataclass
class Style:
    color: str = "#F4E8C8"
    opacity: float = 1.0
    stroke_width: float = 0.0
    stroke_color: str = "#FFFFFF"
    stroke_opacity: float = 1.0


@dataclass
class AxisStyle:
    visible: bool = False
    color: str = "#E7C98A"
    opacity: float = 0.9
    stroke_width: float = 2.0
    length_scale: float = 2.6


@dataclass
class TrailStyle:
    """A path that dries out, like water dropped on a road."""

    enabled: bool = False
    dry_time: float = 3.5
    color: str = "#9EBEFF"
    width: float = 2.2
    min_opacity: float = 0.0


@dataclass
class BodySpec:
    name: str
    kind: str
    radius: float
    true_radius_km: float
    mass_kg: float
    color: str
    texture: str | None = None
    night_texture: str | None = None
    orbit_radius: float = 0.0
    true_orbit_au: float = 0.0
    period_days: float = 365.25
    eccentricity: float = 0.0
    inclination_deg: float = 0.0
    tilt_deg: float = 0.0
    spin_hours: float = 24.0
    phase: float = 0.0
    parent: str | None = None
    has_rings: bool = False
    ring_inner: float = 1.28
    ring_outer: float = 2.28
    ring_color: str = "#D9C7A2"
    style: Style = field(default_factory=Style)
    axis: AxisStyle = field(default_factory=AxisStyle)
    trail: TrailStyle = field(default_factory=TrailStyle)
    spin_paused: bool = False
    orbit_paused: bool = False
    frozen_years: float = 0.0
    spin_angle: float = 0.0


@dataclass
class Clock:
    """Scene seconds mapped onto years. Pause stops the whole sky."""

    seconds_per_year: float = 12.0
    rate: float = 1.0
    paused: bool = False
    t: float = 0.0

    def advance(self, dt: float) -> None:
        if not self.paused:
            self.t += dt * self.rate

    @property
    def years(self) -> float:
        if self.seconds_per_year <= 0:
            return 0.0
        return self.t / self.seconds_per_year


@dataclass
class CameraSpec:
    mode: str = "wide"  # wide, top, follow, zoom, from_body
    target: str = "Sun"
    viewpoint: str | None = None
    height: float = 20.0
    phi: float = 62.0
    theta: float = -28.0
    theta_speed: float = 6.0
    label: str | None = None
    label_corner: str = "UL"


def position_at(spec: BodySpec, years: float, parent: np.ndarray | None = None) -> np.ndarray:
    """Kepler-ish place on the orbit. Visual radii, not true AU."""
    if spec.kind == "star" or spec.orbit_radius <= 0:
        return np.zeros(3) if parent is None else np.array(parent, dtype=float)
    used = spec.frozen_years if spec.orbit_paused else years
    period = max(spec.period_days / 365.25, 1e-4)
    theta = spec.phase + TAU * used / period
    ecc = float(np.clip(spec.eccentricity, 0.0, 0.8))
    radius = spec.orbit_radius * (1 - ecc * ecc) / (1 + ecc * np.cos(theta))
    local = np.array([radius * np.cos(theta), radius * np.sin(theta), 0.0])
    inc = spec.inclination_deg * DEG
    y, z = local[1], local[2]
    local[1] = y * np.cos(inc) - z * np.sin(inc)
    local[2] = y * np.sin(inc) + z * np.cos(inc)
    if parent is None:
        return local
    return np.array(parent, dtype=float) + local


def pole_of(spec: BodySpec) -> np.ndarray:
    tilt = spec.tilt_deg * DEG
    return np.array([0.0, np.sin(tilt), np.cos(tilt)])


def _body(**kwargs) -> BodySpec:
    color = kwargs.get("color", "#F4E8C8")
    spec = BodySpec(**kwargs)
    spec.style = Style(color=color)
    spec.axis = AxisStyle()
    spec.trail = TrailStyle(color=color)
    return spec


def solar_catalog() -> dict[str, BodySpec]:
    """Real periods and tilts. Radii are compressed so a frame can hold them."""
    sun = _body(
        name="Sun", kind="star", radius=0.66, true_radius_km=696_340,
        mass_kg=1.9885e30, color="#FFB347", texture="2k_sun.jpg",
        spin_hours=609.12, period_days=0,
    )
    rows = [
        _body(name="Mercury", kind="planet", radius=0.09, true_radius_km=2439.7,
              mass_kg=3.301e23, color="#C4B8A8", texture="2k_mercury.jpg",
              orbit_radius=1.72, true_orbit_au=0.387, period_days=87.97,
              eccentricity=0.2056, inclination_deg=7.0, tilt_deg=0.03,
              spin_hours=1407.6, phase=0.4),
        _body(name="Venus", kind="planet", radius=0.145, true_radius_km=6051.8,
              mass_kg=4.867e24, color="#E6C07B", texture="2k_venus_atmosphere.jpg",
              orbit_radius=2.28, true_orbit_au=0.723, period_days=224.7,
              eccentricity=0.0068, inclination_deg=3.39, tilt_deg=177.4,
              spin_hours=-5832.5, phase=1.7),
        _body(name="Earth", kind="planet", radius=0.155, true_radius_km=6371.0,
              mass_kg=5.972e24, color="#4C8DFF", texture="2k_earth_daymap.jpg",
              night_texture="2k_earth_nightmap.jpg", orbit_radius=3.0,
              true_orbit_au=1.0, period_days=365.25, eccentricity=0.0167,
              inclination_deg=0.0, tilt_deg=23.44, spin_hours=23.93, phase=0.35),
        _body(name="Moon", kind="moon", radius=0.055, true_radius_km=1737.4,
              mass_kg=7.342e22, color="#D0D0D0", texture="2k_moon.jpg",
              orbit_radius=0.48, true_orbit_au=0.00257, period_days=27.32,
              eccentricity=0.0549, inclination_deg=5.14, tilt_deg=6.68,
              spin_hours=655.7, phase=0.8, parent="Earth"),
        _body(name="Mars", kind="planet", radius=0.115, true_radius_km=3389.5,
              mass_kg=6.417e23, color="#C1440E", texture="2k_mars.jpg",
              orbit_radius=3.82, true_orbit_au=1.524, period_days=686.98,
              eccentricity=0.0934, inclination_deg=1.85, tilt_deg=25.19,
              spin_hours=24.62, phase=2.4),
        _body(name="Jupiter", kind="planet", radius=0.44, true_radius_km=69911,
              mass_kg=1.898e27, color="#D9C2A0", texture="2k_jupiter.jpg",
              orbit_radius=5.45, true_orbit_au=5.204, period_days=4332.6,
              eccentricity=0.0489, inclination_deg=1.3, tilt_deg=3.13,
              spin_hours=9.93, phase=1.05),
        _body(name="Saturn", kind="planet", radius=0.37, true_radius_km=58232,
              mass_kg=5.683e26, color="#E6D3A3", texture="2k_saturn.jpg",
              orbit_radius=6.85, true_orbit_au=9.583, period_days=10759,
              eccentricity=0.0565, inclination_deg=2.49, tilt_deg=26.73,
              spin_hours=10.7, phase=3.7, has_rings=True),
        _body(name="Uranus", kind="planet", radius=0.23, true_radius_km=25362,
              mass_kg=8.681e25, color="#C5E8E8", texture="2k_uranus.jpg",
              orbit_radius=8.25, true_orbit_au=19.19, period_days=30687,
              eccentricity=0.0472, inclination_deg=0.77, tilt_deg=97.77,
              spin_hours=-17.24, phase=1.3),
        _body(name="Neptune", kind="planet", radius=0.22, true_radius_km=24622,
              mass_kg=1.024e26, color="#3D6BFF", texture="2k_neptune.jpg",
              orbit_radius=9.55, true_orbit_au=30.07, period_days=60190,
              eccentricity=0.0086, inclination_deg=1.77, tilt_deg=28.32,
              spin_hours=16.11, phase=4.6),
    ]
    catalog = {sun.name: sun}
    catalog.update({row.name: row for row in rows})
    return catalog


def copy_spec(spec: BodySpec) -> BodySpec:
    return replace(
        spec,
        style=replace(spec.style),
        axis=replace(spec.axis),
        trail=replace(spec.trail),
    )
