
import pytest

import json

import aviary.sector.route as sr
import aviary.sector.sector_element as se
import aviary.geo.geo_helper as gh

def test_reverse(i_element):

    route_index = 1

    target = i_element.routes()[route_index]
    result = i_element.routes()[route_index]
    result.reverse()

    assert target.fix_names()[0] == 'A'
    assert target.fix_names()[1] == 'B'
    assert target.fix_names()[2] == 'C'
    assert target.fix_names()[3] == 'D'
    assert target.fix_names()[4] == 'E'

    assert result.fix_names()[0] == 'E'
    assert result.fix_names()[1] == 'D'
    assert result.fix_names()[2] == 'C'
    assert result.fix_names()[3] == 'B'
    assert result.fix_names()[4] == 'A'

    assert target.fix_points()[0] == result.fix_points()[4]
    assert target.fix_points()[1] == result.fix_points()[3]
    assert target.fix_points()[2] == result.fix_points()[2]
    assert target.fix_points()[3] == result.fix_points()[1]
    assert target.fix_points()[4] == result.fix_points()[0]

def test_geojson(i_element):

    route_index = 1
    target = i_element.routes()[route_index]
    result = target.geojson()

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
    assert sorted(result[se.GEOMETRY_KEY].keys()) == sorted([gh.COORDINATES_KEY, se.TYPE_KEY])

    assert isinstance(result[se.GEOMETRY_KEY][gh.COORDINATES_KEY], list)
    assert len(result[se.GEOMETRY_KEY][gh.COORDINATES_KEY]) == len(i_element.shape.fixes)


def test_serialize(i_element):

    target = i_element.routes()[1]
    result = target.serialize()


    assert isinstance(result, list)
    for x in result:
        assert isinstance(x, dict)
        assert list(x.keys()) == [sr.FIX_NAME_KEY, se.GEOMETRY_KEY]

    for i in range(target.length()):
        assert result[i][sr.FIX_NAME_KEY] == target.fix_names()[i]

    serialized = json.dumps(result, sort_keys=True)
    deserialized = json.loads(serialized)

    assert isinstance(deserialized, list)
    assert len(deserialized) == target.length()
    assert list(deserialized[0].keys()) == [sr.FIX_NAME_KEY, se.GEOMETRY_KEY]

    for i in range(target.length()):
        assert deserialized[i][sr.FIX_NAME_KEY] == target.fix_names()[i]

def test_truncate(i_element):

    # Get the A to E route for the I sector.
    target = i_element.routes()[1]
    full_route = i_element.routes()[1]

    lonA, latA = target.fix_points()[0].coords[0]
    lonB, latB = target.fix_points()[1].coords[0]
    lonC, latC = target.fix_points()[2].coords[0]

    assert latB < latA # Sanity check: the route is due south.
    assert latC < latB # Sanity check: the route is due south.

    # If we start from halfway between fixes A and B, the truncated route omits only fix A.
    target.truncate(initial_lat = (latA + latB)/2, initial_lon = lonA)
    assert target.fix_list == full_route.fix_list[1:]

    # If we start from halfway between fixes B and C, the truncated route omits both fixes A and B.
    target = i_element.routes()[1]

    target.truncate(initial_lat = (latB + latC)/2, initial_lon = lonA)
    assert target.fix_list == full_route.fix_list[2:]

