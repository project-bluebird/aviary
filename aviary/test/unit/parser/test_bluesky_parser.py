import pytest

import os

import aviary.parser.bluesky_parser as sp

import aviary.scenario.scenario_generator as sg
import aviary.sector.sector_element as se

#TO DO - create geojson and json using fixtures in conftest ??

# geoJSON sector obtained by calling geojson.dumps() on an X-shaped SectorElement.
i_sector_geojson = """
{"features": [{"type": "Feature", "geometry": {}, "properties": {"name": "test_sector", "type": "SECTOR", "children": {"SECTOR_VOLUME": {"names": ["221395673130872533"]}, "ROUTE": {"names": ["ASCENSION", "FALLEN"]}}}}, {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-0.2596527086555938, 51.08375683891335], [-0.26207557205922527, 51.916052359621695], [0.007075572059225247, 51.916052359621695], [0.004652708655593784, 51.08375683891335], [-0.2596527086555938, 51.08375683891335]]]}, "properties": {"name": "221395673130872533", "type": "SECTOR_VOLUME", "lower_limit": 60, "upper_limit": 460, "children": {}}}, {"type": "Feature", "properties": {"name": "ASCENSION", "type": "ROUTE", "children": {"FIX": {"names": ["FIYRE", "EARTH", "WATER", "AIR", "SPIRT"]}}}, "geometry": {"type": "LineString", "coordinates": [[-0.1275, 50.91735552314281], [-0.1275, 51.08383154960228], [-0.1275, 51.49999999999135], [-0.1275, 51.916128869951486], [-0.1275, 52.08256690115545]]}}, {"type": "Feature", "properties": {"name": "FALLEN", "type": "ROUTE", "children": {"FIX": {"names": ["SPIRT", "AIR", "WATER", "EARTH", "FIYRE"]}}}, "geometry": {"type": "LineString", "coordinates": [[-0.1275, 52.08256690115545], [-0.1275, 51.916128869951486], [-0.1275, 51.49999999999135], [-0.1275, 51.08383154960228], [-0.1275, 50.91735552314281]]}}, {"type": "Feature", "properties": {"name": "SPIRT", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 52.08256690115545]}}, {"type": "Feature", "properties": {"name": "AIR", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.916128869951486]}}, {"type": "Feature", "properties": {"name": "WATER", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.49999999999135]}}, {"type": "Feature", "properties": {"name": "EARTH", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.08383154960228]}}, {"type": "Feature", "properties": {"name": "FIYRE", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 50.91735552314281]}}]}
"""

# JSON scenario obtained by calling json.dumps() on an overflier_climber scenario in an I-shaped sector generated using ScenarioGenerator.
overflier_climber_scenario_json = """
{"startTime": "00:00:00", "aircraft": [{"timedelta": 0, "startPosition": [-0.1275, 50.80104879383575], "callsign": "VJ159", "type": "A346", "departure": "DEP", "destination": "DEST", "currentFlightLevel": 360, "clearedFlightLevel": 360, "requestedFlightLevel": 360, "route": [["EARTH", {"type": "Point", "coordinates": [-0.1275, 51.08383154960228]}], ["WATER", {"type": "Point", "coordinates": [-0.1275, 51.49999999999135]}], ["AIR", {"type": "Point", "coordinates": [-0.1275, 51.916128869951486]}], ["SPIRT", {"type": "Point", "coordinates": [-0.1275, 52.08256690115545]}]], "startTime": "00:00:00"}, {"timedelta": 0, "startPosition": [-0.1275, 52.27304310000724], "callsign": "VJ405", "type": "B77W", "departure": "DEST", "destination": "DEP", "currentFlightLevel": 300, "clearedFlightLevel": 300, "requestedFlightLevel": 400, "route": [["SPIRT", {"type": "Point", "coordinates": [-0.1275, 52.08256690115545]}], ["AIR", {"type": "Point", "coordinates": [-0.1275, 51.916128869951486]}], ["WATER", {"type": "Point", "coordinates": [-0.1275, 51.49999999999135]}], ["EARTH", {"type": "Point", "coordinates": [-0.1275, 51.08383154960228]}], ["FIYRE", {"type": "Point", "coordinates": [-0.1275, 50.91735552314281]}]], "startTime": "00:00:00"}]}
"""

@pytest.fixture(scope="function")
def target():
    return sp.ScenarioParser(i_sector_geojson, overflier_climber_scenario_json)


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


def test_geometris_of_type(target):

    result = target.geometries_of_type(se.POINT_VALUE)

    assert isinstance(result, list)
    assert len(result) == 5
    for fix in result:
        assert isinstance(fix, dict)
        assert sorted(fix.keys()) == sorted([se.TYPE_KEY, se.COORDINATES_KEY])


def test_polygon_geometries(target):

    result = target.polygon_geometries()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)


