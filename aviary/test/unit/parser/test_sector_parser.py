import pytest

import os
from io import StringIO

import aviary.parser.sector_parser as sp

import aviary.scenario.scenario_generator as sg
import aviary.sector.sector_element as se
import aviary.sector.route as rt
import aviary.geo.geo_helper as gh


@pytest.fixture(scope="function")
def target(i_sector_geojson):
    return sp.SectorParser(StringIO(i_sector_geojson))


def test_features_of_type(target):

    # Get the (singleton) list of sector features.
    result = target.features_of_type(se.SECTOR_VALUE)

    assert isinstance(result, list)
    assert len(result) == 1

    assert isinstance(result[0], dict)
    assert sorted(result[0].keys()) == sorted([se.TYPE_KEY, se.PROPERTIES_KEY, se.GEOMETRY_KEY])


def test_fix_features(target):

    result = target.fix_features()

    assert isinstance(result, list)
    assert len(result) == 5
    for fix in result:
        assert isinstance(fix, dict)
        assert sorted(fix.keys()) == sorted([se.TYPE_KEY, se.PROPERTIES_KEY, se.GEOMETRY_KEY])


def test_properties_of_type(target):

    result = target.properties_of_type(se.SECTOR_VALUE)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)
    assert sorted(result[0].keys()) == sorted([se.NAME_KEY, se.TYPE_KEY, se.CHILDREN_KEY])


def test_sector_volume_properties(target):

    result = target.sector_volume_properties()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)
    assert sorted(result[0].keys()) == sorted([se.NAME_KEY, se.TYPE_KEY, se.CHILDREN_KEY, se.UPPER_LIMIT_KEY, se.LOWER_LIMIT_KEY])


def test_geometries_of_type(target):

    result = target.geometries_of_type(se.POINT_VALUE)

    assert isinstance(result, list)
    assert len(result) == 5
    for fix in result:
        assert isinstance(fix, dict)
        assert sorted(fix.keys()) == sorted([se.TYPE_KEY, gh.COORDINATES_KEY])


def test_polygon_geometries(target):

    result = target.polygon_geometries()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)


def test_sector_polygon(target):

    result = target.sector_polygon()

    assert isinstance(result, dict)
    assert sorted(result.keys()) == sorted([se.TYPE_KEY, gh.COORDINATES_KEY])

    # coordinates are nested list - at lowest level should have 5 coordinates
    # the first and last coordinate is the same
    coords = result[gh.COORDINATES_KEY]
    while len(coords) == 1:
        coords = coords[0]
    assert len(coords) == 5
    assert coords[0] == coords[-1]


def test_sector_name(target):
    result = target.sector_name()
    assert result == "test_sector"


def test_sector_centroid(target):
    result = target.sector_centroid()
    assert result.coords[0] == pytest.approx(se.DEFAULT_ORIGIN, 0.0001)

