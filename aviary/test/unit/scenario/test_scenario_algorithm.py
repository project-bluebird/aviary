import pytest

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm

from aviary.sector.route import Route

class ConcreteAlgorithm(ScenarioAlgorithm):
    def __init__(self, aircraft_types, flight_levels, callsign_prefixes, seed):
        super().__init__(
            aircraft_types=aircraft_types,
            flight_levels=flight_levels,
            callsign_prefixes=callsign_prefixes,
            seed=seed
        )

    def aircraft_generator(self):
        pass


@pytest.fixture(scope="function")
def target():
    """Test fixture: a scenario algorithm object."""

    return ConcreteAlgorithm(
        aircraft_types=["B747", "B777"],
        flight_levels=[200, 240, 280, 320, 360, 400],
        callsign_prefixes=["SPEEDBIRD", "VJ", "DELTA", "EZY"],
        seed=22
    )


@pytest.mark.parametrize(
    "aircraft_types", [[], "B747", [777], ["B747", 747, "B777"], [["B747"]]]
)
def test_aircraft_types_setter(aircraft_types):
    with pytest.raises(AssertionError):
        ConcreteAlgorithm(
            aircraft_types=aircraft_types,
            flight_levels=[200, 240, 280, 320, 360, 400],
            callsign_prefixes=["SPEEDBIRD", "VJ", "DELTA", "EZY"],
            seed=22
        )


@pytest.mark.parametrize(
    "flight_levels", [[], 200, [0], ["200"], [200.0], [205], [200, 215, 230], [[200]]]
)
def test_flight_levels_setter(flight_levels):
    with pytest.raises(AssertionError):
        ConcreteAlgorithm(
            aircraft_types=["B747", "B777"],
            flight_levels=flight_levels,
            callsign_prefixes=["SPEEDBIRD", "VJ", "DELTA", "EZY"],
            seed=22
        )


@pytest.mark.parametrize(
    "callsign_prefixes", [[], "TEST", [123], ["TEST", 123, "OTHER"], [["TEST"]]]
)
def test_callsign_prefixes_setter(callsign_prefixes):
    with pytest.raises(AssertionError):
        ConcreteAlgorithm(
            aircraft_types=["B747", "B777"],
            flight_levels=[200, 240, 280, 320, 360, 400],
            callsign_prefixes=callsign_prefixes,
            seed=22
        )


def test_callsign_generator(target):

    ctr = 0
    for x in target.callsign_generator():
        if ctr == 0:
            assert x == "EZY230"
        if ctr == 1:
            assert x == "SPEEDBIRD215"
        if ctr > 1:
            break
        ctr = ctr + 1


def test_aircraft_type(target):

    result = target.aircraft_type()
    assert result == "B747"

    result = target.aircraft_type()
    assert result == "B747"

    result = target.aircraft_type()
    assert result == "B747"

    result = target.aircraft_type()
    assert result == "B777"


def test_flight_level(target):

    result = target.flight_level()
    assert result == 240

    result = target.flight_level()
    assert result == 240

    result = target.flight_level()
    assert result == 200


def test_route(target, i_element):

    result = target.route(sector=i_element)
    assert isinstance(result, Route)

    assert result.fix_names()[0] == "E"
    assert result.fix_names()[1] == "D"
    assert result.fix_names()[2] == "C"
    assert result.fix_names()[3] == "B"
    assert result.fix_names()[4] == "A"

    result = target.route(sector=i_element)
    assert isinstance(result, Route)

    assert result.fix_names()[0] == "E"
    assert result.fix_names()[1] == "D"
    assert result.fix_names()[2] == "C"
    assert result.fix_names()[3] == "B"
    assert result.fix_names()[4] == "A"

    result = target.route(sector=i_element)
    assert isinstance(result, Route)

    assert result.fix_names()[0] == "E"
    assert result.fix_names()[1] == "D"
    assert result.fix_names()[2] == "C"
    assert result.fix_names()[3] == "B"
    assert result.fix_names()[4] == "A"

    result = target.route(sector=i_element)
    assert isinstance(result, Route)

    assert result.fix_names()[0] == "A"
    assert result.fix_names()[1] == "B"
    assert result.fix_names()[2] == "C"
    assert result.fix_names()[3] == "D"
    assert result.fix_names()[4] == "E"
