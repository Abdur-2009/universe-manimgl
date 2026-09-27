"""File loading that does not depend on Manim.

Both engine repos keep this file identical. Drawing the loaded data
is the engine's job, in assets.py.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
VECTOR_SUFFIXES = {".svg"}
MESH_SUFFIXES = {".obj"}


def kind_of(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        return "image"
    if suffix in VECTOR_SUFFIXES:
        return "vector"
    if suffix in MESH_SUFFIXES:
        return "mesh"
    raise ValueError(f"No loader yet for {suffix}. Use png, jpg, svg or obj.")


def read_obj(path: str | Path, face_cap: int = 800) -> tuple[np.ndarray, list[tuple[int, int, int]]]:
    """Vertices and triangulated faces. A teaching mesh, not a full importer."""
    vertices: list[list[float]] = []
    faces: list[tuple[int, int, int]] = []
    for raw in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("v "):
            parts = line.split()
            if len(parts) < 4:
                continue
            vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
        elif line.startswith("f "):
            ids: list[int] = []
            for token in line.split()[1:]:
                ids.append(int(token.split("/")[0]) - 1)
            if len(ids) < 3:
                continue
            for index in range(1, len(ids) - 1):
                faces.append((ids[0], ids[index], ids[index + 1]))
                if len(faces) >= face_cap:
                    return np.array(vertices, dtype=float), faces
    if not vertices:
        raise ValueError(f"No vertices in {path}")
    return np.array(vertices, dtype=float), faces
