
import pytest

import aviary.scenario.overflier_climber_scenario as ocs
import aviary.scenario.scenario_generator as sg
import aviary.trajectory.lookup_trajectory_predictor as tp
import aviary.sector.route as sr

from aviary.geo.geo_helper import GeoHelper

@pytest.fixture(scope="function")
def target(cruise_speed_dataframe, climb_time_dataframe, downtrack_distance_dataframe):
    """Test fixture: a simple trajectory predictor object."""

    trajectory_predictor = tp.LookupTrajectoryPredictor(cruise_speed_lookup = cruise_speed_dataframe,
                                                        climb_time_lookup = climb_time_dataframe,
                                                        downtrack_distance_lookup = downtrack_distance_dataframe)



    return ocs.OverflierClimberScenario(trajectory_predictor = trajectory_predictor,
                                        aircraft_types = ['B744', 'B743'],
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

    assert overflier[sg.CURRENT_FLIGHT_LEVEL_KEY] == 400
    assert climber[sg.CURRENT_FLIGHT_LEVEL_KEY] == 200
    assert climber[sg.REQUESTED_FLIGHT_LEVEL_KEY] == 400

    # Check that the aircraft will be in conflict at the centre point of the sector (assuming default trajectories).

    overflier_speed = 270.7942522 # From the dummy lookup tables in test/conftest.py (m/s)
    lon1, lat1 = overflier[sg.START_POSITION_KEY]
    lat2, lon2 = i_element.centre_point()
    overflier_distance = GeoHelper.distance(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2)

    time_to_conflict = overflier_distance/overflier_speed

    climber_time_to_conflict_level = 2100 - 500 # From the dummy lookup tables in test/conftest.py (seconds)

    # We expect the time taken for the overflier to reach the conflict location
    # to be (approximately) equal to the computed time taken for the climber to
    # ascend to the overflier's level.
    assert time_to_conflict == pytest.approx(climber_time_to_conflict_level)

    # We also expect the climber to have reached the conflict location at the same time.
    lon1, lat1 = climber[sg.START_POSITION_KEY]
    lat2, lon2 = i_element.centre_point()
    climber_distance = GeoHelper.distance(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2)

    downtrack_distance = 400000.4376 - 70000.47755 # From the dummy lookup tables in test/conftest.py (metres)

    # We expect the horizontal distance travelled by the climber during the
    # climb from its inital flight level to the conflict level to be
    # (approximately) equal to the computed distance travelled by the climber.
    assert downtrack_distance == pytest.approx(climber_distance)

    # Check the aircraft routes.

    # Compare the distance between the fixes with the distance travelled by the overflier to the conflict point.
    lat1, lon1 = i_element.fix_location(fix_name = "A")
    lat2, lon2 = i_element.centre_point()
    assert overflier_distance > GeoHelper.distance(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2)

    # At the start of the scenario the overflier has not yet reached the first fix (A).
    assert [i[sr.FIX_NAME_KEY] for i in overflier[sg.ROUTE_KEY]] == ['A', 'B', 'C', 'D', 'E']

    # Check the route assigned to the climber.

    # Compare the distance between the fixes with the distance travelled by the climber to the conflict point.
    lat1, lon1 = i_element.fix_location(fix_name = "E")
    lat2, lon2 = i_element.centre_point()
    assert climber_distance > GeoHelper.distance(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2)

    # At the start of the scenario the climber has not yet reached the first fix (E).
    assert [i[sr.FIX_NAME_KEY] for i in climber[sg.ROUTE_KEY]] == ['E', 'D', 'C', 'B', 'A']