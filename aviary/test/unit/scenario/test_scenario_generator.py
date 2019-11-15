
import pytest

import os
import json

import aviary.scenario.scenario_generator as sg


@pytest.fixture(params=['i_element', 'x_element'])
def target_sector(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(params=['poisson_scenario', 'overflier_climber_scenario'])
def target_scenario(request):
    return request.getfixturevalue(request.param)


def test_generate_scenario(target_sector, target_scenario):
    seed = 83
    duration = 100

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario)
    scenario = scen_gen.generate_scenario(duration, seed)

    assert sg.START_TIME_KEY in scenario.keys()
    assert sg.AIRCRAFT_KEY in scenario.keys()

    for i in range(10):
        scenario2 = scen_gen.generate_scenario(duration, seed=seed)
        assert scenario == scenario2


def test_serialisation(target_sector, target_scenario):
    seed = 62
    duration = 100

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario)
    scenario = scen_gen.generate_scenario(duration, seed=seed)

    print(scenario[sg.AIRCRAFT_KEY])
    serialised = json.dumps(scenario, sort_keys=True)

    deserialised = json.loads(serialised)

    assert isinstance(deserialised, dict)
    assert sorted(deserialised.keys()) == sorted([sg.AIRCRAFT_KEY, sg.START_TIME_KEY])

    # print(serialised)


def test_write_json_scenario(target_sector, target_scenario):

    scen_gen = sg.ScenarioGenerator(target_sector, target_scenario)

    scenario = {
        sg.START_TIME_KEY: "00:00:00",
        sg.AIRCRAFT_KEY: []
    }

    ## TODO: create actual scenario
    # scenario = scen_gen.generate_scenario(duration, seed=seed)

    filename = "test_scenario"
    here = os.path.abspath(os.path.dirname(__file__))
    scen_gen.write_json_scenario(
        scenario = scenario,
        filename = filename,
        path = here
        )

    assert os.path.exists(
        os.path.join(here, "{}.{}".format(filename, sg.JSON_EXTENSION))
        )
