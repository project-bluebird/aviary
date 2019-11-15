
import pytest

import aviary.scenario.overflier_climber_scenario as ocs
import aviary.scenario.scenario_generator as sg

from aviary.geo.geo_helper import GeoHelper

@pytest.fixture(scope="function")
def target():
    """Test fixture: an overflier-climber scenario object."""

    return ocs.OverflierClimberScenario(aircraft_types = ['B744', 'B743'],
                                        callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                                        flight_levels = [200, 400],
                                        seed = 223)


# Test the callsign generator method in the base class ScenarioAlgorithm.
# This checks that the **kwargs are correctly passed to the superconstructor.
def test_callsign_generator(target):

    ctr = 0
    for x in target.callsign_generator():
        if ctr == 0:
            assert x == 'VJ597'
        if ctr == 1:
            assert x == 'SPEEDBIRD681'
        if ctr > 1:
            break
        ctr = ctr + 1


def test_overflier_flight_level(target):

    for i in range(0, 100):
        result = target.overflier_flight_level()
        assert result in target.flight_levels
        assert result > min(target.flight_levels)


def test_aircraft_generator(target, i_element):

    # Test across multiple generated scenarios.
    ctr = 0
    for x in target.aircraft_generator(i_element):

        assert isinstance(x, dict)
        assert sorted(x.keys()) == [sg.CALLSIGN_KEY, sg.CLEARED_FLIGHT_LEVEL_KEY, sg.CURRENT_FLIGHT_LEVEL_KEY,
                                    sg.DEPARTURE_KEY, sg.DESTINATION_KEY, sg.REQUESTED_FLIGHT_LEVEL_KEY, sg.ROUTE_KEY,
                                    sg.START_POSITION_KEY, sg.START_TIME_KEY, sg.AIRCRAFT_TYPE_KEY]

        ctr = ctr + 1
        if ctr == 1:
            overflier = x
        if ctr == 2:
            climber = x

    # Check that the scenario contains precisely two aircraft.
    assert ctr == 2

    assert overflier[sg.AIRCRAFT_TYPE_KEY] == 'B744'
    assert climber[sg.AIRCRAFT_TYPE_KEY] == 'B743'

    assert overflier[sg.CURRENT_FLIGHT_LEVEL_KEY] == 400
    assert climber[sg.CURRENT_FLIGHT_LEVEL_KEY] == 200
    assert climber[sg.REQUESTED_FLIGHT_LEVEL_KEY] == 400

    # TODO: include these:
    # assert [i[0] for i in overflier[sg.ROUTE_KEY]] == ['C', 'B', 'A']
    # assert [i[0] for i in climber[sg.ROUTE_KEY]] == ['C', 'D', 'E']

    # Check that the aircraft will be in conflict at the centre point of the sector (assuming default trajectories).

    overflier_speed = 316.7942522 # From the lookup tables (m/s)
    lat1, lon1 = overflier[sg.START_POSITION_KEY]
    lat2, lon2 = i_element.centre_point()
    overflier_distance = GeoHelper.distance(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2)
    time_to_conflict = overflier_distance/overflier_speed

    climber_time_to_conflict_level = 2016 - 492

    # We expect the time taken for the overflier to reach the conflict location to be
    # (approximately) equal to the time taken for the climber to ascend to the overflier's level.
    assert time_to_conflict == pytest.approx(climber_time_to_conflict_level)

    # We also expect the climber to have reached the conflict location at the same time.
    lat1, lon1 = climber[sg.START_POSITION_KEY]
    lat2, lon2 = i_element.centre_point()
    climber_distance = GeoHelper.distance(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2)

    downtrack_distance = 389237.4376 - 71745.47755 # From the lookup tables (m)

    assert downtrack_distance == pytest.approx(climber_distance)

    print("overflier:")
    print(overflier)

    print("climber:")
    print(climber)