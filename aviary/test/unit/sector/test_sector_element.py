
import pytest

import os
import geojson
import shapely
from io import StringIO

import aviary.constants as C
import aviary.sector.sector_element as se
import aviary.sector.sector_shape as ss
import aviary.utils.geo_helper as gh

def test_sector_element():

    origin = (-0.1275, 51.5) # longitude/latitude

    length_nm = 50
    airway_width_nm = 10

    shape = ss.IShape(length_nm = length_nm,
                       airway_width_nm = airway_width_nm)
    sector = se.SectorElement(shape = shape,
                              name = "I-Sector",
                              origin = origin,
                              )

    shape = ss.IShape(length_nm = 2 * length_nm,
                       airway_width_nm = airway_width_nm)
    longSector = se.SectorElement(shape = shape,
                              name = "Long-I-Sector",
                              origin = origin,
                              )

    shape = ss.IShape(length_nm = length_nm,
                        airway_width_nm = 2 * airway_width_nm)
    wideSector = se.SectorElement(shape = shape,
                              name = "Wide-I-Sector",
                              origin = origin,
                              )

    assert isinstance(sector, se.SectorElement)
    assert isinstance(longSector, se.SectorElement)
    assert isinstance(wideSector, se.SectorElement)

    lon, lat = sector.polygon().exterior.coords.xy
    longSector_lon, longSector_lat = longSector.polygon().exterior.coords.xy
    wideSector_lon, wideSector_lat = wideSector.polygon().exterior.coords.xy

    # Check that the "length" of the I shape runs north to south, and the "width" runs east to west.

    # In the longSector the latitudes should be different.
    # (Note: longitudes should be similar to the original sector but not identical due to the non-linear projection).
    assert longSector_lat[0] < lat[0]
    assert longSector_lat[1] > lat[1]
    assert longSector_lat[2] > lat[2]
    assert longSector_lat[3] < lat[3]

    # In the wideSector the longitudes should be different.
    # (Note: latitudes should be similar to the original sector but not identical due to the non-linear projection).
    assert wideSector_lon[0] < lon[0]
    assert wideSector_lon[1] < lon[1]
    assert wideSector_lon[2] > lon[2]
    assert wideSector_lon[3] > lon[3]


def test_sector_element_with_names():

    # route_names = ['up', 'down']
    fix_names = ['a', 'b', 'c', 'd', 'e']

    shape = ss.IShape(fix_names = fix_names)
                      # route_names = route_names)
    target = se.SectorElement(shape = shape,
                              name = "I-Sector-with-names",
                              origin = (0, 40),
                              )


    assert isinstance(target, se.SectorElement)
    # assert target.shape.sector_type == ss.SectorType.I
    # assert target.routes()[0].name == 'UP'
    # assert target.routes()[1].name == 'DOWN'

    assert 'A' in target.shape.fixes
    assert 'B' in target.shape.fixes
    assert 'C' in target.shape.fixes
    assert 'D' in target.shape.fixes
    assert 'E' in target.shape.fixes


# def test_fix(i_element):
#
#     result = i_element.fix(fix_name = "D")

def test_polygon(i_element):

    result = i_element.polygon()

    # The result is a Shapely Polygon.
    assert isinstance(result, shapely.geometry.polygon.Polygon)
    assert isinstance(result.exterior.coords, shapely.coords.CoordinateSequence)

    # Check that the I-element polygon contains five points.
    assert len(result.exterior.coords) == 5

    # Each coordinate is a (lon, lat) tuple.
    assert isinstance(result.exterior.coords[0], tuple)
    assert len(result.exterior.coords[0]) == 2


def test_centre_point(i_element):

    result = i_element.centre_point()
    assert result == pytest.approx((-0.1275, 51.5), 0.0001)

def test_fix_location(i_element):

    assert i_element.fix_location(fix_name = 'C') == pytest.approx((-0.1275, 51.5), 0.0001)
    assert i_element.fix_location(fix_name = 'A') == pytest.approx((-0.1275, 52.08), 0.0001)
    assert i_element.fix_location(fix_name = 'E') == pytest.approx((-0.1275, 50.92), 0.0001)

def test_routes(i_element):

    result = i_element.routes()

    # Route 1 goes from 'A' to 'E'.
    assert result[1].length() == 5
    assert result[1].fix_names()[0] == 'A'
    assert result[1].fix_points()[0].coords[0] == pytest.approx((-0.1275, 52.08), 0.0001)

    assert result[1].fix_names()[4] == 'E'
    assert result[1].fix_points()[4].coords[0] == pytest.approx((-0.1275, 50.92), 0.0001)

    # Route 0 goes from 'E' to 'A'.
    assert result[0].length() == 5
    assert result[0].fix_names()[0] == 'E'
    assert result[0].fix_points()[0].coords[0] == pytest.approx((-0.1275, 50.92), 0.0001)

    assert result[0].fix_names()[4] == 'A'
    assert result[0].fix_points()[4].coords[0] == pytest.approx((-0.1275, 52.08), 0.0001)


