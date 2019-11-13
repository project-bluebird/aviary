
import pytest

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
# import aviary.scenario.scenario_generator as sg
# import aviary.sector.sector_shape as ss
# import aviary.sector.sector_element as se

class ConcreteAlgorithm(ScenarioAlgorithm):

    def __init__(self, aircraft_types, callsign_prefixes, seed):
        super().__init__(aircraft_types = aircraft_types, callsign_prefixes = callsign_prefixes, seed=seed)


    def generate_aircraft(self):
        pass


@pytest.fixture(scope="function")
def target():
    """Test fixture: a scenario algorithm object."""

    return ConcreteAlgorithm(aircraft_types = ['B747', 'B777'],
                             callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                             seed = 22)


def test_aircraft_type(target):

    ctr = 0
    for x in target.aircraft_type():
        if ctr == 0:
            assert x == 'B747'
        if ctr == 1:
            assert x == 'B747'
        if ctr == 2:
            assert x == 'B747'
        if ctr == 3:
            assert x == 'B777'
        if ctr > 3:
            break
        ctr = ctr + 1

def test_callsign(target):

    ctr = 0
    for x in target.callsign():
        if ctr == 0:
            assert x == 'EZY230'
        if ctr == 1:
            assert x == 'SPEEDBIRD215'
        if ctr > 1:
            break
        ctr = ctr + 1

