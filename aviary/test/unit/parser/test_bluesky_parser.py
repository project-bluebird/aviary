import pytest

import os
from io import StringIO

import aviary.parser.bluesky_parser as bp

import aviary.scenario.scenario_generator as sg
import aviary.sector.sector_element as se
import aviary.sector.route as rt
import aviary.utils.geo_helper as gh


@pytest.fixture(scope="function")
def target(i_sector_geojson, overflier_climber_scenario_json):
    return bp.BlueskyParser(StringIO(i_sector_geojson), StringIO(overflier_climber_scenario_json))


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
        assert x[0:len(bp.BS_DEFWPT_PREFIX)] == bp.BS_DEFWPT_PREFIX
        assert x[len(bp.BS_DEFWPT_PREFIX):(len(bp.BS_DEFWPT_PREFIX) + len(bp.BS_DEFINE_WAYPOINT))] == bp.BS_DEFINE_WAYPOINT


def test_all_lines(target):

    result = target.all_lines()
    assert isinstance(result, list)
    # 1 PAN  + 1 POLYALT  + 5 DEFWPT + 2 CRE + 5 ADDWPT + 5 ADDWPT + 1 ASAS
    assert len(result) == 1 + 1 + 5 + 2 + 5 + 5 + 1


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
        assert isinstance(fix, dict)
        assert sorted(fix.keys()) == sorted([se.GEOMETRY_KEY, rt.FIX_NAME_KEY])
        assert isinstance(fix[rt.FIX_NAME_KEY], str)
        assert fix[rt.FIX_NAME_KEY] in ["FIYRE", "EARTH", "WATER", "AIR", "SPIRT"]
        assert isinstance(fix[se.GEOMETRY_KEY], dict)
        assert sorted(fix[se.GEOMETRY_KEY].keys()) == sorted([se.TYPE_KEY, gh.COORDINATES_KEY])


def test_create_aircraft_lines(target):

    result = target.create_aircraft_lines()

    # The result is a list of two BlueSky create aircraft commands (CRE).
    assert isinstance(result, list)
    assert len(result) == 2

    # All create aircraft commands begin with "HH:MM:SS.00>CRE"
    for x in result:
        assert x[len(bp.BS_DEFWPT_PREFIX):(len(bp.BS_DEFWPT_PREFIX) + len(bp.BS_CREATE_AIRCRAFT))] == bp.BS_CREATE_AIRCRAFT


def test_add_aircraft_waypoint_lines(target):

    result = target.add_aircraft_waypoint_lines(callsign = "VJ159")

    assert isinstance(result, list)
    assert len(result) == 5

    result2 = target.add_aircraft_waypoint_lines(callsign = "VJ405")
    assert isinstance(result2, list)
    assert len(result2) == 5


def test_add_waypoint_lines(target):

    result = target.add_waypoint_lines()

    assert isinstance(result, list)
    assert len(result) == 10


def test_write_bluesky_scenario(target):

    here = os.path.abspath(os.path.dirname(__file__))
    file = target.write_bluesky_scenario(
        filename = "i_sector_parsed_scenario_test",
        path = here
        )
    assert os.path.exists(file)

    # Clean up.
    os.remove(file)