def test_sector_geojson(i_element):

    result = i_element.sector_geojson()

    assert sorted(result.keys()) == sorted([C.GEOMETRY_KEY, C.PROPERTIES_KEY, C.TYPE_KEY])

    assert result[C.TYPE_KEY] == C.FEATURE_VALUE

    assert isinstance(result[C.PROPERTIES_KEY], dict)
    assert sorted(result[C.PROPERTIES_KEY].keys()) == \
           sorted([C.CHILDREN_KEY, C.NAME_KEY, C.SHAPE_KEY, C.ORIGIN_KEY, C.TYPE_KEY])

    assert result[C.PROPERTIES_KEY][C.TYPE_KEY] == C.SECTOR_VALUE
    assert result[C.PROPERTIES_KEY][C.SHAPE_KEY] == "I"

    assert isinstance(result[C.PROPERTIES_KEY][C.CHILDREN_KEY], dict)
    assert sorted(result[C.PROPERTIES_KEY][C.CHILDREN_KEY].keys()) == \
           sorted([C.ROUTE_VALUE, C.SECTOR_VOLUME_VALUE])

    assert isinstance(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.ROUTE_VALUE], dict)
    assert sorted(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.ROUTE_VALUE].keys()) == \
           [C.CHILDREN_NAMES_KEY]

    assert isinstance(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.ROUTE_VALUE][C.CHILDREN_NAMES_KEY], list)
    assert len(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.ROUTE_VALUE][C.CHILDREN_NAMES_KEY]) == len(i_element.shape.routes)

    assert isinstance(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.SECTOR_VOLUME_VALUE], dict)
    assert sorted(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.SECTOR_VOLUME_VALUE].keys()) == [C.CHILDREN_NAMES_KEY]
    assert len(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.SECTOR_VOLUME_VALUE]) == 1

    assert isinstance(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.SECTOR_VOLUME_VALUE][C.CHILDREN_NAMES_KEY], list)

def test_boundary_geojson(i_element):

    result = i_element.boundary_geojson()

    assert sorted(result.keys()) == sorted([C.GEOMETRY_KEY, C.PROPERTIES_KEY, C.TYPE_KEY])

    assert result[C.TYPE_KEY] == C.FEATURE_VALUE

    assert sorted(result[C.GEOMETRY_KEY].keys()) == sorted([C.COORDINATES_KEY, C.TYPE_KEY])

    assert result[C.GEOMETRY_KEY][C.TYPE_KEY] == C.POLYGON_VALUE

    # Multiple coordinate pairs are stored as a list of tuples.
    assert isinstance(result[C.GEOMETRY_KEY][C.COORDINATES_KEY], list)
    assert isinstance(result[C.GEOMETRY_KEY][C.COORDINATES_KEY][0], list)
    assert isinstance(result[C.GEOMETRY_KEY][C.COORDINATES_KEY][0][0], tuple)

    # The I geometry contains 5 "bounding box" points (since the first and last are duplicates).
    assert len(result[C.GEOMETRY_KEY][C.COORDINATES_KEY][0]) == 5

    # # Check the order of coordinates is correct, i.e. (longitude, latitude):
    assert result[C.GEOMETRY_KEY][C.COORDINATES_KEY][0][0] == (-0.2597, 51.0838)

    assert sorted(result[C.PROPERTIES_KEY].keys()) == \
           sorted([C.NAME_KEY, C.TYPE_KEY, C.UPPER_LIMIT_KEY, C.LOWER_LIMIT_KEY, C.CHILDREN_KEY])
                   # C.LENGTH_NM_KEY, C.AIRWAY_WIDTH_NM_KEY, C.OFFSET_NM_KEY, C.CHILDREN_KEY])

    assert isinstance(result[C.PROPERTIES_KEY][C.NAME_KEY], str)
    assert result[C.PROPERTIES_KEY][C.TYPE_KEY] == C.SECTOR_VOLUME_VALUE
    assert isinstance(result[C.PROPERTIES_KEY][C.UPPER_LIMIT_KEY], int)
    assert isinstance(result[C.PROPERTIES_KEY][C.LOWER_LIMIT_KEY], int)
    assert isinstance(result[C.PROPERTIES_KEY][C.CHILDREN_KEY], dict)

