"""
Basic sector exit metric. Specification is:

Denote:
- x = (x_lat, x_lon, x_alt) := the target sector exit location.
- y = (y_lat, y_lon, y_alt) := the terminal location of the aircraft within the sector.
- d_h = Geodesic distance between (x_lat, x_lon) and (y_lat, y_lon)
- d_v = | x_alt - y_alt |, the absolute vertical distance between x & y

A general class of metrics takes the form:
- m(d_h, d_v) = min{ m_h(d_h), m_v(d_v) }

Where m_h and m_v are functions depending on horizontal & vertical distance, respectively.

For the simplest metric, define v(d, c, C), a function of distance d and parameters c < C, by:
- v(d) = 0, if d <= c
- v(d) = -1, if d > C
- v(d) = -(d - c)/(C - c), otherwise.

Define the sector exit metric m by:
- m(d_h, d_v) = min{ v(d_h, c_h, C_h), v(d_v, c_v, C_v) }

The thresholds c_h, C_h, c_v, C_v are arbitrary parameters passed as arguments.
"""

import aviary.geo.geo_helper as gh
import aviary.metrics.utils as utils
import aviary.sector.sector_element as se

# TODO: set thresholds (+ units) and decide if these should be passed as arguments
vert_warn_dist = 1000  # Vertical separation (ft)
hor_warn_dist = 5  # Horizontal separation (nm)
vert_max_dist = 2 * vert_warn_dist
hor_max_dist = 2 * hor_warn_dist


def target(route):
    """Return second to last waypoint on route - this is the target exit location."""
    route_coordinates = [
        wpt[se.GEOMETRY_KEY][gh.COORDINATES_KEY] for wpt in route
    ]
    return route_coordinates[-2]


def get_midpoint(
    current_lon, current_lat, current_alt, previous_lon, previous_lat, previous_alt
):
    """Return midpoint between previous and current lon/lat/alt positions."""
    # TODO - return better estimate of the exit position as midpoint between the two locations
    return (current_lon+previous_lon)/2, (current_lat+previous_lat)/2, (current_alt + previous_alt)/2


def score(d, c, C):
    assert d >= 0, f"Incorrent value {d} for distance"
    assert c < C, f"Expected {c} < {C}"
    if d <= c:
        return 0
    if d > C:
        return -1
    return -(d - c) / (C - c)


def sector_exit_score(actual_lon, actual_lat, actual_alt, target_lon, target_lat, target_alt):
    """
    Implements setor exit score.

    :param actual_alt: actual altitude in feet
    :param target_alt: target altitude in feet
    """
    horizontal_sep_m = utils.horizontal_distance_nm(
        target_lon, target_lat, actual_lon, actual_lat
    )
    m_h = score(horizontal_sep_m, hor_warn_dist, hor_max_dist)

    vertical_sep_ft = abs(actual_alt - target_alt)
    m_v = score(vertical_sep_ft, vert_warn_dist, vert_max_dist)

    return min(m_h, m_v)


def sector_exit_metric(
    current_lon,
    current_lat,
    current_alt,
    previous_lon,
    previous_lat,
    previous_alt,
    requested_flight_level,
    sector,
    route,
):
    """
	Return metric score based on the aircraft's estimated exit point from the sector. Returns None if aircraft has not just exited sector.

    :param current_alt: Current altitude in metres
    :param previous_alt: Previous altitude in metres
	"""
    current_alt_ft = current_alt * utils._SCALE_METRES_TO_FEET
    previous_alt_ft = previous_alt * utils._SCALE_METRES_TO_FEET

    # check if aircraft just exited sector
    # sector expresses altitude in flight levels
    if not sector.contains(current_lon, current_lat, current_alt_ft/100) and sector.contains(
        previous_lon, previous_lat, previous_alt_ft/100
    ):
        # estimate actual exit location as midpoint between previous and current position
        actual_lon, actual_lat, actual_alt_ft = get_midpoint(
            current_lon,
            current_lat,
            current_alt_ft,
            previous_lon,
            previous_lat,
            previous_alt_ft,
        )

        target_lon, target_lat = target(route)
        target_alt_ft = requested_flight_level * 100 # convert FL to feet
        print(actual_lon, actual_lat)
        print(target_lon, target_lat)
        return sector_exit_score(
            actual_lon, actual_lat, actual_alt_ft,
            target_lon, target_lat, target_alt_ft
        )
    return None
