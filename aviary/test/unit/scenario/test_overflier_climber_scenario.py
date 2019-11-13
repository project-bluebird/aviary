
import pytest

import aviary.scenario.overflier_climber_scenario as ocs
import aviary.sector.sector_element as se
import aviary.sector.sector_shape as ss
import aviary.scenario.scenario_generator as sg

@pytest.fixture(scope="function")
def target():
    """Test fixture: an overflier-climber scenario object."""

    return ocs.OverflierClimberScenario(aircraft_types = ['B747', 'B777'],
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


# Test the callsign generator method in the base class ScenarioAlgorithm.
# This checks that the **kwargs are correctly passed to the superconstructor.
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


def test_aircraft_generator(target, i_element):

    # Test across multiple generated scenarios.
    for i in range(0, 10):

        ctr = 0
        for x in target.aircraft_generator(i_element):

            assert isinstance(x, dict)
            assert sorted(x.keys()) == [sg.CALLSIGN_KEY, sg.CLEARED_FLIGHT_LEVEL_KEY, sg.CURRENT_FLIGHT_LEVEL_KEY,
                                        sg.DEPARTURE_KEY, sg.DESTINATION_KEY, sg.REQUESTED_FLIGHT_LEVEL_KEY,
                                        sg.ROUTE_KEY,sg.START_TIME_KEY, sg.AIRCRAFT_TYPE_KEY]

            print(x)
            ctr = ctr + 1
            if ctr == 1:
                overflier = x
            if ctr == 2:
                climber = x

        # Check that the scenario contains precisely two aircraft.
        assert ctr == 2

        assert overflier[sg.CURRENT_FLIGHT_LEVEL_KEY] > climber[sg.CURRENT_FLIGHT_LEVEL_KEY]
        assert overflier[sg.CURRENT_FLIGHT_LEVEL_KEY] <= climber[sg.REQUESTED_FLIGHT_LEVEL_KEY]
