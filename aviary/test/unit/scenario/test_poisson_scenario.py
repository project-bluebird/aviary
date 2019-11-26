
import pytest

import aviary.scenario.poisson_scenario as ps
import aviary.sector.sector_element as se
import aviary.sector.sector_shape as ss
import aviary.scenario.scenario_generator as sg

@pytest.fixture(scope="function")
def target():
    """Test fixture: a Poisson scenario object."""

    arrival_rate = 2 / 60 # Two arrivals per minute on average
    return ps.PoissonScenario(arrival_rate = arrival_rate,
                              aircraft_types = ['B747', 'B777'],
                              callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                              flight_levels = [200, 240, 280, 320, 360, 400],
                              seed = 22)


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

    ctr = 0
    N = 200
    interarrival_times = []
    for x in target.aircraft_generator(i_element):

        assert isinstance(x, dict)
        assert sorted(x.keys()) == sorted([sg.CALLSIGN_KEY, sg.CLEARED_FLIGHT_LEVEL_KEY, sg.CURRENT_FLIGHT_LEVEL_KEY,
                                    sg.DEPARTURE_KEY, sg.DESTINATION_KEY, sg.REQUESTED_FLIGHT_LEVEL_KEY,
                                    sg.ROUTE_KEY, sg.AIRCRAFT_TIMEDELTA_KEY, sg.AIRCRAFT_TYPE_KEY,
                                    sg.START_POSITION_KEY])
        assert isinstance(x[sg.START_POSITION_KEY], tuple)
        assert len(x[sg.START_POSITION_KEY]) == 2
        interarrival_times.append(x[sg.AIRCRAFT_TIMEDELTA_KEY])
        if ctr > N:
            break
        ctr = ctr + 1


    # Check the mean interarrival time against the arrival rate parameter (with a 5% tolerance).
    mean = sum(interarrival_times) / N
    assert mean == pytest.approx(1 / target.arrival_rate, rel = 0.05)