def test_waypoint_geojson(i_element):

    name = 'b'.upper()
    result = i_element.waypoint_geojson(name)

    assert sorted(result.keys()) == sorted([C.GEOMETRY_KEY, C.PROPERTIES_KEY, C.TYPE_KEY])

    assert result[C.TYPE_KEY] == C.FEATURE_VALUE

    assert sorted(result[C.GEOMETRY_KEY].keys()) == sorted([C.COORDINATES_KEY, C.TYPE_KEY])
    assert result[C.GEOMETRY_KEY][C.TYPE_KEY] == C.POINT_VALUE

    # A single coordinate pair is stored as a tuple.
    #assert isinstance(result[C.GEOMETRY_KEY][C.COORDINATES_KEY], list)
    assert isinstance(result[C.GEOMETRY_KEY][C.COORDINATES_KEY], tuple)
    assert len(result[C.GEOMETRY_KEY][C.COORDINATES_KEY]) == 2

    assert sorted(result[C.PROPERTIES_KEY].keys()) == sorted([C.NAME_KEY, C.TYPE_KEY])
    assert result[C.PROPERTIES_KEY][C.NAME_KEY] == name.upper()
    assert result[C.PROPERTIES_KEY][C.TYPE_KEY] == C.FIX_VALUE

    # Check the order of coordinates is correct, i.e. (longitude, latitude):
    assert result[C.GEOMETRY_KEY][C.COORDINATES_KEY] == (-0.1275, 51.9161)

def test_geo_interface(y_element):

    result = y_element.__geo_interface__

    assert sorted(result.keys()) == [C.FEATURES_KEY, C.TYPE_KEY]

    # The result contains one feature per route and per fix, plus one
    # for the sector, one for the sector boundary/volume and one for the FIR.
    assert len(result[C.FEATURES_KEY]) == len(y_element.shape.routes) + len(y_element.shape.fixes) + 3


def test_contains(i_element):

    # boundaries = gh.GeoHelper().__inv_project__(i_element.projection, i_element.shape.polygon)
    boundaries = i_element.shape.polygon
    exterior = list(boundaries.exterior.coords)

    centre = i_element.centre_point()
    interior = [centre, (-0.259, 51.0838), (0.004, 51.0838), (-0.262, 51.916), (0.007, 51.916)]

    FLs = [i_element.lower_limit, i_element.lower_limit + 50, i_element.upper_limit - 50, i_element.upper_limit]

    for fl in FLs:
        for lon, lat in interior:
            assert i_element.contains(lon=lon, lat=lat, flight_level=fl)
        for lon, lat in exterior:
            assert not i_element.contains(lon=lon, lat=lat, flight_level=fl)

    assert not i_element.contains(centre[0], centre[1], flight_level=i_element.lower_limit-10)
    assert not i_element.contains(centre[0], centre[1], flight_level=i_element.upper_limit+10)


def test_serialisation(x_element):
    # Test JSON serialisation/deserialisation.

    serialised = geojson.dumps(x_element, sort_keys=True, indent = 4)

    deserialised = geojson.loads(serialised)

    assert isinstance(deserialised, dict)
    assert list(deserialised.keys()) == [C.TYPE_KEY, C.FEATURES_KEY]


def test_write_geojson(x_element):

    filename = "x_sector_hell"
    here = os.path.abspath(os.path.dirname(__file__))
    file = x_element.write_geojson(
        filename = filename,
        path = here
        )

    assert os.path.exists(file)

    # Clean up.
    os.remove(file)


def test_hash_sector_coordinates(x_element):

    result = x_element.hash_sector_coordinates()
    assert result == x_element.hash_sector_coordinates()
    different_result = x_element.hash_sector_coordinates(C.FLOAT_PRECISION + 1)
    assert not result == different_result


def test_deserialise(i_sector_geojson, i_element):
#
    print(list(i_element.shape.polygon.exterior.coords))
    print(i_element.sector_geojson())

    #TODO: update tests
    result = se.SectorElement.deserialise(StringIO(i_sector_geojson))
#
#     assert isinstance(result, se.SectorElement)
#     assert result.origin == C.DEFAULT_ORIGIN
#     assert result.shape.sector_type == ss.SectorType.I
#
#     assert result.lower_limit == 50
#     assert result.upper_limit == 450
#
#     assert result.shape.length_nm == 100
#     assert result.shape.airway_width_nm == 20
#     assert result.shape.offset_nm == 40
#
#     # Check that re-serialisation produces the original GeoJSON string
    print(geojson.dumps(result))
    assert str(geojson.dumps(result)) == i_sector_geojson.strip()


def test_sector_is_valid_geojson(i_sector_geojson):
    loaded = geojson.loads(i_sector_geojson)
    # print(loaded.errors())
    assert loaded.is_valid
