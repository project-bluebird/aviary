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

# import aviary.sector.route as rt
import aviary.geo.geo_helper as gh
import aviary.metrics.utils as utils
import aviary.sector.sector_element as se

# TODO: set thresholds
vert_min_dist = 1000  # Vertical separation (ft)
hor_min_dist = 5  # Horizontal separation (nm)
vert_warn_dist = 2 * vert_min_dist
hor_warn_dist = 2 * hor_min_dist


def target(route):
    """Return second to last waypoint on route as the target exit location"""
    route_coordinates = [
        wpt[se.GEOMETRY_KEY][gh.COORDINATES_KEY] for wpt in route
    ]
    return route_coordinates[-2]


def exit_position(
    current_lat, current_lon, current_alt, previous_lat, previous_lon, previous_alt
):
    # TODO - return better estimate of the exit position as midpoint between the two locations
    return (current_lat+previous_lat)/2, (current_lon+previous_lon)/2, (current_alt + previous_alt)/2


def score(d, c, C):
    assert c < C, f"Expected {c} < {C}"
    if d <= c:
        return 0
    if d > C:
        return -1
    return -(d - c) / (C - c)


def sector_exit(actual_lon, actual_lat, actual_alt, target_lon, target_lat, target_alt):
    """Implements setor exit score"""
    horizontal_sep_m = utils.horizontal_separation_m(
        target_lon, target_lat, actual_lon, actual_lat
    )
    m_h = score(horizontal_sep_m, hor_min_dist, hor_warn_dist)

    vertical_sep_m = utils.vertical_separation_m(actual_alt, target_alt)
    m_v = score(vertical_sep_m, vert_min_dist, vert_warn_dist)

    return min(m_h, m_v)


def sector_exit_metric(
    current_lat,
    current_lon,
    current_alt,
    previous_lat,
    previous_lon,
    previous_alt,
    requested_flight_level,
    sector,
    route,
):
    """
	Metric score based on the aircraft's exit point from the sector
	"""
    # check if aircraft just exited sector
    if not sector.contains(current_lat, current_lon, current_alt) and sector.contains(
        previous_lat, previous_lon, previous_alt
    ):

        actual_lon, actual_lat, actual_alt = exit_position(
            current_lat,
            current_lon,
            current_alt,
            previous_lat,
            previous_lon,
            previous_alt,
        )

        target_lon, target_lat = target(route)
        target_alt = requested_flight_level

        return sector_exit(
            actual_lon, actual_lat, actual_alt, target_lon, target_lat, target_alt
        )
    return 0
