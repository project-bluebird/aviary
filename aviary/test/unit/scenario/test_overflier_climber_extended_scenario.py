import pytest

import aviary.scenario.overflier_climber_extended_scenario as oces
import aviary.scenario.scenario_generator as sg
import aviary.trajectory.lookup_trajectory_predictor as tp

from aviary.geo.geo_helper import GeoHelper

THINKING_TIME = 60

@pytest.fixture(scope="function")
def target(cruise_speed_dataframe, climb_time_dataframe, downtrack_distance_dataframe):
    """Test fixture: a simple trajectory predictor object."""

    trajectory_predictor = tp.LookupTrajectoryPredictor(cruise_speed_lookup = cruise_speed_dataframe,
                                                        climb_time_lookup = climb_time_dataframe,
                                                        downtrack_distance_lookup = downtrack_distance_dataframe)

    return oces.OverflierClimberExtendedScenario(trajectory_predictor = trajectory_predictor,
                                                 thinking_time = THINKING_TIME,
                                                 aircraft_types = ['B744', 'B743'],
                                                 callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                                                 flight_levels = [300, 300, 360, 400],
                                                 seed = 223)


def test_constructor(target):

    assert target.low == 300
    assert target.mid == 360
    assert target.high == 400

def test_aircraft_generator(target, i_element):

    # Test across multiple generated scenarios.
    ctr = 0
    for x in target.aircraft_generator(i_element):

        assert isinstance(x, dict)
        assert sorted(x.keys()) == [sg.CALLSIGN_KEY, sg.CLEARED_FLIGHT_LEVEL_KEY, sg.CURRENT_FLIGHT_LEVEL_KEY,
                                    sg.DEPARTURE_KEY, sg.DESTINATION_KEY, sg.REQUESTED_FLIGHT_LEVEL_KEY, sg.ROUTE_KEY,
                                    sg.START_POSITION_KEY, sg.AIRCRAFT_TIMEDELTA_KEY, sg.AIRCRAFT_TYPE_KEY]
        assert isinstance(x[sg.START_POSITION_KEY], tuple)
        assert not isinstance(x[sg.START_POSITION_KEY][0], tuple)
        assert x[sg.START_POSITION_KEY][0] == -0.1275

        ctr = ctr + 1
        if ctr == 1:
            overflier = x
        if ctr == 2:
            climber = x

    # Check that the scenario contains precisely two aircraft.
    assert ctr == 2

    assert overflier[sg.AIRCRAFT_TYPE_KEY] == 'B744'
    assert climber[sg.AIRCRAFT_TYPE_KEY] == 'B743'

    # Flight levels are determined by the low, mid and high instance variables.
    assert overflier[sg.CURRENT_FLIGHT_LEVEL_KEY] == 360
    assert climber[sg.CURRENT_FLIGHT_LEVEL_KEY] == 300
    assert climber[sg.REQUESTED_FLIGHT_LEVEL_KEY] == 400


    # Check that the aircraft will be in conflict at the centre point of the sector
    # (assuming flat cruise during the thinking time followed by the default trajectories).

    overflier_speed = 250.4972923 # From the dummy lookup tables in test/conftest.py (m/s)
    lon1, lat1 = overflier[sg.START_POSITION_KEY]
    lon2, lat2 = i_element.centre_point()
    overflier_distance = GeoHelper.distance(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2)

    time_to_conflict = overflier_distance/overflier_speed

    climber_time_to_conflict_level = THINKING_TIME + 1500 - 900 # From the dummy lookup tables in test/conftest.py (seconds)

    # We expect the time taken for the overflier to reach the conflict location
    # to be (approximately) equal to the computed time taken for the climber to
    # ascend to the overflier's level.
    assert time_to_conflict == pytest.approx(climber_time_to_conflict_level)

    lon1, lat1 = climber[sg.START_POSITION_KEY]
    lon2, lat2 = i_element.centre_point()
    climber_distance = GeoHelper.distance(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2)

    climber_cruise_speed = 180.5525891 # From the dummy lookup tables in test/conftest.py (m/s)
    climber_cruise_distance = THINKING_TIME * climber_cruise_speed
    climber_downtrack_distance = 220000.7294 - 150000.6448 # From the dummy lookup tables in test/conftest.py (m/s)

    # We expect the distance from the climber's start position to the sector
    # centre point to be (approximately) equal to the computed hoizontal distance
    # travelled during the flat cruise followed by the climb.
    assert climber_distance == pytest.approx(climber_cruise_distance + climber_downtrack_distance)
