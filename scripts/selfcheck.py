"""No render. Checks that orbits, fonts and the catalog are sane."""

import numpy as np

from universe.model import font_for, position_at, solar_catalog


def main() -> None:
    catalog = solar_catalog()
    assert set(catalog) >= {"Sun", "Earth", "Moon", "Saturn", "Uranus"}
    earth = catalog["Earth"]
    start = position_at(earth, 0.0)
    later = position_at(earth, 0.5)
    assert np.linalg.norm(start - later) > 0.2
    moon = catalog["Moon"]
    assert moon.parent == "Earth"
    assert font_for("পৃথিবী") == "Noto Serif Bengali"
    assert font_for("Earth") == "CMU Serif"
    assert catalog["Uranus"].tilt_deg > 90
    print("selfcheck ok")
    print("Earth t=0", np.round(start, 3))
    print("bodies", len(catalog))


if __name__ == "__main__":
    main()
