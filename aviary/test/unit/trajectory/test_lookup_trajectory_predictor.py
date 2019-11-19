
import pytest

import aviary.trajectory.lookup_trajectory_predictor as tp


@pytest.fixture(scope="function")
def target(cruise_speed_dataframe, climb_time_dataframe, downtrack_distance_dataframe):
    """Test fixture: a TrajectoryPredictor object"""

    return tp.LookupTrajectoryPredictor(cruise_speed_lookup = cruise_speed_dataframe,
                                  climb_time_lookup = climb_time_dataframe,
                                  downtrack_distance_lookup = downtrack_distance_dataframe)


def test_cruise_speed(target):

    assert target.cruise_speed(flight_level = 200, aircraft_type = 'B744') == 210.7354179
    assert target.cruise_speed(flight_level = 400, aircraft_type = 'B743') == 220.8129835

    with pytest.raises(Exception):
        target.cruise_speed(flight_level = -1, aircraft_type = 'B744')

    with pytest.raises(Exception):
        target.cruise_speed(flight_level = 200, aircraft_type = 'X744')

def test_climb_time_to_level(target):

    assert target.climb_time_to_level(flight_level = 200, aircraft_type = 'B743') == 500
    assert target.climb_time_to_level(flight_level = 360, aircraft_type = 'B744') == 900


def test_downtrack_distance_to_level(target):

    assert target.downtrack_distance_to_level(flight_level = 360, aircraft_type = 'B743') == 220000.7294
    assert target.downtrack_distance_to_level(flight_level = 400, aircraft_type = 'B744') == 350000.8483

