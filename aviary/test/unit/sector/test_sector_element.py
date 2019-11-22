
import pytest

import os
import geojson

import aviary.sector.sector_element as se

def test_centre_point(i_element):
    
    result = i_element.centre_point()
    assert result == pytest.approx((51.5, -0.1275), 0.0001)

def test_fix_location(i_element):

    assert i_element.fix_location(fix_name = 'C') == pytest.approx((51.5, -0.1275), 0.0001)
    assert i_element.fix_location(fix_name = 'A') == pytest.approx((52.08, -0.1275), 0.0001)
    assert i_element.fix_location(fix_name = 'E') == pytest.approx((50.92, -0.1275), 0.0001)

def test_routes(i_element):

    result = i_element.routes()

    # Route 1 goes from 'A' to 'E'.
    assert len(result[1]) == 5
    assert result[1][0][0] == 'A'
    assert result[1][0][1].coords[0] == pytest.approx((-0.1275, 52.08), 0.0001)

    assert result[1][4][0] == 'E'
    assert result[1][4][1].coords[0] == pytest.approx((-0.1275, 50.92), 0.0001)

    # Route 0 goes from 'E' to 'A'.
    assert len(result[0]) == 5
    assert result[0][0][0] == 'E'
    assert result[0][0][1].coords[0] == pytest.approx((-0.1275, 50.92), 0.0001)

    assert result[0][4][0] == 'A'
    assert result[0][4][1].coords[0] == pytest.approx((-0.1275, 52.08), 0.0001)


def test_truncate_route(i_element):

    # Get the A to E route for the I sector.
    route = i_element.routes()[1]

    lonA, latA = route[0][1].coords[0]
    lonB, latB = route[1][1].coords[0]
    lonC, latC = route[2][1].coords[0]

    assert latB < latA # Sanity check: the route is due south.
    assert latC < latB # Sanity check: the route is due south.

    # If we start from halfway between fixes A and B, the truncated route omits only fix A.
    assert i_element.truncate_route(route, initial_lat = (latA + latB)/2, initial_lon = lonA) == route[1:]

    # If we start from halfway between fixes B and C, the truncated route omits both fixes A and B.
    assert i_element.truncate_route(route, initial_lat = (latB + latC)/2, initial_lon = lonA) == route[2:]


def test_sector_geojson(i_element):

    result = i_element.sector_geojson()

    assert sorted(result.keys()) == sorted([se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY])

    assert result[se.TYPE_KEY] == se.FEATURE_VALUE

    assert isinstance(result[se.PROPERTIES_KEY], dict)
    assert sorted(result[se.PROPERTIES_KEY].keys()) == \
           sorted([se.CHILDREN_KEY, se.NAME_KEY, se.TYPE_KEY])

    assert result[se.PROPERTIES_KEY][se.TYPE_KEY] == se.SECTOR_VALUE

    assert isinstance(result[se.PROPERTIES_KEY][se.CHILDREN_KEY], dict)
    assert sorted(result[se.PROPERTIES_KEY][se.CHILDREN_KEY].keys()) == \
           sorted([se.ROUTE_VALUE, se.SECTOR_VOLUME_VALUE])

    assert isinstance(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.ROUTE_VALUE], dict)
    assert sorted(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.ROUTE_VALUE].keys()) == \
           [se.CHILDREN_NAMES_KEY]

    assert isinstance(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.ROUTE_VALUE][se.CHILDREN_NAMES_KEY], list)
    assert len(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.ROUTE_VALUE][se.CHILDREN_NAMES_KEY]) == len(i_element.shape.route_names)

    assert isinstance(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.SECTOR_VOLUME_VALUE], dict)
    assert sorted(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.SECTOR_VOLUME_VALUE].keys()) == [se.CHILDREN_NAMES_KEY]
    assert len(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.SECTOR_VOLUME_VALUE]) == 1

    assert isinstance(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.SECTOR_VOLUME_VALUE][se.CHILDREN_NAMES_KEY], list)

