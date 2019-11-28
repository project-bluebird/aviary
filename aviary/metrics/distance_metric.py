"""
Abstract base class representing a distance based metric.
"""

from pyproj import Geod
from abc import ABC, abstractmethod

_WGS84 = Geod(ellps='WGS84')

_SCALE_METRES_TO_FEET = 3.280839895

_ONE_NM = 1852  # Meters


class DistanceMetric(ABC):

    @abstractmethod
    def score():
        pass

    @staticmethod
    def horizontal_distance_m(lon1, lat1, lon2, lat2):
        """Horizontal distance between two (lon/lat) points in metres"""

        _, _, horizontal_m = _WGS84.inv(lon1, lat1, lon2, lat2)
        return horizontal_m

    @staticmethod
    def horizontal_distance_nm(lon1, lat1, lon2, lat2):
        """Horizontal distance between two (lon/lat) points in nautical miles"""

        horizontal_m = DistanceMetric.horizontal_distance_m(lon1, lat1, lon2, lat2)
        return round(horizontal_m / _ONE_NM)

    @staticmethod
    def vertical_distance_m(alt1, alt2):
        """Vertical distance between two altitudes in metres"""

        return abs(alt1 - alt2)

    @staticmethod
    def vertical_distance_ft(alt1, alt2):
        """Vertical distance in feet between two altitudes in metres"""

        return DistanceMetric.vertical_distance_m(alt1, alt2) * _SCALE_METRES_TO_FEET
