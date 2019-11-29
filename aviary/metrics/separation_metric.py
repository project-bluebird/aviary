"""
Basic aircraft separation metric. Specification is:

Denote:
- d_h := absolute horizontal distance between two aircraft measured in nautical miles (nm)
- d_v := absolute vertical separation between two aircraft measured in feet (ft)

A general class of metrics takes the form:
- m(d_h, d_v) = max{ m_h(d_h), m_v(d_v) }

Where m_h and m_v are functions depending on horizontal & vertical distance, respectively.

For the simplest metric, define v(d, c, C), a function of distance d and parameters c < C, by:
- v(d) = 0, if d >= C
- v(d) = -1, if d < c
- v(d) = (d - c)/(C - c) -1, otherwise.

The simplest aircraft separation metric is then defined by:
- m(d_h, d_v) = max{ v(d_h, c_h, C_h), v(d_v, c_v, C_V) }

where:
- The c_h (horizontal) and c_v (vertical) thresholds are part of the definition
of "loss of separation", i.e. they're given constants: c_h = 5 nm, c_v = 1000 ft.
- the C_h and C_v thresholds are arbitrary parameters (except for the requirement
that C_h > c_h and C_v > c_v), so the function takes them as arguments.
Default values are double the corresponding lower thresholds.

An alternative metric (in the same class) would define m_h and m_v as smooth
functions, each with a negative asymptote at zero, so the reward tends
to minus infinity as the separation decreases to zero.
"""

import aviary.metrics.utils as utils

vert_min_dist = 1000  # Vertical separation (ft)
hor_min_dist = 5  # Horizontal separation (nm)
vert_warn_dist = 2 * vert_min_dist
hor_warn_dist = 2 * hor_min_dist


def score(d, c, C):
    assert c < C, f"Expected {c} < {C}"
    if d < c:
        return -1
    if d >= C:
        return 0
    return (d - c) / (C - c) - 1


def vertical_separation(alt1, alt2):
    """
    Basic vertical separation metric
    :param alt1:
    :param alt2:
    :return:
    """

    vertical_distance_ft = utils.vertical_distance_ft(alt1, alt2)
    return score(vertical_distance_ft, vert_min_dist, vert_warn_dist)


def horizontal_separation(lon1, lat1, lon2, lat2):
    """
    Basic horizontal separation metric
    :param acid1:
    :param acid2:
    :return:
    """

    horizontal_distance_nm = utils.horizontal_distance_nm(lon1, lat1, lon2, lat2)
    return score(horizontal_distance_nm, hor_min_dist, hor_warn_dist)


def pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2):
    """
    Combined score based on horizontal and vertical separation.
    :param acid1:
    :param acid2:
    :return:
    """

    horizontal_sep = horizontal_separation(lon1, lat1, lon2, lat2)
    vertical_sep = vertical_separation(alt1, alt2)

    return round(max(horizontal_sep, vertical_sep), 2)
