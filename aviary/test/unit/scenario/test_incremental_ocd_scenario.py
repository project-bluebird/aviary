
import pytest

import numpy as np

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

    # Start with an empty scenario.
    target = emps.EmptyScenario(sector_element=i_element)

    for i in range(10):

        ctr = 0
        for x in target.aircraft_generator():
            ctr = ctr + 1

        assert ctr == i

        # Incrementally add one aircraft at a time.
        target = incs.IncrementalOcdScenario(
            underlying_scenario=target,
            seed=i
        )


def test_choose_route_segment(i_element, underlying):

    # Test with five route segments.
    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 22,
        start_position_distribution = np.array([1, 0, 0, 0, 0]),
    )

    route = target.route
    fixes = route.fix_points()

    # Test the _pre_fix_index method at the same time.
    assert target._pre_fix_index()[0] == 0

    result = target.choose_route_segment()

    # The first Point in the result should coincide with the fix with index 0.
    assert result[0].x == fixes[0].x
    assert result[0].y == pytest.approx(fixes[0].y, 1e-10)

    # The second Point in the result should be one fifth of the distance along the straight-line route.
    expected_distance = (1/5) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)
    assert result[1].x == expected_point.x
    assert result[1].y == expected_point.y

    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 22,
        start_position_distribution = np.array([0, 1, 0, 0, 0]),
    )

    # Test the _pre_fix_index method at the same time.
    assert target._pre_fix_index()[0] == 1

    result = target.choose_route_segment()

    # The first Point in the result should be one fifth of the distance along the straight-line route.
    expected_distance = (1/5) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)
    assert result[0].x == expected_point.x
    assert result[0].y == expected_point.y

    # The second Point in the result should be one two fifths of the distance along the straight-line route.
    expected_distance = (2/5) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)
    assert result[1].x == expected_point.x
    assert result[1].y == pytest.approx(expected_point.y, 1e-10)

    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 22,
        start_position_distribution = np.array([0, 0, 0, 0, 1]),
    )

    # Test the _pre_fix_index method at the same time.
    assert target._pre_fix_index()[0] == 2 # Note: this means the central fix is the one before the last fifth segment.

    result = target.choose_route_segment()

    # The first Point in the result should be four fifths of the distance along the straight-line route.
    expected_distance = (4/5) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)

    assert result[0].x == expected_point.x
    assert result[0].y == pytest.approx(expected_point.y, 1e-10)

    # The second Point in the result should coincide with the fix with index 4 (the end of the route).
    assert result[1].x == fixes[4].x
    assert result[1].y == fixes[4].y

    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 22,
        start_position_distribution = np.array([0, 1/2, 0, 1/2, 0]),
    )

    # Test the _pre_fix_index method at the same time.
    assert target._pre_fix_index()[0] == 1 # With this seed, the earlier segment is selected

    result = target.choose_route_segment()

    # The first Point in the result should be one fifth of the distance along the straight-line route.
    expected_distance = (1/5) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)
    assert result[0].x == expected_point.x
    assert result[0].y == expected_point.y

    # The second Point in the result should be one two fifths of the distance along the straight-line route.
    expected_distance = (2/5) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)
    assert result[1].x == expected_point.x
    assert result[1].y == pytest.approx(expected_point.y, 1e-10)

    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 28,
        start_position_distribution = np.array([0, 1/2, 0, 1/2, 0]),
    )

    # Test the _pre_fix_index method at the same time.
    # With the different seed, the route is the same but the later segment is selected:
    assert target.route.fix_names() == route.fix_names()
    assert target._pre_fix_index()[0] == 2

    result = target.choose_route_segment()

    # The first Point in the result should be three fifths of the distance along the straight-line route.
    expected_distance = (3/5) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)

    assert result[0].x == expected_point.x
    assert result[0].y == pytest.approx(expected_point.y, 1e-10)

    # The second Point in the result should be four fifths of the distance along the straight-line route.
    expected_distance = (4/5) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)

    assert result[1].x == expected_point.x
    assert result[1].y == pytest.approx(expected_point.y, 1e-10)


