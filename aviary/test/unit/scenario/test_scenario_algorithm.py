
import pytest

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
# import aviary.scenario.scenario_generator as sg
import aviary.sector.sector_shape as ss
import aviary.sector.sector_element as se

class ConcreteAlgorithm(ScenarioAlgorithm):

    def __init__(self, aircraft_types, callsign_prefixes, flight_levels, seed):
        super().__init__(aircraft_types = aircraft_types, callsign_prefixes = callsign_prefixes, flight_levels = flight_levels, seed=seed)


    def aircraft_generator(self):
        pass


@pytest.fixture(scope="function")
def target():
    """Test fixture: a scenario algorithm object."""

    return ConcreteAlgorithm(aircraft_types = ['B747', 'B777'],
                             callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                             flight_levels = [200, 240, 280, 320, 360, 400],
                             seed = 22)


@pytest.fixture(scope="function")
def i_element():

    name = "EARTH"
    origin = (51.5, -0.1275)
    shape = ss.IShape(fix_names=['a', 'b', 'c', 'd', 'e'], route_names = ['up', 'down'])

    lower_limit = 140
    upper_limit = 400
    return se.SectorElement(name, origin, shape, lower_limit, upper_limit)


def test_callsign_generator(target):

    ctr = 0
    for x in target.callsign_generator():
        if ctr == 0:
            assert x == 'EZY230'
        if ctr == 1:
            assert x == 'SPEEDBIRD215'
        if ctr > 1:
            break
        ctr = ctr + 1


def test_aircraft_type_generator(target):

    ctr = 0
    for x in target.aircraft_type_generator():
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

def test_flight_level_generator(target):

    ctr = 0
    for x in target.flight_level_generator():
        if ctr == 0:
            assert x == 240
        if ctr == 1:
            assert x == 240
        if ctr == 2:
            assert x == 200
        if ctr == 3:
            assert x == 360
        if ctr > 3:
            break
        ctr = ctr + 1


def test_route_generator(target, i_element):

    # TODO: make this a real test

    ctr = 0
    for x in target.route_generator(sector = i_element):
        if ctr == 0:
            assert isinstance(x, list)
        if ctr == 1:
            assert isinstance(x, list)
        if ctr == 2:
            assert isinstance(x, list)
        if ctr == 3:
            assert isinstance(x, list)
        if ctr > 3:
            break
        ctr = ctr + 1