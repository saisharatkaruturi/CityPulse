"""Small geographic helpers (no spatial engine required)."""

from __future__ import annotations

import math

EARTH_RADIUS_M = 6_371_000


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def bounding_box(lat: float, lng: float, radius_m: float) -> tuple[float, float, float, float]:
    """Return (min_lat, max_lat, min_lng, max_lng) enclosing a circle; used as an indexed pre-filter."""
    dlat = math.degrees(radius_m / EARTH_RADIUS_M)
    dlng = math.degrees(radius_m / (EARTH_RADIUS_M * max(math.cos(math.radians(lat)), 1e-6)))
    return lat - dlat, lat + dlat, lng - dlng, lng + dlng


def point_in_polygon(lat: float, lng: float, polygon: list[list[float]]) -> bool:
    """Ray casting; polygon is [[lat, lng], ...]."""
    inside = False
    n = len(polygon)
    if n < 3:
        return False
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i]
        yj, xj = polygon[j]
        if (xi > lng) != (xj > lng):
            y_cross = (yj - yi) * (lng - xi) / (xj - xi) + yi
            if lat < y_cross:
                inside = not inside
        j = i
    return inside


def fuzz(value: float, decimals: int) -> float:
    return round(value, decimals)
