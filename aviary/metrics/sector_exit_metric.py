"""
Basic sector exit metric. Specification is:

- x = (x_lat, x_lon, x_alt) := the target sector exit location.
- y = (y_lat, y_lon, y_alt) := the terminal location of the aircraft within the sector.
- d_h = Geodesic distance between (x_lat, x_lon) and (y_lat, y_lon) in nautical miles (nm)
- d_v = | x_alt - y_alt |, the absolute vertical distance between x & y in feet (ft)

A general class of metrics takes the form:

- m(d_h, d_v) = min{ m_h(d_h), m_v(d_v) }

Where m_h and m_v are functions depending on horizontal & vertical distance, respectively.
"""

import aviary.geo.geo_helper as gh
import aviary.metrics.utils as utils
import aviary.sector.sector_element as se


# TODO: set thresholds and decide if these should be passed as arguments
vert_warn_dist = 1000  # Vertical separation (ft)
hor_warn_dist = 5  # Horizontal separation (nm)
vert_max_dist = 2 * vert_warn_dist
hor_max_dist = 2 * hor_warn_dist


def target(route):
    """
    Return second to last waypoint on route as the target exit location.

    :param route: aircraft route (as defined by aviary.sector.Route)
    """

    route_coordinates = [wpt[se.GEOMETRY_KEY][gh.COORDINATES_KEY] for wpt in route]
    return route_coordinates[-2]


def get_midpoint(current_lon, current_lat, previous_lon, previous_lat):
    """
    Return midpoint between previous and current lon/lat positions.
    """

    # see: https://pyproj4.github.io/pyproj/dev/_modules/pyproj/geod.html#Geod.npts
    lonlats = utils._WGS84.npts(
        current_lon, current_lat, previous_lon, previous_lat, npts=1
    )
    return lonlats[0]


def score(d, c, C):
    """
    - score(d) = 0, if d <= c
    - score(d) = -1, if d > C
    - score(d) = -(d - c)/(C - c), otherwise.
    """

    assert d >= 0, f"Incorrent value {d} for distance"
    assert c < C, f"Expected {c} < {C}"
    if d <= c:
        return 0
    if d > C:
        return -1
    return -(d - c) / (C - c)


def sector_exit_score(
    actual_lon, actual_lat, actual_alt, target_lon, target_lat, target_alt
):
    """
    Implements setor exit score.

    :param actual_lon: Longitude of actual position.
    :param actual_lat: Latitude of actual position.
    :param actual_alt: Altitude (in feet) of actual position.
    :param target_lon: Longitude of target position.
    :param target_lat: Latitude of target position.
    :param target_alt: Altitude (in feet) of target position.
    :return: Combined score based on horizontal and vertical distance between actual and target position.
    """

    horizontal_sep_nm = utils.horizontal_distance_nm(
        target_lon, target_lat, actual_lon, actual_lat
    )
    m_h = score(horizontal_sep_nm, hor_warn_dist, hor_max_dist)

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
	Sector exit metric.

    :param current_lon: Longitude of current position.
    :param current_lat: Latitude of current position.
    :param current_alt: Altitude (in metres) of current position.
    :param previous_lon: Longitude of previous position.
    :param previous_lat: Latitude of previous position.
    :param previous_alt: Altitude (in metres) of previous position.
    :param requested_flight_level: Requested flight level at sector exit.
    :param sector: Shapely Polygon object defining the sector.
    :param route: Aircraft route (as returned by aviary.sector.Route).
    :return: Score based on distance between target and estimated actual position of aircraft at exit from the sector. None if aircraft has not exited sector between current and previous position.
	"""

    current_alt_ft = current_alt * utils._SCALE_METRES_TO_FEET
    previous_alt_ft = previous_alt * utils._SCALE_METRES_TO_FEET

    # check if aircraft just exited sector
    # NOTE: sector stores altitude in flight levels
    if not sector.contains(
        current_lon, current_lat, current_alt_ft / 100
    ) and sector.contains(previous_lon, previous_lat, previous_alt_ft / 100):

        # estimate actual sector exit position as midpoint between previous and current position
        actual_lon, actual_lat = get_midpoint(
            current_lon, current_lat, previous_lon, previous_lat
        )
        actual_alt_ft = (current_alt_ft + previous_alt_ft) / 2

        target_lon, target_lat = target(route)
        target_alt_ft = requested_flight_level * 100  # convert FL to feet

        return sector_exit_score(
            actual_lon, actual_lat, actual_alt_ft, target_lon, target_lat, target_alt_ft
        )
    return None
