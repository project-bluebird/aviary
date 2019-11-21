import pytest

import aviary.scenario.overflier_climber_extended_scenario as oces
import aviary.scenario.scenario_generator as sg
import aviary.trajectory.lookup_trajectory_predictor as tp

# from aviary.geo.geo_helper import GeoHelper

@pytest.fixture(scope="function")
def target(cruise_speed_dataframe, climb_time_dataframe, downtrack_distance_dataframe):
    """Test fixture: a simple trajectory predictor object."""

    trajectory_predictor = tp.LookupTrajectoryPredictor(cruise_speed_lookup = cruise_speed_dataframe,
                                                        climb_time_lookup = climb_time_dataframe,
                                                        downtrack_distance_lookup = downtrack_distance_dataframe)

    return oces.OverflierClimberExtendedScenario(trajectory_predictor = trajectory_predictor,
                                                 thinking_time = 60,
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
                                    sg.DEPARTURE_KEY, sg.DESTINATION_KEY, sg.REQUESTED_FLIGHT_LEVEL_KEY,
                                    sg.ROUTE_KEY,
                                    sg.START_POSITION_KEY, sg.AIRCRAFT_TIMEDELTA_KEY, sg.AIRCRAFT_TYPE_KEY]

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
