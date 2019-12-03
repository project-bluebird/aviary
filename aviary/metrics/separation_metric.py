"""
Basic aircraft separation metric. Specification is:

- d_h := Geodesic distance between two aircraft measured in nautical miles (nm)
- d_v := absolute vertical separation between two aircraft measured in feet (ft)

A general class of metrics takes the form:

- m(d_h, d_v) = max{ m_h(d_h), m_v(d_v) }

Where m_h and m_v are functions depending on horizontal & vertical distance, respectively.
"""

import aviary.metrics.utils as utils

vert_min_dist = 1000  # Vertical separation (ft)
hor_min_dist = 5  # Horizontal separation (nm)
vert_warn_dist = 2 * vert_min_dist
hor_warn_dist = 2 * hor_min_dist


def score(d, c, C):
    """
    - score(d) = 0, if d >= C
    - score(d) = -1, if d < c
    - score(d) = (d - c)/(C - c) -1, otherwise.
    """

    assert d >= 0, f"Incorrent value {d} for distance"
    assert c < C, f"Expected {c} < {C}"
    if d < c:
        return -1
    if d >= C:
        return 0
    return (d - c) / (C - c) - 1


def vertical_separation_score(alt1, alt2):
    """
    Basic vertical separation metric.

    :param alt1: Aircraft 1 altitude in metres.
    :param alt2: Aircraft 2 altitude in metres.
    :return: Score based on vertical distance between aircraft.
    """

    vert_dist_ft = abs(alt1 - alt2) * utils._SCALE_METRES_TO_FEET
    return score(vert_dist_ft, vert_min_dist, vert_warn_dist)


def horizontal_separation_score(lon1, lat1, lon2, lat2):
    """
    Basic horizontal separation metric.

    :param lon1: Aircraft 1 longitude.
    :param lat1: Aircraft 1 latitude.
    :param lon2: Aircraft 2 longitude.
    :param lat2: Aircraft 2 latitude.
    :return: Score based on horizontal distance between aircraft.
    """

    hor_dist_nm = utils.horizontal_distance_nm(lon1, lat1, lon2, lat2)
    return score(hor_dist_nm, hor_min_dist, hor_warn_dist)


def pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2):
    """
    Aircraft separation metric.

    :param lon1: Aircraft 1 longitude.
    :param lat1: Aircraft 1 latitude.
    :param alt1: Aircraft 1 altitude (in metres).
    :param lon2: Aircraft 2 longitude.
    :param lat2: Aircraft 2 latitude.
    :param alt2: Aircraft 2 altitude (in metres).
    :return: Combined score based on horizontal and vertical separation between aircraft.
    """

    hor_sep = horizontal_separation_score(lon1, lat1, lon2, lat2)
    vert_sep = vertical_separation_score(alt1, alt2)

    return max(hor_sep, vert_sep)
