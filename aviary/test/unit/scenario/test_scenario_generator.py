
import pytest

import json

import aviary.scenario.scenario_generator as sg
import aviary.scenario.poisson_scenario as ps
import aviary.sector.sector_shape as ss
import aviary.sector.sector_element as se

@pytest.fixture(scope="function")
def x_target():
    """Test fixture: a scenario generator operating on an X-shaped sector element."""

    name = "HELL"
    origin = (51.5, -0.1275)
    shape = ss.XShape()
    lower_limit = 140
    upper_limit = 400
    x_sector = se.SectorElement(name, origin, shape, lower_limit, upper_limit)

    arrival_rate = 2 / 60 # Two arrivals per minute on average
    seed = 74
    poisson_scenario = ps.PoissonScenario(arrival_rate = arrival_rate, seed=seed)

    return sg.ScenarioGenerator(x_sector, poisson_scenario)


def test_generate_scenario(x_target):
    seed = 50
    duration = 100
    scenario = x_target.generate_scenario(duration, seed=seed)

    assert sg.START_TIME_KEY in scenario.keys()
    assert sg.AIRCRAFT_KEY in scenario.keys()

    for i in range(10):
        scenario2 = x_target.generate_scenario(duration, seed=seed)
        assert scenario == scenario2



# def test_serialisation(x_target):
#
#     arrival_rate = 2 / 60 # Two arrivals per minute on average
#     duration = 1 * 60 # One minute scenario
#     seed = 74
#     result = x_target.poisson_scenario(arrival_rate = arrival_rate, duration = duration, seed = seed)
#
#     serialised = json.dumps(result, sort_keys=True)
#
#     deserialised = json.loads(serialised)
#
#     assert isinstance(deserialised, dict)
#     assert sorted(deserialised.keys()) == sorted([sg.AIRCRAFT_KEY, sg.START_TIME_KEY])

    #print(serialised)

# def test_write_json_scenario(x_target):
#     # Test JSON serialisation to file.
#
#     arrival_rate = 5 / 60 # Five arrivals per minute on average
#     duration = 10 * 60 # Ten minute scenario
#     seed = 74
#     scenario = x_target.poisson_scenario(arrival_rate = arrival_rate, duration = duration, seed = seed)
#
#     x_target.write_json_scenario(scenario = scenario, filename = "x_sector_hell_poisson_scenario")
