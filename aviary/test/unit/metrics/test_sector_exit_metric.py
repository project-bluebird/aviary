
import pytest

from aviary.metrics.sector_exit_metric import sector_exit_metric, score, get_midpoint, sector_exit_score, target

import aviary.metrics.utils as utils

_SCALE_FEET_TO_METRES = 1/utils._SCALE_METRES_TO_FEET

route =  [
    {"fixName": "FIYRE", "geometry": {"type": "Point", "coordinates": [-0.1275, 50.91735552314281]}}, {"fixName": "EARTH", "geometry": {"type": "Point", "coordinates": [-0.1275, 51.08383154960228]}}, {"fixName": "WATER", "geometry": {"type": "Point", "coordinates": [-0.1275, 51.49999999999135]}}, {"fixName": "AIR", "geometry": {"type": "Point", "coordinates": [-0.1275, 51.916128869951486]}}, {"fixName": "SPIRT", "geometry": {"type": "Point", "coordinates": [-0.1275, 52.08256690115545]}}
    ]


def test_target():

    result = target(route)
    assert result == [-0.1275, 51.916128869951486]


def test_get_midpoint():

    result = get_midpoint(0, 0, 0, 0)
    assert result == (0, 0)

    result = get_midpoint(0, 0, 0.2, 0.2)
    assert result == pytest.approx((0.1, 0.1), 0.01)


def test_score():

    result = score(0, 0, 1)
    assert result == 0

    result = score(5, 5, 10)
    assert result == 0

    result = score(7.5, 5, 10)
    assert result == -0.5

    result = score(10, 5, 10)
    assert result == -1

    result = score(15, 5, 10)
    assert result == -1


def test_sector_exit_score():

    lon1, lat1, alt1 = (0, 0, 0)
    lon2, lat2, alt2 = (0, 0, 0)

    assert sector_exit_score(lon1, lat1, alt1, lon2, lat2, alt2) == 0

    lon2, lat2, alt2 = (-.05, 0, 0)

    assert sector_exit_score(lon1, lat1, alt1, lon2, lat2, alt2) == 0

    lon2, lat2, alt2 = (0, -.1, 0)

    # the distance is ~11057.43 metres which is ~5.970 nautical miles
    assert sector_exit_score(lon1, lat1, alt1, lon2, lat2, alt2) == pytest.approx(-0.2)

    lon2, lat2, alt2 = (0.15, 0, 0)

    # the distance is ~66758.31 metres which is ~8.956 nautical miles
    assert sector_exit_score(lon1, lat1, alt1, lon2, lat2, alt2) == pytest.approx(-0.8)

    lon2, lat2, alt2 = (0, 0.2, 0)

    assert sector_exit_score(lon1, lat1, alt1, lon2, lat2, alt2) == -1

    lon2, lat2, alt2 = (0, 0, 1000)

    assert sector_exit_score(lon1, lat1, alt1, lon2, lat2, alt2) == 0

    lon2, lat2, alt2 = (0, 0, 1230)

    assert sector_exit_score(lon1, lat1, alt1, lon2, lat2, alt2) == -0.23

    lon2, lat2, alt2 = (0, 0, 1500)

    assert sector_exit_score(lon1, lat1, alt1, lon2, lat2, alt2) == -0.5

    lon2, lat2, alt2 = (0, 0, 2000)

    assert sector_exit_score(lon1, lat1, alt1, lon2, lat2, alt2) == -1


def test_sector_exit_metric(i_element):

    target_lon = -0.1275
    target_lat = 51.916

    requested_FL = 350
    requested_FL_m = requested_FL * 100 * _SCALE_FEET_TO_METRES

    # aircraft has not exited sector -- use approx coordinates of 2nd and 3rd waypoint
    result = sector_exit_metric(
        target_lon , 51.5, requested_FL_m,
        target_lon , 51.1, requested_FL_m,
        requested_FL,
        i_element,
        route
    )
    assert result is None

    # aircraft exited sector, the exit was at target waypoint & correct altitude
    result = sector_exit_metric(
        target_lon , target_lat + 0.4, requested_FL_m,
        target_lon , target_lat - 0.4, requested_FL_m,
        requested_FL,
        i_element,
        route
    )
    assert result == 0

    # aircraft exited sector, the exit was at target waypoint but wrong altitude
    wrong_alt_m = requested_FL_m - 2000 * _SCALE_FEET_TO_METRES
    result = sector_exit_metric(
        target_lon , target_lat + 0.4, wrong_alt_m,
        target_lon , target_lat - 0.4, wrong_alt_m,
        requested_FL,
        i_element,
        route
    )
    assert result == -1

    # aircraft exited sector, the exit was at target waypoint but wrong altitude
    near_alt_m = requested_FL_m - 1500 * _SCALE_FEET_TO_METRES
    result = sector_exit_metric(
        target_lon, target_lat + 0.4, near_alt_m,
        target_lon, target_lat - 0.4, near_alt_m,
        requested_FL,
        i_element,
        route
    )
    assert result == -0.5

    # aircraft exited sector at correct altitude but NOT near target waypoint
    # exit latitude is 51.716, which is ~12 nautical miles from target
    result = sector_exit_metric(
        target_lon , target_lat + 0.2, requested_FL_m,
        target_lon , target_lat - 0.6, requested_FL_m,
        requested_FL,
        i_element,
        route
    )
    assert result == -1

    # aircraft exited sector at correct altitude but NOT near target waypoint
    # exit latitude is 51.816, which is ~6 nautical miles from target
    result = sector_exit_metric(
        target_lon , target_lat + 0.2, requested_FL_m,
        target_lon , target_lat - 0.4, requested_FL_m,
        requested_FL,
        i_element,
        route
    )
    assert result == -0.2
