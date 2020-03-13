
import pytest

# tmp testing:
import aviary.scenario.empty_scenario as emps

import aviary.scenario.incremental_ocd_scenario as incs
import aviary.scenario.overflier_climber_scenario as ocs
import aviary.scenario.scenario_generator as sg
import aviary.trajectory.lookup_trajectory_predictor as tp
import aviary.sector.route as sr

from aviary.utils.geo_helper import GeoHelper

@pytest.fixture(scope="function")
def underlying(i_element, cruise_speed_dataframe, climb_time_dataframe, downtrack_distance_dataframe):
    """Test fixture: an overflier-climber scenario to act as the underlying scenario."""

    trajectory_predictor = tp.LookupTrajectoryPredictor(cruise_speed_lookup = cruise_speed_dataframe,
                                                        climb_time_lookup = climb_time_dataframe,
                                                        downtrack_distance_lookup = downtrack_distance_dataframe)

    return ocs.OverflierClimberScenario(sector_element = i_element,
                                        trajectory_predictor = trajectory_predictor,
                                        aircraft_types = ['B744', 'B743'],
                                        callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                                        flight_levels = [200, 400],
                                        seed = 223)

def test_aircraft_generator_from_empty(i_element):

    target = emps.EmptyScenario(sector_element=i_element)

    for i in range(10):

        ctr = 0
        for x in target.aircraft_generator():
            ctr = ctr + 1

        assert ctr == i

        target = incs.IncrementalOcdScenario(
            underlying_scenario=target,
            seed=i
        )

def test_aircraft_generator(underlying):

    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 22,
    )

    # Test across multiple generated scenarios.
    ctr = 0
    for x in target.aircraft_generator():

        assert isinstance(x, dict)
        assert sorted(x.keys()) == [sg.CALLSIGN_KEY, sg.CLEARED_FLIGHT_LEVEL_KEY, sg.CURRENT_FLIGHT_LEVEL_KEY,
                                    sg.DEPARTURE_KEY, sg.DESTINATION_KEY, sg.REQUESTED_FLIGHT_LEVEL_KEY, sg.ROUTE_KEY,
                                    sg.START_POSITION_KEY, sg.AIRCRAFT_TIMEDELTA_KEY, sg.AIRCRAFT_TYPE_KEY]
        # assert isinstance(x[sg.START_POSITION_KEY], tuple)
        # assert not isinstance(x[sg.START_POSITION_KEY][0], tuple)
        # assert x[sg.START_POSITION_KEY][0] == pytest.approx(-0.1275, 10e-8)

        ctr = ctr + 1
        if ctr == 1:
            overflier = x
        if ctr == 2:
            climber = x
        if ctr == 3:
            extra = x

    # Check that the scenario contains precisely three aircraft.
    assert ctr == 3
