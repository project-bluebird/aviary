"""
Basic aircraft separation metric. Specification is:

Let's denote:
- d_h := absolute horizontal distance betweenthe two aircraft measured in nautical miles (nm)
- d_v := absolute vertical separation between two aircraft measured in feet (ft)

A general class of metrics takes the form:
- m(d_h, d_v) = max{ m_h(d_h), m_v(d_v) }

Where m_h and m_v are functions depending on horizontal & vertical (absolute)
distance, respectively.

The simplest metric m is the function of d_h and d_v defined by:
- m(d_h, d_v) = 0, if d_h >= C_h (for any d_v)
- m(d_h, d_v) = 0, if d_v >= C_v (for any d_h)
- m(d_h, d_v) = -1, if d_h < c_h and d_v < c_v (loss of separation)
- (d_h, d_v) = max{ (d_h - c_h)/(C_h - c_h) - 1, (d_v - c_v)/(C_v - c_v) - 1 }, otherwise

where:
- The c_h (horizontal) and c_v (vertical) thresholds are part of the definition
of "loss of separation", i.e. they're given constants: c_h = 5 nm, c_v = 1000 ft.
- the C_h and C_v thresholds are arbitrary parameters (except for the requirement
that C_h > c_h and C_v > c_v), so the function should take them as arguments.
Default values could be double the corresponding lower thresholds.

Later we might want an alternative metric (in the same class) where m_h and m_v
are smooth functions, each with a negative asymptote at zero, so the reward tends
to minus infinity as the separation decreases to zero.
"""

from aviary.metrics.distance_metric import DistanceMetric


class AircraftSeparation(DistanceMetric):

    def __init__(self, vert_warn_dist=None, hor_warn_dist=None):

        self.vert_min_dist = 1000 # Vertical separation (ft)
        self.hor_min_dist = 5 # Horizontal separation (nm)

        if vert_warn_dist is None:
            vert_warn_dist = 2 * self.vert_min_dist
        self.vert_warn_dist = vert_warn_dist

        if hor_warn_dist is None:
            hor_warn_dist = 2 * self.hor_min_dist
        self.hor_warn_dist = hor_warn_dist

    @staticmethod
    def v(d, c, C):
        assert c < C, f'Expected {c} < {C}'
        if d < c:
        	return -1
        if d > C:
        	return 0
        return (d-c)/(C-c) - 1

    def vertical_score(self, alt1, alt2):
        """
        Basic vertical separation metric
        :param alt1:
        :param alt2:
        :return:
        """

        vertical_distance_ft = self.vertical_distance_ft(alt1, alt2)

        return AircraftSeparation.v(vertical_distance_ft, self.vert_min_dist, self.vert_warn_dist)

    def horizontal_score(self, lon1, lat1, lon2, lat2):
        """
        Basic horizontal separation metric
        :param acid1:
        :param acid2:
        :return:
        """

        horizontal_distance_nm = self.horizontal_distance_nm(lon1, lat1, lon2, lat2)

        return AircraftSeparation.v(horizontal_distance_nm, self.hor_min_dist, self.hor_warn_dist)

    def score(self, lon1, lat1, alt1, lon2, lat2, alt2):
        """
        Combined score based on horizontal and vertical separation.
        :param acid1:
        :param acid2:
        :return:
        """

        horizontal_sep = self.horizontal_score(lon1, lat1, lon2, lat2)
        vertical_sep = self.vertical_score(alt1, alt2)

        return max(horizontal_sep, vertical_sep)
