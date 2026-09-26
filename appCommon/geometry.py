"""Helpers for Shapely 2 multipart geometries and FlatCAM geometry lists."""
from shapely.geometry.base import BaseMultipartGeometry


def geometry_parts(value):
    """Expose multipart components while preserving lists and atomic geometries.

    Atomic polygons/lines intentionally stay non-iterable, so existing recursive
    geometry code can distinguish them from containers.
    """
    return value.geoms if isinstance(value, BaseMultipartGeometry) else value
