
import pytest

from aviary.geo.geo_helper import GeoHelper


def test_distance():

    lat1, lon1 = 51.5080, -0.1281
    lat2, lon2 = 50.6083, -1.9608

    result = GeoHelper.distance(lat1, lon1, lat2, lon2)
    assert result == pytest.approx(162.5e3, 0.01)

def test_waypoint_location():

    lat1, lon1 = 51.5080, -0.1281
    lat2, lon2 = 50.6083, -1.9608

    result = GeoHelper.waypoint_location(lat1, lon1, lat2, lon2, distance_m = 0)
    assert result == pytest.approx((lon1, lat1))

    result = GeoHelper.waypoint_location(lat1, lon1, lat2, lon2, distance_m = 162.5e3)
    assert result == pytest.approx((lon2, lat2), 0.01)

    result = GeoHelper.waypoint_location(lat1, lon1, lat2, lon2, distance_m = 81.25e3)
    assert result == pytest.approx((-1.051272, 51.06276), 0.01)

    # Check the behaviour in case the distance exceeds the separation between the fixes.
    result = GeoHelper.waypoint_location(lat1, lon1, lat2, lon2, distance_m = 250e3)
    assert result == pytest.approx((-2.9125, 50.1154), 0.01)


