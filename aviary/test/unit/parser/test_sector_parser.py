import pytest

import os
from io import StringIO

import aviary.parser.sector_parser as sp

import aviary.scenario.scenario_generator as sg
import aviary.sector.sector_element as se
import aviary.sector.route as rt
import aviary.geo.geo_helper as gh

#TO DO - create geojson and json using fixtures in conftest ??

# geoJSON sector obtained by calling geojson.dumps() on an X-shaped SectorElement.
i_sector_geojson = """
{"features": [{"type": "Feature", "geometry": {}, "properties": {"name": "test_sector", "type": "SECTOR", "children": {"SECTOR_VOLUME": {"names": ["221395673130872533"]}, "ROUTE": {"names": ["ASCENSION", "FALLEN"]}}}}, {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-0.2596527086555938, 51.08375683891335], [-0.26207557205922527, 51.916052359621695], [0.007075572059225247, 51.916052359621695], [0.004652708655593784, 51.08375683891335], [-0.2596527086555938, 51.08375683891335]]]}, "properties": {"name": "221395673130872533", "type": "SECTOR_VOLUME", "lower_limit": 60, "upper_limit": 460, "children": {}}}, {"type": "Feature", "properties": {"name": "ASCENSION", "type": "ROUTE", "children": {"FIX": {"names": ["FIYRE", "EARTH", "WATER", "AIR", "SPIRT"]}}}, "geometry": {"type": "LineString", "coordinates": [[-0.1275, 50.91735552314281], [-0.1275, 51.08383154960228], [-0.1275, 51.49999999999135], [-0.1275, 51.916128869951486], [-0.1275, 52.08256690115545]]}}, {"type": "Feature", "properties": {"name": "FALLEN", "type": "ROUTE", "children": {"FIX": {"names": ["SPIRT", "AIR", "WATER", "EARTH", "FIYRE"]}}}, "geometry": {"type": "LineString", "coordinates": [[-0.1275, 52.08256690115545], [-0.1275, 51.916128869951486], [-0.1275, 51.49999999999135], [-0.1275, 51.08383154960228], [-0.1275, 50.91735552314281]]}}, {"type": "Feature", "properties": {"name": "SPIRT", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 52.08256690115545]}}, {"type": "Feature", "properties": {"name": "AIR", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.916128869951486]}}, {"type": "Feature", "properties": {"name": "WATER", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.49999999999135]}}, {"type": "Feature", "properties": {"name": "EARTH", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.08383154960228]}}, {"type": "Feature", "properties": {"name": "FIYRE", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 50.91735552314281]}}]}
"""

@pytest.fixture(scope="function")
def target():
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
    assert result.coords[0] == pytest.approx(se.DEFAULT_ORIGIN[::-1], 0.0001)

