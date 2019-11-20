
import pytest

import os
import json
import time

import aviary.scenario.scenario_generator as sg


@pytest.fixture(params=['i_element', 'x_element'])
def target_sector(request):
    """Test fixture: used to test scenario generation for each sector fixture in params"""
    return request.getfixturevalue(request.param)


@pytest.fixture(params=['poisson_scenario'])
def target_scenario(request):
    """Test fixture: used to test scenario generation for each scenario fixture in params"""
    return request.getfixturevalue(request.param)


def test_generate_scenario(target_sector, target_scenario):
    seed = 83
    duration = 1000

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario)
    scenario = scen_gen.generate_scenario(duration=duration, seed=seed)

    assert sg.START_TIME_KEY in scenario.keys()
    assert sg.AIRCRAFT_KEY in scenario.keys()
    assert isinstance(scenario[sg.START_TIME_KEY], str)
    assert isinstance(scenario[sg.AIRCRAFT_KEY], list)
    assert len(scenario[sg.AIRCRAFT_KEY]) > 0

    total_time = 0
    for aircraft in scenario[sg.AIRCRAFT_KEY]:
        assert sg.START_TIME_KEY in aircraft.keys()
        total_time += aircraft[sg.START_TIME_KEY]
    assert total_time <= duration

    for i in range(10):
        scenario2 = scen_gen.generate_scenario(duration=duration, seed=seed)
        assert scenario == scenario2


def test_serialisation(target_sector, target_scenario):
    seed = 62
    duration = 1000

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario)
    scenario = scen_gen.generate_scenario(duration=duration, seed=seed)
    scenario = scen_gen.serialize_route(scenario)

    serialised = json.dumps(scenario, sort_keys=True)

    deserialised = json.loads(serialised)

    assert isinstance(deserialised, dict)
    assert sorted(deserialised.keys()) == sorted([sg.AIRCRAFT_KEY, sg.START_TIME_KEY])


def test_write_json_scenario(target_sector, target_scenario):
    seed = 76
    duration = 1000

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario)
    scenario = scen_gen.generate_scenario(duration=duration, seed=seed)

    filename = "test_scenario"
    here = os.path.abspath(os.path.dirname(__file__))
    file = scen_gen.write_json_scenario(
        scenario = scenario,
        filename = filename,
        path = here
        )

    assert os.path.exists(file)

    # Clean up.
    os.remove(file)
