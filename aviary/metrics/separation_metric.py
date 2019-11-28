"""
Basic aircraft separation metric. Specification is:

Let's denote:
- d_h := absolute horizontal distance betweenthe two aircraft  measured in nautical miles (nm)
- d_v := absolute vertical separation between two aircraft measured in feet (ft)

The simple metric is the function of d_h and d_v defined by:
- m(d_h, d_v) = 0, if d_h >= C_h (for any d_v)
- m(d_h, d_v) = 0, if d_v >= C_v (for any d_h)
- m(d_h, d_v) = -1, if d_h < c_h and d_v < c_v (loss of separation)
- m(d_h, d_v) = max{ (d_h - c_h)/(C_h - c_h) - 1, (d_v - c_v)/(C_v - c_v) - 1 }, otherwise

where:
- The c_h (horizontal) and c_v (vertical) thresholds are part of the definition of "loss of
separation", i.e. they're given constants: c_h = 5 nm, c_v = 1000 ft
- The C_h and C_v thresholds are arbitrary parameters (except for the requirement that C_h > c_h
and C_v > c_v), so the function should take them as arguments. Default values could be double the
corresponding lower thresholds, that is: C_h = 10 nm, C_v = 2000 ft

Later we might want an alternative metric (in the same class) where m_h and m_v are smooth functions, each with a negative asymptote at zero, so the reward tends to minus infinity as the separation decreases to zero.
"""

import numpy as np

from aviary.metrics.distance_metric import DistanceMetric

LOS_SCORE = -1  # Score below the minimum separation

# Vertical separation (ft)
VERT_MIN_DIST = 1000
VERT_WARN_DIST = 2 * VERT_MIN_DIST

# Horizontal separation (nm)
HOR_MIN_DIST = 5
HOR_WARN_DIST = 2 * HOR_MIN_DIST

class AircraftSeparation(DistanceMetric):

    def __init__(self, los_score=None, vert_min_dist=None, vert_warn_dist=None, hor_min_dist=None, hor_warn_dist=None):

        if los_score is None:
            los_score = LOS_SCORE
        self.los_score = los_score

        if vert_min_dist is None:
            vert_min_dist = VERT_MIN_DIST
        self.vert_min_dist = vert_min_dist

        if vert_warn_dist is None:
            vert_warn_dist = VERT_WARN_DIST
        self.vert_warn_dist = vert_warn_dist

        if hor_min_dist is None:
            hor_min_dist = HOR_MIN_DIST
        self.hor_min_dist = hor_min_dist

        if hor_warn_dist is None:
            hor_warn_dist = HOR_WARN_DIST
        self.hor_warn_dist = hor_warn_dist

    def vertical_score(self, alt1, alt2):
    	"""
    	Basic vertical separation metric
    	:param alt1:
    	:param alt2:
    	:return:
    	"""

    	vertical_distance_ft = self.vertical_distance_ft(alt1, alt2)

    	if vertical_distance_ft < self.vert_min_dist:
    		return self.los_score

    	if vertical_distance_ft < self.vert_warn_dist:
    		# Linear score between the minimum and warning distances
    		return np.interp(vertical_distance_ft,
    		                 [self.vert_min_dist, self.vert_warn_dist], [self.los_score, 0])

    	return 0

    def horizontal_score(self, lon1, lat1, lon2, lat2):
    	"""
    	Basic horizontal separation metric
    	:param acid1:
    	:param acid2:
    	:return:
    	"""

    	horizontal_distance_nm = self.horizontal_distance_nm(lon1, lat1, lon2, lat2)

    	if horizontal_distance_nm < self.hor_min_dist:
    		return round(self.los_score, 1)

    	if horizontal_distance_nm < self.hor_warn_dist:
    		# Linear score between the minimum and warning distances
    		return round(np.interp(horizontal_distance_nm,
    		                       [self.hor_min_dist, self.hor_warn_dist], [self.los_score, 0]), 1)
    	return 0

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
