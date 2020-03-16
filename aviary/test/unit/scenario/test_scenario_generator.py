
import pytest

import os
from datetime import datetime

import aviary.scenario.poisson_scenario as ps
import aviary.scenario.scenario_generator as sg


@pytest.fixture(params=["i_element", "x_element", "y_element"])
def target_sector(request):
    """Test fixture: used to test scenario generation for each sector fixture in params"""
    return request.getfixturevalue(request.param)


def test_generate_scenario(target_sector):
    seed = 83
    duration = 1000

    arrival_rate = 2 / 60 # Two arrivals per minute on average
    target_scenario = ps.PoissonScenario(sector_element = target_sector,
                              arrival_rate = arrival_rate,
                              aircraft_types = ['B747', 'B777'],
                              callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                              flight_levels = [200, 240, 280, 320, 360, 400],
                              seed = 22)

    scen_gen = sg.ScenarioGenerator(target_scenario)
    scenario = scen_gen.generate_scenario(duration=duration)

    assert sg.START_TIME_KEY in scenario.keys()
    assert sg.AIRCRAFT_KEY in scenario.keys()
    assert isinstance(scenario[sg.START_TIME_KEY], str)
    assert isinstance(scenario[sg.AIRCRAFT_KEY], list)
    assert len(scenario[sg.AIRCRAFT_KEY]) > 0

    for aircraft in scenario[sg.AIRCRAFT_KEY]:
        assert sorted(aircraft.keys()) == sorted(
            [
                sg.CALLSIGN_KEY,
                sg.CLEARED_FLIGHT_LEVEL_KEY,
                sg.CURRENT_FLIGHT_LEVEL_KEY,
                sg.DEPARTURE_KEY,
                sg.DESTINATION_KEY,
                sg.REQUESTED_FLIGHT_LEVEL_KEY,
                sg.ROUTE_KEY,
                sg.AIRCRAFT_TIMEDELTA_KEY,
                sg.AIRCRAFT_TYPE_KEY,
                sg.START_POSITION_KEY,
                sg.START_TIME_KEY
            ]
        )

    total_time = 0
    for aircraft in scenario[sg.AIRCRAFT_KEY]:
        assert sg.START_TIME_KEY in aircraft.keys()
        total_time += aircraft[sg.AIRCRAFT_TIMEDELTA_KEY]
    assert total_time <= duration

    # Check that scenario's generated with the same random seed are identical.
    for i in range(1):
        scenario2 = scen_gen.generate_scenario(duration=duration)
        assert scenario == scenario2


def test_generate_scenario_with_start_time(target_sector):

    seed = 83
    duration = 1000
    scenario_start_time = datetime.strptime("12:05:42", "%H:%M:%S")

    arrival_rate = 2 / 60 # Two arrivals per minute on average
    target_scenario = ps.PoissonScenario(sector_element = target_sector,
                              arrival_rate = arrival_rate,
                              aircraft_types = ['B747', 'B777'],
                              callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                              flight_levels = [200, 240, 280, 320, 360, 400],
                              seed = seed)

    scen_gen = sg.ScenarioGenerator(target_scenario, scenario_start_time)
    scenario = scen_gen.generate_scenario(duration=duration)

    total_time = 0
    for aircraft in scenario[sg.AIRCRAFT_KEY]:
        assert sg.AIRCRAFT_TIMEDELTA_KEY in aircraft.keys()
        assert (
            datetime.strptime(aircraft[sg.START_TIME_KEY], "%H:%M:%S")
            > scenario_start_time
        )
        inferred_aircraft_timedelta = (
            datetime.strptime(aircraft[sg.START_TIME_KEY], "%H:%M:%S")
            - scenario_start_time
        ).total_seconds()
        assert inferred_aircraft_timedelta == int(aircraft[sg.AIRCRAFT_TIMEDELTA_KEY])
        total_time += aircraft[sg.AIRCRAFT_TIMEDELTA_KEY]

    assert total_time <= duration


def test_write_json_scenario(target_sector):
    seed = 76
    duration = 1000

    arrival_rate = 2 / 60 # Two arrivals per minute on average
    target_scenario = ps.PoissonScenario(sector_element = target_sector,
                              arrival_rate = arrival_rate,
                              aircraft_types = ['B747', 'B777'],
                              callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                              flight_levels = [200, 240, 280, 320, 360, 400],
                              seed = 22)

    scen_gen = sg.ScenarioGenerator(target_scenario)
    scenario = scen_gen.generate_scenario(duration=duration)

    filename = "test_scenario"
    here = os.path.abspath(os.path.dirname(__file__))
    file = scen_gen.write_json_scenario(scenario=scenario, filename=filename, path=here)

    assert os.path.exists(file)

    # Clean up.
    os.remove(file)