def test_choose_start_position(underlying):

    #
    # Test with discrete start positions.
    #

    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 22,
        start_position_distribution = np.array([0, 1]),
        discrete_start_positions=True
    )

    route = target.route
    fixes = route.fix_points()

    result = target.choose_start_position()

    # The start position should be half way along the straight-line route.
    expected_distance = (1/2) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)

    assert result.x == expected_point.x
    assert result.y == pytest.approx(expected_point.y, 1e-10)

    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 22,
        start_position_distribution = np.array([1, 0]),
        discrete_start_positions=True
    )

    result = target.choose_start_position()

    # The start position should coincide with the fix with index 0.
    assert result.x == fixes[0].x
    assert result.y == pytest.approx(fixes[0].y, 1e-10)

    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 22,
        start_position_distribution = np.array([0, 0, 0, 0, 1, 0, 0]),
        discrete_start_positions=True
    )

    result = target.choose_start_position()

    # The start position should be four sevenths of the way along the straight-line route.
    expected_distance = (4/7) * GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)

    assert result.x == expected_point.x
    assert result.y == pytest.approx(expected_point.y, 1e-10)

    #
    # Test with continuous start positions.
    #

    target = incs.IncrementalOcdScenario(
        underlying_scenario=underlying,
        seed = 22,
        start_position_distribution = np.array([0, 0, 0, 0, 1, 0, 0]),
        discrete_start_positions=False
    )

    result = target.choose_start_position()

    # The start position should be on the straight-line route.
    assert result.x == fixes[0].x
    assert result.y >= fixes[0].y
    assert result.x == fixes[4].x
    assert result.y <= fixes[4].y

    # The start position should be between four and five sevenths of the way along the straight-line route.
    route_span = GeoHelper.distance(lat1=fixes[0].y, lon1=fixes[0].x,
                                           lat2=fixes[4].y, lon2=fixes[4].x)
    expected_distance = (4.5/7) * route_span
    expected_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=expected_distance)

    # The margin of uncertainty is the length on one route segment: one seventh of the span of the route.
    margin = route_span/7

    assert GeoHelper.distance(lat1=expected_point.y, lon1=expected_point.x,
                              lat2=result.y, lon2=result.x) < margin/2

    lower_bound_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=(4/7) * route_span)
    upper_bound_point = GeoHelper.waypoint_location(lat1=fixes[0].y, lon1=fixes[0].x,
                                                 lat2=fixes[4].y, lon2=fixes[4].x,
                                                 distance_m=(5/7) * route_span)

    assert GeoHelper.distance(lat1=lower_bound_point.y, lon1=lower_bound_point.x,
                              lat2=result.y, lon2=result.x) < margin
    assert GeoHelper.distance(lat1=upper_bound_point.y, lon1=upper_bound_point.x,
                              lat2=result.y, lon2=result.x) < margin


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

        ctr = ctr + 1

    # Check that the scenario contains precisely three aircraft.
    assert ctr == 3


def test_incremental_aircraft_generator(underlying):

    target = underlying

    count_overfliers = 0
    count_climbers = 0
    count_descenders = 0

    N = 30
    for i in range(N):

        ctr = 0
        for x in target.aircraft_generator():

            assert isinstance(x, dict)
            assert sorted(x.keys()) == [sg.CALLSIGN_KEY, sg.CLEARED_FLIGHT_LEVEL_KEY, sg.CURRENT_FLIGHT_LEVEL_KEY,
                                        sg.DEPARTURE_KEY, sg.DESTINATION_KEY, sg.REQUESTED_FLIGHT_LEVEL_KEY, sg.ROUTE_KEY,
                                        sg.START_POSITION_KEY, sg.AIRCRAFT_TIMEDELTA_KEY, sg.AIRCRAFT_TYPE_KEY]

            # On the last pass through the loop, keep track of the number of aircraft of each phase.
            if i == N - 1:
                if x[sg.CURRENT_FLIGHT_LEVEL_KEY] == x[sg.REQUESTED_FLIGHT_LEVEL_KEY]:
                    count_overfliers += 1
                if x[sg.CURRENT_FLIGHT_LEVEL_KEY] < x[sg.REQUESTED_FLIGHT_LEVEL_KEY]:
                    count_climbers += 1
                if x[sg.CURRENT_FLIGHT_LEVEL_KEY] > x[sg.REQUESTED_FLIGHT_LEVEL_KEY]:
                    count_descenders += 1

            ctr += 1

        # Two aircraft in the underlying scenario, plus i (i.e. the number of incremental additions)
        assert ctr == i + 2

        # Incrementally add one aircraft at a time.
        target = incs.IncrementalOcdScenario(
            underlying_scenario=target,
            seed=i,
            overflier_prob=1/3,
            climber_prob=1/3,
            descender_prob=1/3,
        )

    # The target is now a scenario with N + 1 aircraft.
    assert count_overfliers + count_climbers + count_descenders == (N - 1) + 2

    assert count_overfliers == pytest.approx(N/3, rel=0.1)
    assert count_climbers == pytest.approx(N/3, rel=0.1)
    assert count_descenders == pytest.approx(N/3, rel=0.1)