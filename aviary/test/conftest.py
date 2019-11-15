
import pytest

import aviary.sector.sector_shape as ss
import aviary.sector.sector_element as se
import aviary.scenario.poisson_scenario as ps
import aviary.scenario.overflier_climber_scenario as ocs

@pytest.fixture(scope="function")
def x_element():
    """Test fixture: an X-shaped sector element object."""

    name = "HELL"
    origin = (51.5, -0.1275)
    shape = ss.XShape()
    lower_limit = 140
    upper_limit = 400
    return se.SectorElement(name, origin, shape, lower_limit, upper_limit)


@pytest.fixture(scope="function")
def i_element():
    """Test fixture: an I-shaped sector element object."""

    name = "EARTH"
    origin = (51.5, -0.1275)
    shape = ss.IShape(fix_names=['a', 'b', 'c', 'd', 'e'], route_names = ['up', 'down'])

    lower_limit = 140
    upper_limit = 400
    return se.SectorElement(name, origin, shape, lower_limit, upper_limit)


@pytest.fixture(scope="function")
def y_element():
    """Test fixture: a Y-shaped sector element object."""

    name = "HEAVEN"
    origin = (51.5, -0.1275)
    shape = ss.YShape()

    lower_limit = 140
    upper_limit = 400
    return se.SectorElement(name, origin, shape, lower_limit, upper_limit)


@pytest.fixture(scope="function")
def poisson_scenario():
    """Test fixture: a Poisson scenario object."""

    arrival_rate = 2 / 60 # Two arrivals per minute on average
    return ps.PoissonScenario(arrival_rate = arrival_rate,
                              aircraft_types = ['B747', 'B777'],
                              callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                              flight_levels = [200, 240, 280, 320, 360, 400],
                              seed = 22)


@pytest.fixture(scope="function")
def overflier_climber_scenario():
    """Test fixture: an overflier-climber scenario object."""

    return ocs.OverflierClimberScenario(aircraft_types = ['B747', 'B777'],
                              callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
                              flight_levels = [200, 240, 280, 320, 360, 400],
                              seed = 22)