def test_boundary_geojson(i_element):

    result = i_element.boundary_geojson()

    assert sorted(result.keys()) == sorted([se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY])

    assert result[se.TYPE_KEY] == se.FEATURE_VALUE

    assert sorted(result[se.GEOMETRY_KEY].keys()) == sorted([se.COORDINATES_KEY, se.TYPE_KEY])

    assert result[se.GEOMETRY_KEY][se.TYPE_KEY] == se.POLYGON_VALUE
    assert isinstance(result[se.GEOMETRY_KEY][se.COORDINATES_KEY], list)
    # TODO: check length of coordinates

    assert sorted(result[se.PROPERTIES_KEY].keys()) == \
           sorted([se.NAME_KEY, se.TYPE_KEY, se.UPPER_LIMIT_KEY, se.LOWER_LIMIT_KEY, se.CHILDREN_KEY])

    assert isinstance(result[se.PROPERTIES_KEY][se.NAME_KEY], str)
    assert result[se.PROPERTIES_KEY][se.TYPE_KEY] == se.SECTOR_VOLUME_VALUE
    assert isinstance(result[se.PROPERTIES_KEY][se.UPPER_LIMIT_KEY], int)
    assert isinstance(result[se.PROPERTIES_KEY][se.LOWER_LIMIT_KEY], int)
    assert isinstance(result[se.PROPERTIES_KEY][se.CHILDREN_KEY], dict)

def test_waypoint_geojson(i_element):

    name = 'b'.upper()
    result = i_element.waypoint_geojson(name)

    assert sorted(result.keys()) == sorted([se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY])

    assert result[se.TYPE_KEY] == se.FEATURE_VALUE

    assert sorted(result[se.GEOMETRY_KEY].keys()) == sorted([se.COORDINATES_KEY, se.TYPE_KEY])
    assert result[se.GEOMETRY_KEY][se.TYPE_KEY] == se.POINT_VALUE
    assert isinstance(result[se.GEOMETRY_KEY][se.COORDINATES_KEY], list)
    assert len(result[se.GEOMETRY_KEY][se.COORDINATES_KEY]) == 2

    assert sorted(result[se.PROPERTIES_KEY].keys()) == sorted([se.NAME_KEY, se.TYPE_KEY])
    assert result[se.PROPERTIES_KEY][se.NAME_KEY] == name.upper()
    assert result[se.PROPERTIES_KEY][se.TYPE_KEY] == se.FIX_VALUE

def test_route_geojson(i_element):

    route_index = 1
    result = i_element.route_geojson(route_index = route_index)

    assert sorted(result.keys()) == sorted([se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY])

    assert result[se.TYPE_KEY] == se.FEATURE_VALUE

    assert sorted(result[se.PROPERTIES_KEY]) == \
           sorted([se.CHILDREN_KEY, se.NAME_KEY, se.TYPE_KEY])

    assert result[se.PROPERTIES_KEY][se.NAME_KEY] == i_element.shape.route_names[route_index]
    assert result[se.PROPERTIES_KEY][se.TYPE_KEY] == se.ROUTE_VALUE
    assert sorted(result[se.PROPERTIES_KEY][se.CHILDREN_KEY].keys()) == [se.FIX_VALUE]
    assert isinstance(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.FIX_VALUE][se.CHILDREN_NAMES_KEY], list)
    assert len(result[se.PROPERTIES_KEY][se.CHILDREN_KEY][se.FIX_VALUE][se.CHILDREN_NAMES_KEY]) == len(i_element.shape.fixes)

    assert isinstance(result[se.GEOMETRY_KEY], dict)
    assert sorted(result[se.GEOMETRY_KEY].keys()) == sorted([se.COORDINATES_KEY, se.TYPE_KEY])

    assert isinstance(result[se.GEOMETRY_KEY][se.COORDINATES_KEY], list)
    assert len(result[se.GEOMETRY_KEY][se.COORDINATES_KEY]) == len(i_element.shape.fixes)


def test_geo_interface(y_element):

    result = y_element.__geo_interface__

    assert sorted(result.keys()) == [se.FEATURES_KEY]

    # The result contains one feature per route and per waypoint, plus one for the sector and one for the sector boundary/volume.
    assert len(result[se.FEATURES_KEY]) == len(y_element.shape.route_names) + len(y_element.shape.fixes) + 2


def test_serialisation(x_element):
    # Test JSON serialisation/deserialisation.

    serialised = geojson.dumps(x_element, sort_keys=True, indent = 4)

    deserialised = geojson.loads(serialised)

    assert isinstance(deserialised, dict)
    assert list(deserialised.keys()) == [se.FEATURES_KEY]


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