def test_sector_polygon(target):

    result = target.sector_polygon()

    assert isinstance(result, dict)
    assert sorted(result.keys()) == sorted([se.TYPE_KEY, se.COORDINATES_KEY])

    # coordinates are nested list - at lowest level should have 5 coordinates
    # the first and last coordinate is the same
    coords = result[se.COORDINATES_KEY]
    while len(coords) == 1:
        coords = coords[0]
    assert len(coords) == 5
    assert coords[0] == coords[-1]


def test_sector_name(target):
    result = target.sector_name()
    assert result == "test_sector"


def test_pan_lines(target):

    result = target.pan_lines()
    assert isinstance(result, list)
    assert len(result) == 1


def test_polyalt_lines(target):

    result = target.polyalt_lines()
    assert isinstance(result, list)
    assert len(result) == 1


def test_define_waypoint_lines(target):

    result = target.define_waypoint_lines()

    # The result is a list of BlueSky waypoint definitions (DEFWPT).
    assert isinstance(result, list)
    assert len(result) == 5

    # All waypoint definitions begin with "00:00:00.00>DEFWPT"
    for x in result:
        assert x[0:len(sp.BS_DEFWPT_PREFIX)] == sp.BS_DEFWPT_PREFIX
        assert x[len(sp.BS_DEFWPT_PREFIX):(len(sp.BS_DEFWPT_PREFIX) + len(sp.BS_DEFINE_WAYPOINT))] == sp.BS_DEFINE_WAYPOINT


def test_all_lines(target):

    result = target.all_lines()
    assert isinstance(result, list)
    # 1 PAN  + 1 POLYALT  + 5 DEFWPT + 2 CRE + 4 ADDWPT + 5 ADDWPT + 1 ASAS
    assert len(result) == 1 + 1 + 5 + 2 + 4 + 5 + 1


def test_aircraft_heading(target):

    # we are using an I scenario
    # --> one aircraft flies N-S and the other S-N
    result = target.aircraft_heading("VJ159")
    assert result == 0

    result2 = target.aircraft_heading("VJ405")
    assert result2 == 180


def test_bearing(target):

    # waypoint coordinates taken from an X scenario
    WITCH = [-1.0609024169298713, 51.49629572437266]
    SIREN = [-0.7942364352609249, 51.49811000242283]
    LIMBO = [-0.1275, 50.91735552314281]
    HAUNT = [-0.1275, 51.08383154960228]

    # WITCH is the left exterior and SIREN the left interior waypoint.
    assert target.bearing(from_waypoint = WITCH, to_waypoint=SIREN) - 90 < 1
    assert target.bearing(from_waypoint = SIREN, to_waypoint=WITCH) + 90 < 1

    # LIMBO is the bottom exterior and HAUNT the bottom interior waypoint.
    assert abs(target.bearing(from_waypoint = LIMBO, to_waypoint=HAUNT)) < 1
    assert abs(target.bearing(from_waypoint = HAUNT, to_waypoint=LIMBO)) - 180 < 1


def test_route(target):

    result = target.route(callsign = "VJ159")

    # result is a list of lists, each one a route element (fix/waypoint)
    assert isinstance(result, list)
    for fix in result:
        assert isinstance(fix, list)
        assert isinstance(fix[0], str)
        assert fix[0] in ["FIYRE", "EARTH", "WATER", "AIR", "SPIRT"]
        assert isinstance(fix[1], dict)
        assert sorted(fix[1].keys()) == sorted([se.TYPE_KEY, se.COORDINATES_KEY])


def test_create_aircraft_lines(target):

    result = target.create_aircraft_lines()

    # The result is a list of two BlueSky create aircraft commands (CRE).
    assert isinstance(result, list)
    assert len(result) == 2

    # All create aircraft commands begin with "HH:MM:SS.00>CRE"
    for x in result:
        assert x[len(sp.BS_DEFWPT_PREFIX):(len(sp.BS_DEFWPT_PREFIX) + len(sp.BS_CREATE_AIRCRAFT))] == sp.BS_CREATE_AIRCRAFT


def test_add_aircraft_waypoint_lines(target):

    result = target.add_aircraft_waypoint_lines(callsign = "VJ159")

    assert isinstance(result, list)
    assert len(result) == 4

    result2 = target.add_aircraft_waypoint_lines(callsign = "VJ405")
    assert isinstance(result2, list)
    assert len(result2) == 5


def test_add_waypoint_lines(target):

    result = target.add_waypoint_lines()

    assert isinstance(result, list)
    assert len(result) == 9


def test_write_bluesky_scenario(target):

    here = os.path.abspath(os.path.dirname(__file__))
    file = target.write_bluesky_scenario(
        filename = "i_sector_parsed_scenario_test",
        path = here
        )
    assert os.path.exists(file)

    # Clean up.
    os.remove(file)
