# Architecture

This is step 1 of a 3D universe toolkit. The later library may reach 10 to 15 thousand lines. That depth is not pretended here. The shape is here so later scenes plug into the same names.

## Three repos

| Repo | What it holds |
| --- | --- |
| `universe-works` | Finished videos, under `year2026/<project>/` |
| `universe-manimgl` | The controller, drawn by ManimGL |
| `universe-manimce` | The same controller, drawn by Manim Community |

The package name in both engine repos is `universe`. Do not install them into the same environment. The calls are the same so a scene can move from one engine to the other by changing the install, not the script.

`universe-works` does not import `universe`. It is the shelf for rendered films and the project files that made them.

## Layers

Shared files, kept identical in both engine repos:

- `universe/model.py` — catalog, Kepler placement, clock, camera spec, font choice. No Manim import.
- `universe/handles.py` — fluent body and camera controls. They write the spec. They do not draw.
- `universe/templates.py` — connected shots. `A.then(B).then(C).play(scene)` runs on one universe.
- `universe/importing.py` — png, jpg, svg, obj classification, and a small obj reader.

Engine files, allowed to differ:

- `universe/engine.py` — reads the spec every frame and draws.
- `universe/scene.py` — `UniverseScene`.
- `universe/assets.py` — `Asset3D`, the 3D cousin of an image loader.

A scene does not talk to Manim cameras directly. It talks to `universe.camera` and `universe.body("Earth")`. The engine is the only file that knows `frame.reorient` or `set_camera_orientation`.

## What a frame does

1. The clock advances unless it is paused.
2. Each body is placed by `position_at`. Orbit pause freezes that body's year. Spin pause skips the rotation.
3. Style, axis, and the drying trail are read from the spec.
4. The camera mode picks a center, a height, and angles. Modes are `wide`, `top`, `follow`, `zoom`, and `from_body`.
5. Labels are fixed in the frame. Bangla uses `Noto Serif Bengali`. Latin uses `CMU Serif`.

## Templates already connected

- `SolarWide` — the catalog, slow camera.
- `EarthOrbit` — Sun, Earth, Moon, follow camera, drying trail, axis.
- `MoonViewpoint` — camera direction from the Moon toward Earth.
- `GravityWell` — cloth with a mass. A teaching dent, not a relativity solver.
- `LightBend` — a ray that bends past a mass. A sketch of the idea.
- `FallingApple` — the apple falls.

They share one clock and one set of bodies. A later template does not rebuild the Sun.

## Controls already on the body

`pause_spin`, `resume_spin`, `pause_orbit`, `resume_orbit`, `set_opacity`, `set_color`, `set_stroke`, `show_axis`, `hide_axis`, `trail`, `clear_trail`.

The trail's `dry_time` is the water-on-the-road fade. Old samples drop out. The path does not stay painted forever.

## ManimCE split

OpenGL is the 3D path: textured spheres, real surfaces, perspective. Cairo is the fallback when `--renderer opengl` is not set. Cairo draws colored spheres, at a coarser mesh, and does not pretend to be a photo planet. Quality tests use OpenGL. A small pole seam on OpenGL spheres is still open; it is not the finished look.

## What is deliberately not here yet

A full solar-system film, starfields, ship flight, a real spacetime solver, a production obj shader, and the thousands of lines of later shots. Those come as later steps, on these same names.

## Test quality

Any test render is 30 fps and 480p. 16:9 at 480p is 854×480. Do not use HD to try an idea.
