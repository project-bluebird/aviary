import pytest

import os
from io import StringIO

import aviary.parser.sector_parser as sp

import aviary.constants as C
import aviary.scenario.scenario_generator as sg
import aviary.sector.sector_shape as ss
import aviary.sector.sector_element as se
import aviary.sector.route as rt
import aviary.utils.geo_helper as gh

import shapely.geometry as geom


@pytest.fixture(scope="function")
def target(i_sector_geojson):
    return sp.SectorParser(StringIO(i_sector_geojson))


def test_features_of_type(target):

    # Get the (singleton) list of sector features.
    result = target.features_of_type(C.SECTOR_VALUE)

    assert isinstance(result, list)
    assert len(result) == 1

    assert isinstance(result[0], dict)
    assert sorted(result[0].keys()) == sorted([C.TYPE_KEY, C.PROPERTIES_KEY, C.GEOMETRY_KEY])


def test_fix_features(target):

    result = target.fix_features()

    assert isinstance(result, list)
    assert len(result) == 5
    for fix in result:
        assert isinstance(fix, dict)
        assert sorted(fix.keys()) == sorted([C.TYPE_KEY, C.PROPERTIES_KEY, C.GEOMETRY_KEY])


def test_fix_names(target):

    result = target.fix_names()
    assert result == [name.upper() for name in ss.IShape.i_fix_names]

#
# def test_route_names(target):
#
#     result = target.route_names()
#     assert result == [name.upper() for name in ss.SectorShape.i_route_names]
#

def test_properties_of_type(target):

    result = target.properties_of_type(C.SECTOR_VALUE)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)
    assert sorted(result[0].keys()) == sorted([C.NAME_KEY, C.TYPE_KEY, C.SHAPE_KEY, C.ORIGIN_KEY, C.CHILDREN_KEY])


def test_sector_volume_properties(target):

    result = target.sector_volume_properties()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)
    assert sorted(result[0].keys()) == sorted([C.NAME_KEY, C.TYPE_KEY,
                                               C.CHILDREN_KEY, C.UPPER_LIMIT_KEY, C.LOWER_LIMIT_KEY,
                                               C.LENGTH_NM_KEY, C.AIRWAY_WIDTH_NM_KEY, C.OFFSET_NM_KEY])


def test_geometries_of_type(target):

    result = target.geometries_of_type(C.POINT_VALUE)

    assert isinstance(result, list)
    assert len(result) == 5
    for fix in result:
        assert isinstance(fix, dict)
        assert sorted(fix.keys()) == sorted([C.TYPE_KEY, gh.COORDINATES_KEY])


def test_polygon_geometries(target):

    result = target.polygon_geometries()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)


def test_sector_polygon(target):

    result = target.sector_polygon()

    assert isinstance(result, geom.polygon.BaseGeometry)
    # assert sorted(result.keys()) == sorted([C.TYPE_KEY, gh.COORDINATES_KEY])
    #
    # # coordinates are nested list - at lowest level should have 5 coordinates
    # # the first and last coordinate is the same
    # coords = result[gh.COORDINATES_KEY]
    # while len(coords) == 1:
    #     coords = coords[0]
    # assert len(coords) == 5
    # assert coords[0] == coords[-1]


def test_sector_name(target):
    result = target.sector_name()
    assert result == "test_sector"


def test_sector_type(target):
    result = target.sector_type()
    assert result == "I"


def test_sector_origin(target):
    result = target.sector_origin()

    # Sector origin is exactly equal to the origin passed to the SectorElement constructor.
    assert result.coords[0] == C.DEFAULT_ORIGIN


# def test_sector_centroid(target):
#     result = target.sector_centroid()
#
#     # Sector centroid is approximately, but not exactly, equal to the origin
#     # passed to the SectorElement constructor (as the centroid is computed
#     # from the coordinates of the polygon, resulting in a small numerical error).
#     assert not result.coords[0] == C.DEFAULT_ORIGIN
#     assert result.coords[0] == pytest.approx(C.DEFAULT_ORIGIN, 0.0001)
#

# def test_sector_lower_limit(target):
#     result = target.sector_lower_limit()
#
#     assert isinstance(result, int)
#
#     # Note that the lower limit in the test fixture is not the default value.
#     assert result == 50
#
#
# def test_sector_upper_limit(target):
#     result = target.sector_upper_limit()
#
#     assert isinstance(result, int)
#
#     # Note that the upper limit in the test fixture is not the default value.
#     assert result == 450
#
#
# def test_sector_length_nm(target):
#     result = target.sector_length_nm()
#
#     assert isinstance(result, int)
#
#     # Note that the length in the test fixture is not the default value.
#     assert result == 100


# def test_sector_airway_width_nm(target):
#     result = target.sector_airway_width_nm()
#
#     assert isinstance(result, int)
#
#     # Note that the airway width in the test fixture is not the default value.
#     assert result == 20
#
#
# def test_waypoint_offset_nm(target):
#     result = target.waypoint_offset_nm()
#
#     assert isinstance(result, int)
#
#     # Note that the waypoint offset in the test fixture is not the default value.
#     assert result == 40
