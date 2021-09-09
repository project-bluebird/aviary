
import pytest

import json

import aviary.constants as C
import aviary.sector.route as sr
import aviary.sector.sector_element as se
# import aviary.utils.geo_helper as gh

# TODO - go over tests and check correctness of behaviour

def test_reverse(i_element):

    route_index = 1

    target = i_element.routes()[route_index]
    result = i_element.routes()[route_index].copy()
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

    assert sorted(result.keys()) == sorted([C.GEOMETRY_KEY, C.PROPERTIES_KEY, C.TYPE_KEY])

    assert result[C.TYPE_KEY] == C.FEATURE_VALUE

    assert sorted(result[C.PROPERTIES_KEY]) == \
           sorted([C.CHILDREN_KEY, C.NAME_KEY, C.TYPE_KEY])

    # TODO: UPDATE THIS PART OF THE TEST
    # assert result[C.PROPERTIES_KEY][C.NAME_KEY] == i_element.shape.route_names[route_index]
    assert result[C.PROPERTIES_KEY][C.TYPE_KEY] == C.ROUTE_VALUE
    assert sorted(result[C.PROPERTIES_KEY][C.CHILDREN_KEY].keys()) == [C.FIX_VALUE]
    assert isinstance(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.FIX_VALUE][C.CHILDREN_NAMES_KEY], list)
    assert len(result[C.PROPERTIES_KEY][C.CHILDREN_KEY][C.FIX_VALUE][C.CHILDREN_NAMES_KEY]) == len(i_element.shape.fixes)

    assert isinstance(result[C.GEOMETRY_KEY], dict)
    assert sorted(result[C.GEOMETRY_KEY].keys()) == sorted([C.COORDINATES_KEY, C.TYPE_KEY])

    assert isinstance(result[C.GEOMETRY_KEY][C.COORDINATES_KEY], list)
    assert len(result[C.GEOMETRY_KEY][C.COORDINATES_KEY]) == len(i_element.shape.fixes)


def test_serialize(i_element):

    target = i_element.routes()[1]
    result = target.serialize()

    assert isinstance(result, list)
    for x in result:
        assert isinstance(x, dict)
        assert list(x.keys()) == [sr.FIX_NAME_KEY, C.GEOMETRY_KEY]

    for i in range(target.length()):
        assert result[i][sr.FIX_NAME_KEY] == target.fix_names()[i]

    serialized = json.dumps(result, sort_keys=True)
    deserialized = json.loads(serialized)

    assert isinstance(deserialized, list)
    assert len(deserialized) == target.length()
    assert list(deserialized[0].keys()) == [sr.FIX_NAME_KEY, C.GEOMETRY_KEY]

    for i in range(target.length()):
        assert deserialized[i][sr.FIX_NAME_KEY] == target.fix_names()[i]

def test_next_waypoint(i_element):

    # Get the A to E route for the I sector.
    target = i_element.routes()[1]

    lonA, latA = target.fix_points()[0].coords[0]
    lonB, latB = target.fix_points()[1].coords[0]
    lonC, latC = target.fix_points()[2].coords[0]
    lonD, latD = target.fix_points()[3].coords[0]
    lonE, latE = target.fix_points()[4].coords[0]

    assert latB < latA # Sanity check: the route is due south.
    assert latC < latB # Sanity check: the route is due south.
    assert latD < latC # Sanity check: the route is due south.
    assert latE < latD # Sanity check: the route is due south.

    # If we're north of fix A, the next waypoint is A.
    assert target.next_waypoint(lat = latA + 1, lon = lonA) == 'A'

    # If we're halfway between fixes A and B, the next waypoint is B.
    assert target.next_waypoint(lat = (latA + latB)/2, lon = lonA) == 'B'

    # If we're halfway between fixes B and C, the next waypoint is C.
    assert target.next_waypoint(lat = (latB + latC)/2, lon = lonA) == 'C'

    # If we're halfway between fixes C and D, the next waypoint is D.
    assert target.next_waypoint(lat = (latC + latD)/2, lon = lonA) == 'D'

    # If we're halfway between fixes D and E, the next waypoint is E.
    assert target.next_waypoint(lat = (latD + latE)/2, lon = lonA) == 'E'

    # If we're south of fix E, the next waypoint is None.
    assert target.next_waypoint(lat = latE - 1, lon = lonA) is None


def test_truncate(i_element):

    # Get the A to E route for the I sector.
    target = i_element.routes()[1]
    full_route = i_element.routes()[1]#.copy()

    lonA, latA = target.fix_points()[0].coords[0]
    lonB, latB = target.fix_points()[1].coords[0]
    lonC, latC = target.fix_points()[2].coords[0]
    lonD, latD = target.fix_points()[3].coords[0]
    lonE, latE = target.fix_points()[4].coords[0]

    assert latB < latA # Sanity check: the route is due south.
    assert latC < latB # Sanity check: the route is due south.
    assert latD < latC # Sanity check: the route is due south.
    assert latE < latD # Sanity check: the route is due south.

    # If we start from north of fix A, the truncated route is identical to the original route
    target.truncate(initial_lat = latA + 1, initial_lon = lonA)
    assert target.fix_list == full_route.fix_list

    # If we start from halfway between fixes B and C, the truncated route omits both fixes A and B.
    target = i_element.routes()[1]

    # If we start from halfway between fixes A and B, the truncated route omits only fix A.
    target.truncate(initial_lat = (latA + latB)/2, initial_lon = lonA)
    assert target.fix_list == full_route.fix_list[1:]

    # If we start from halfway between fixes B and C, the truncated route omits both fixes A and B.
    target = i_element.routes()[1]

    target.truncate(initial_lat = (latB + latC)/2, initial_lon = lonA)
    assert target.fix_list == full_route.fix_list[2:]

    # If we start from halfway between fixes C and D, the truncated route omits fixes A, B and C.
    target = i_element.routes()[1]

    target.truncate(initial_lat = (latC + latD)/2, initial_lon = lonA)
    assert target.fix_list == full_route.fix_list[3:]

    # If we start from halfway between fixes D and E, the truncated route omits both fixes A, B, C and D.
    target = i_element.routes()[1]

    target.truncate(initial_lat = (latD + latE)/2, initial_lon = lonA)
    assert target.fix_list == full_route.fix_list[4:]

    # If we start from south of fix E, the truncated route has an empty fix list.
    target = i_element.routes()[1]

    target.truncate(initial_lat = latE - 1, initial_lon = lonA)
    assert not target.fix_list
