"""
Abstract base class representing a distance based metric between two (lon, lat, alt) positions.
"""

from pyproj import Geod

_WGS84 = Geod(ellps="WGS84")

_SCALE_METRES_TO_FEET = 3.280839895

_ONE_NM = 1852  # Meters


def horizontal_distance_m(lon1, lat1, lon2, lat2):
    """Horizontal distance (metres) between two (lon/lat) points"""

    _, _, horizontal_m = _WGS84.inv(lon1, lat1, lon2, lat2)
    return horizontal_m


def horizontal_distance_nm(lon1, lat1, lon2, lat2):
    """Horizontal distance (nautical miles) between two (lon/lat) points"""

    horizontal_m =horizontal_distance_m(lon1, lat1, lon2, lat2)
    return round(horizontal_m / _ONE_NM)


def vertical_distance_m(alt1, alt2):
    """Vertical distance (metres) between two altitudes (in metres)"""

    return abs(alt1 - alt2)


def vertical_distance_ft(alt1, alt2):
    """Vertical distance (feet) between two altitudes (in metres)"""

    return vertical_distance_m(alt1, alt2) * _SCALE_METRES_TO_FEET
