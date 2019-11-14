
import pytest

import os
import json

import aviary.scenario.scenario_generator as sg


@pytest.fixture(scope="function")
def x_target(x_element, poisson_scenario):
    return sg.ScenarioGenerator(x_element, poisson_scenario)


@pytest.fixture(scope="function")
def i_target(i_element, poisson_scenario):
    return sg.ScenarioGenerator(i_element, poisson_scenario)


def test_generate_scenario(x_target, i_target):
    seed = 83
    duration = 100
    i_scenario = i_target.generate_scenario(duration, seed=seed)
    x_scenario = x_target.generate_scenario(duration, seed=seed)

    assert sg.START_TIME_KEY in i_scenario.keys()
    assert sg.START_TIME_KEY in x_scenario.keys()
    assert sg.AIRCRAFT_KEY in i_scenario.keys()
    assert sg.AIRCRAFT_KEY in x_scenario.keys()

    for i in range(10):
        i_scenario2 = i_target.generate_scenario(duration, seed=seed)
        x_scenario2 = x_target.generate_scenario(duration, seed=seed)
        assert i_scenario == i_scenario2
        assert x_scenario == x_scenario2


def test_serialisation(x_target):
    seed = 62
    duration = 100
    scenario = x_target.generate_scenario(duration, seed=seed)

    serialised = json.dumps(scenario, sort_keys=True)

    deserialised = json.loads(serialised)

    assert isinstance(deserialised, dict)
    assert sorted(deserialised.keys()) == sorted([sg.AIRCRAFT_KEY, sg.START_TIME_KEY])

    # print(serialised)


def test_write_json_scenario(x_target):

    scenario = {
        sg.START_TIME_KEY: "00:00:00",
        sg.AIRCRAFT_KEY: []
    }

    filename = "x_sector_hell_poisson_scenario"
    here = os.path.abspath(os.path.dirname(__file__))
    x_target.write_json_scenario(
        scenario = scenario,
        filename = filename,
        path = here
        )

    assert os.path.exists(
        os.path.join(here, "{}.{}".format(filename, sg.JSON_EXTENSION))
        )
