
import pytest

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
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


def test_aircraft_type(target):

    result = target.aircraft_type()
    assert result == 'B747'

    result = target.aircraft_type()
    assert result == 'B747'

    result = target.aircraft_type()
    assert result == 'B747'

    result = target.aircraft_type()
    assert result == 'B777'


def test_flight_level(target):

    result =  target.flight_level()
    assert result == 240

    result =  target.flight_level()
    assert result == 240

    result =  target.flight_level()
    assert result == 200


def test_route(target, i_element):

    result = target.route(sector = i_element)
    assert isinstance(result, list)

    assert result[0][0] == 'E'
    assert result[1][0] == 'D'
    assert result[2][0] == 'C'
    assert result[3][0] == 'B'
    assert result[4][0] == 'A'

    result = target.route(sector = i_element)
    assert isinstance(result, list)

    assert result[0][0] == 'E'
    assert result[1][0] == 'D'
    assert result[2][0] == 'C'
    assert result[3][0] == 'B'
    assert result[4][0] == 'A'

    result = target.route(sector = i_element)
    assert isinstance(result, list)

    assert result[0][0] == 'E'
    assert result[1][0] == 'D'
    assert result[2][0] == 'C'
    assert result[3][0] == 'B'
    assert result[4][0] == 'A'

    result = target.route(sector = i_element)
    assert isinstance(result, list)

    assert result[0][0] == 'A'
    assert result[1][0] == 'B'
    assert result[2][0] == 'C'
    assert result[3][0] == 'D'
    assert result[4][0] == 'E'
