"""
Abstract base class representing a distance based metric.

denote:
- x = (x_lat, x_lon, x_alt) := location of point x
- y = (y_lat, y_lon, y_alt) := location of point y
- d_h = Geodesic distance between(x_lat, x_lon) and (y_lat, y_lon)
- d_v = | x_alt - y_alt |, the absolute vertical distance between x & y

A general class of metrics takes the form:
- m(d_h, d_v) = max{ m_h(d_h), m_v(d_v) }

Where m_h and m_v are functions depending on horizontal & vertical (absolute) distance, respectively.
"""

from pyproj import Geod
from abc import ABC, abstractmethod

_WGS84 = Geod(ellps='WGS84')

_SCALE_METRES_TO_FEET = 3.280839895

_ONE_NM = 1852  # Meters


class DistanceMetric(ABC):

    @abstractmethod
    def score(self) -> float:
        pass

    def horizontal_distance_m(self, lon1, lat1, lon2, lat2):
        """Horizontal distance between two (lon/lat) points in metres"""

        _, _, horizontal_m = _WGS84.inv(lon1, lat1, lon2, lat2)
        return horizontal_m

    def horizontal_distance_nm(self, lon1, lat1, lon2, lat2):
        """Horizontal distance between two (lon/lat) points in nautical miles"""

        horizontal_m = self.horizontal_distance_m(lon1, lat1, lon2, lat2)
        return round(horizontal_m / _ONE_NM)

    def vertical_distance_m(self, alt1, alt2):
        """Vertical distance between two altitudes in metres"""

        return abs(alt1 - alt2)

    def vertical_distance_ft(self, alt1, alt2):
        """Vertical distance in feet between two altitudes in metres"""

        return self.vertical_distance_m(alt1, alt2) * _SCALE_METRES_TO_FEET
