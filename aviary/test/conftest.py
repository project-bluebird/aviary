
import pytest

import pandas
from io import StringIO

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
def cruise_speed_dataframe():
    """Test fixture: a data frame of flight level vs cruise speed, by aircraft type"""

    # Note: these are dummy data for the purpose of unit testing. They are not realistic.
    cruise_speed_data = StringIO("""FL,B743,B744
    0, 100.6111111, 150.9111111
    10, 120.4308586, 170.29811
    100, 140.5212832, 190.8113518
    200, 160.8251279, 210.7354179
    300, 180.5525891, 230.4467388
    360, 200.4457726, 250.4972923
    400, 220.8129835, 270.7942522
    """)
    index_col = "FL"

    return pandas.read_csv(cruise_speed_data, index_col = index_col)


@pytest.fixture(scope="function")
def climb_time_dataframe():
    """Test fixture: a data frame of flight level vs cumulative climb time, by aircraft type"""

    # Note: these are dummy data for the purpose of unit testing. They are not realistic.
    climb_time_data = StringIO("""fl_bins,B743,B744
    400, 2100, 1500
    360, 1500, 900
    300, 900, 700
    200, 500, 400
    100, 200, 150
    10, 20, 10
    0, 0, 0
    """)
    index_col = "fl_bins"

    return pandas.read_csv(climb_time_data, index_col = index_col)


@pytest.fixture(scope="function")
def downtrack_distance_dataframe():
    """Test fixture: a data frame of flight level vs downtrack distance in the climb, by aircraft type"""

    # Note: these are dummy data for the purpose of unit testing. They are not realistic.
    downtrack_distance_data = StringIO("""fl_bins,B743,B744
    400, 400000.4376, 350000.8483
    360, 220000.7294, 230000.4023
    300, 150000.6448, 160000.5534
    200, 70000.47755, 80000.94401
    100, 30000.29687, 31000.19148
    10, 2000.974622, 2100.75499
    0, 0, 0
    """)
    index_col = "fl_bins"

    return pandas.read_csv(downtrack_distance_data, index_col = index_col)
