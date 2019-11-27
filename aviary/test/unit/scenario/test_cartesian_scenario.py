
import pytest

import aviary.scenario.cartesian_scenario as cs
import aviary.scenario.scenario_generator as sg

@pytest.fixture(scope="function")
def target(i_element):
    """Test fixture: a Cartesian scenario object."""

    return cs.CartesianScenario(
        sector_element = i_element,
        aircraft_types = ['B747', 'B777'],
        flight_levels = [200, 240, 280, 320, 360, 400],
        callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
        seed = 22)


def test_aircraft_generator(target, i_element):

    ctr = 0
    for x in target.aircraft_generator():

        assert isinstance(x, dict)
        assert sorted(x.keys()) == [sg.CALLSIGN_KEY, sg.CLEARED_FLIGHT_LEVEL_KEY, sg.CURRENT_FLIGHT_LEVEL_KEY,
                                    sg.DEPARTURE_KEY, sg.DESTINATION_KEY, sg.REQUESTED_FLIGHT_LEVEL_KEY,
                                    sg.ROUTE_KEY, sg.AIRCRAFT_TIMEDELTA_KEY, sg.AIRCRAFT_TYPE_KEY]
        assert x[sg.AIRCRAFT_TIMEDELTA_KEY] == 0
        ctr = ctr + 1

    assert ctr == len(target.flight_levels) * len(target.aircraft_types)
