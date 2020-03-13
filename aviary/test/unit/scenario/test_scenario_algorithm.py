import pytest

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm

from aviary.sector.route import Route

class ConcreteAlgorithm(ScenarioAlgorithm):
    def __init__(self, sector_element, aircraft_types, flight_levels, callsign_prefixes, seed):
        super().__init__(
            sector_element=sector_element,
            aircraft_types=aircraft_types,
            flight_levels=flight_levels,
            callsign_prefixes=callsign_prefixes,
            seed=seed
        )

    def aircraft_generator(self):
        pass


@pytest.fixture(scope="function")
def target(i_element):
    """Test fixture: a scenario algorithm object."""

    return ConcreteAlgorithm(
        sector_element=i_element,
        aircraft_types=["B747", "B777"],
        flight_levels=[200, 240, 280, 320, 360, 400],
        callsign_prefixes=["SPEEDBIRD", "VJ", "DELTA", "EZY"],
        seed=22
    )


@pytest.mark.parametrize(
    "aircraft_types", [[], "B747", [777], ["B747", 747, "B777"], [["B747"]]]
)
def test_aircraft_types_setter(aircraft_types, i_element):
    with pytest.raises(AssertionError):
        ConcreteAlgorithm(
            sector_element=i_element,
            aircraft_types=aircraft_types,
            flight_levels=[200, 240, 280, 320, 360, 400],
            callsign_prefixes=["SPEEDBIRD", "VJ", "DELTA", "EZY"],
            seed=22
        )


@pytest.mark.parametrize(
    "flight_levels", [[], 200, [0], ["200"], [200.0], [205], [200, 215, 230], [[200]]]
)
def test_flight_levels_setter(flight_levels, i_element):
    with pytest.raises(AssertionError):
        ConcreteAlgorithm(
            sector_element=i_element,
            aircraft_types=["B747", "B777"],
            flight_levels=flight_levels,
            callsign_prefixes=["SPEEDBIRD", "VJ", "DELTA", "EZY"],
            seed=22
        )


@pytest.mark.parametrize(
    "callsign_prefixes", [[], "TEST", [123], ["TEST", 123, "OTHER"], [["TEST"]]]
)
def test_callsign_prefixes_setter(callsign_prefixes, i_element):
    with pytest.raises(AssertionError):
        ConcreteAlgorithm(
            sector_element=i_element,
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

    # flight_levels: [200, 240, 280, 320, 360, 400]
    with pytest.raises(ValueError):
        target.flight_level(exclude_lowest=0.4, exclude_highest=0.6)

    # Exclude all except the 280 level
    result = target.flight_level(exclude_lowest=0.39, exclude_highest=0.59)
    assert result == 280

    # Exclude all except the 280 level
    result = target.flight_level(exclude_lowest=0.2, exclude_highest=0.4)
    assert result == 280

    # Exclude up to the 320 level
    result = target.flight_level(exclude_lowest=0.5)
    assert result == 400

def test_route(target):

    result = target.route()
    assert isinstance(result, Route)

    assert result.fix_names()[0] == "E"
    assert result.fix_names()[1] == "D"
    assert result.fix_names()[2] == "C"
    assert result.fix_names()[3] == "B"
    assert result.fix_names()[4] == "A"

    result = target.route()
    assert isinstance(result, Route)

    assert result.fix_names()[0] == "E"
    assert result.fix_names()[1] == "D"
    assert result.fix_names()[2] == "C"
    assert result.fix_names()[3] == "B"
    assert result.fix_names()[4] == "A"

    result = target.route()
    assert isinstance(result, Route)

    assert result.fix_names()[0] == "E"
    assert result.fix_names()[1] == "D"
    assert result.fix_names()[2] == "C"
    assert result.fix_names()[3] == "B"
    assert result.fix_names()[4] == "A"

    result = target.route()
    assert isinstance(result, Route)

    assert result.fix_names()[0] == "A"
    assert result.fix_names()[1] == "B"
    assert result.fix_names()[2] == "C"
    assert result.fix_names()[3] == "D"
    assert result.fix_names()[4] == "E"
