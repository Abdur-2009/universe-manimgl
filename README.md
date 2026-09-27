# universe-manimgl

সৌরজগৎ দিয়ে শুরু করা একটি 3D ইউনিভার্স টুলকিটের প্রথম ধাপ। ManimGL দিয়ে আঁকা। একই নামের ManimCE যমজ আলাদা রিপোতে।

This is step 1, not the full 10–15k line library. The architecture is in `ARCHITECTURE.md`.

## Use a template

```python
from universe.scene import UniverseScene
from universe.templates import EarthOrbit, MoonViewpoint, SolarWide

class Film(UniverseScene):
    def construct(self):
        (
            SolarWide(seconds=6, label="সৌরজগৎ")
            .then(EarthOrbit(seconds=6, label="পৃথিবী"))
            .then(MoonViewpoint(seconds=5))
            .play(self)
        )
```

## Or drive it yourself

```python
universe = self.ensure_universe()
earth = universe.ensure("Earth")
earth.show_axis(color="#E7C98A", opacity=0.9, stroke_width=3)
earth.trail(dry_time=2.5)
earth.pause_spin()
universe.camera.follow("Earth", height=5)
universe.camera.set_label("পৃথিবী")
self.hold(4)
```

## Low-quality test

30 fps, 854×480. Not HD.

```bash
manimgl examples/01_earth_orbit.py EarthOrbitDemo -w -r 854x480 --fps 30 -c "#000000" --video_dir videos
```

## Fonts

Latin text uses `CMU Serif`. Bangla uses `Noto Serif Bengali`. Both must be installed on the machine that renders.

## Textures

Planet maps under `universe/assets/textures/` are from Solar System Scope. Credit them if a film is published. They are not original art.

## Layout

`model.py`, `handles.py`, `templates.py`, and `importing.py` are shared with `universe-manimce` and must stay identical. Drawing lives only in `engine.py`.
