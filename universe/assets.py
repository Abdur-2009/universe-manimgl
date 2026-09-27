"""Load a file into the universe the way ImageMobject loads a picture.

png, jpg and svg are drawn now. obj uses ManimGL's mesh loader, and falls
back to the shared face reader if that mesh cannot be built.
"""

from __future__ import annotations

from pathlib import Path

from manimlib import Group, ImageMobject, Polygon, Sphere, SVGMobject, TexturedSurface

from universe.importing import kind_of, read_obj


class Asset3D:
    def __init__(self, path: str, scale: float = 1.0):
        self.path = Path(path)
        self.scale = scale
        if not self.path.exists():
            raise FileNotFoundError(self.path)

    def load(self):
        kind = kind_of(self.path)
        if kind == "image":
            mob = ImageMobject(str(self.path))
        elif kind == "vector":
            mob = SVGMobject(str(self.path))
        else:
            mob = self._mesh()
        mob.scale(self.scale)
        return mob

    def _mesh(self):
        try:
            from manimlib.mobject.types.surface import ThreeDModel
            return ThreeDModel(str(self.path))
        except Exception:
            vertices, faces = read_obj(self.path)
            group = Group()
            for a, b, c in faces:
                triangle = Polygon(vertices[a], vertices[b], vertices[c])
                triangle.set_stroke(width=0)
                triangle.set_fill("#D9C7A2", opacity=1)
                group.add(triangle)
            return group


def textured_sphere(image: str, radius: float = 1.0, resolution=(32, 16)):
    """Same idea as ImageMobject, wrapped on a sphere."""
    return TexturedSurface(Sphere(radius=radius, resolution=resolution), image)
