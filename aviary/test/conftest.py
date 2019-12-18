
import pytest

import pandas
from io import StringIO

import aviary.sector.sector_shape as ss
import aviary.sector.sector_element as se
import aviary.scenario.poisson_scenario as ps
import aviary.scenario.overflier_climber_scenario as ocs

@pytest.fixture(scope="function")
def i_element():
    """Test fixture: an I-shaped sector element object."""

    type = ss.SectorType.I
    name = "EARTH"
    origin = (-0.1275, 51.5)
    fix_names = ['a', 'b', 'c', 'd', 'e']
    route_names = ['up', 'down']

    lower_limit = 140
    upper_limit = 400
    return se.SectorElement(type = type, name = name, origin = origin, lower_limit = lower_limit, upper_limit = upper_limit,
                            fix_names = fix_names, route_names = route_names)


@pytest.fixture(scope="function")
def x_element():
    """Test fixture: an X-shaped sector element object."""

    type = ss.SectorType.X
    name = "HELL"
    origin = (-0.1275, 51.5)
    lower_limit = 140
    upper_limit = 400
    return se.SectorElement(type = type, name = name, origin = origin, lower_limit = lower_limit, upper_limit = upper_limit)


@pytest.fixture(scope="function")
def y_element():
    """Test fixture: a Y-shaped sector element object."""

    type = ss.SectorType.Y
    name = "HEAVEN"
    origin = (-0.1275, 51.5)

    lower_limit = 140
    upper_limit = 400
    return se.SectorElement(type = type, name = name, origin = origin, lower_limit = lower_limit, upper_limit = upper_limit)


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


@pytest.fixture(scope="function")
def i_sector_geojson():
    """Test fixture: a serialised geoJSON sector,
     obtained by calling geojson.dumps() on an I-shaped SectorElement."""

    return """
    {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"name": "test_sector", "type": "SECTOR", "shape": "I", "origin": [-0.1275, 51.5], "children": {"SECTOR_VOLUME": {"names": ["221395673130872533"]}, "ROUTE": {"names": ["ASCENSION", "FALLEN"]}}}, "geometry": {}}, {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-0.2596527086555938, 51.08375683891335], [-0.26207557205922527, 51.916052359621695], [0.007075572059225247, 51.916052359621695], [0.004652708655593784, 51.08375683891335], [-0.2596527086555938, 51.08375683891335]]]}, "properties": {"name": "221395673130872533", "type": "SECTOR_VOLUME", "lower_limit": 60, "upper_limit": 460, "children": {}}}, {"type": "Feature", "properties": {"name": "ASCENSION", "type": "ROUTE", "children": {"FIX": {"names": ["FIYRE", "EARTH", "WATER", "AIR", "SPIRT"]}}}, "geometry": {"type": "LineString", "coordinates": [[-0.1275, 50.91735552314281], [-0.1275, 51.08383154960228], [-0.1275, 51.49999999999135], [-0.1275, 51.916128869951486], [-0.1275, 52.08256690115545]]}}, {"type": "Feature", "properties": {"name": "FALLEN", "type": "ROUTE", "children": {"FIX": {"names": ["SPIRT", "AIR", "WATER", "EARTH", "FIYRE"]}}}, "geometry": {"type": "LineString", "coordinates": [[-0.1275, 52.08256690115545], [-0.1275, 51.916128869951486], [-0.1275, 51.49999999999135], [-0.1275, 51.08383154960228], [-0.1275, 50.91735552314281]]}}, {"type": "Feature", "properties": {"name": "SPIRT", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 52.08256690115545]}}, {"type": "Feature", "properties": {"name": "AIR", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.916128869951486]}}, {"type": "Feature", "properties": {"name": "WATER", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.49999999999135]}}, {"type": "Feature", "properties": {"name": "EARTH", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.08383154960228]}}, {"type": "Feature", "properties": {"name": "FIYRE", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 50.91735552314281]}}]}
    """

@pytest.fixture(scope="function")
def overflier_climber_scenario_json():
    """Test fixture: a serialised JSON scenario,
    obtained by calling json.dumps() on an overflier_climber scenario in an I-shaped sector generated using ScenarioGenerator.
    """

    return """
    {"startTime": "00:00:00", "aircraft": [{"timedelta": 0, "startPosition": [-0.1275, 49.39138473926763], "callsign": "VJ159", "type": "A346", "departure": "DEP", "destination": "DEST", "currentFlightLevel": 400, "clearedFlightLevel": 400, "requestedFlightLevel": 400, "route": [{"fixName": "FIYRE", "geometry": {"type": "Point", "coordinates": [-0.1275, 50.91735552314281]}}, {"fixName": "EARTH", "geometry": {"type": "Point", "coordinates": [-0.1275, 51.08383154960228]}}, {"fixName": "WATER", "geometry": {"type": "Point", "coordinates": [-0.1275, 51.49999999999135]}}, {"fixName": "AIR", "geometry": {"type": "Point", "coordinates": [-0.1275, 51.916128869951486]}}, {"fixName": "SPIRT", "geometry": {"type": "Point", "coordinates": [-0.1275, 52.08256690115545]}}], "startTime": "00:00:00"}, {"timedelta": 0, "startPosition": [-0.1275, 53.57478111513239], "callsign": "VJ405", "type": "B77W", "departure": "DEST", "destination": "DEP", "currentFlightLevel": 200, "clearedFlightLevel": 200, "requestedFlightLevel": 400, "route": [{"fixName": "SPIRT", "geometry": {"type": "Point", "coordinates": [-0.1275, 52.08256690115545]}}, {"fixName": "AIR", "geometry": {"type": "Point", "coordinates": [-0.1275, 51.916128869951486]}}, {"fixName": "WATER", "geometry": {"type": "Point", "coordinates": [-0.1275, 51.49999999999135]}}, {"fixName": "EARTH", "geometry": {"type": "Point", "coordinates": [-0.1275, 51.08383154960228]}}, {"fixName": "FIYRE", "geometry": {"type": "Point", "coordinates": [-0.1275, 50.91735552314281]}}], "startTime": "00:00:00"}]}
    """


