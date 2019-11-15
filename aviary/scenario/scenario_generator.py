"""
Generates scenarios taking place within I, X, Y airspace sector elements.

Takes a sector element and a scenario generation algorithm. The latter is an object with a 'generate_scenario' method.

"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import os.path
import time

import numpy as np

from json import dump
from shapely.geometry import mapping, point

import aviary.sector.sector_element as se

# CONSTANTS
JSON_EXTENSION = "json"

# JSON keys
CALLSIGN_KEY = "callsign"
AIRCRAFT_TYPE_KEY = "type"
DEPARTURE_KEY = "departure"
DESTINATION_KEY = "destination"
START_POSITION_KEY = "startPosition"
START_TIME_KEY = "startTime"
CURRENT_FLIGHT_LEVEL_KEY = "currentFlightLevel"
CLEARED_FLIGHT_LEVEL_KEY = "clearedFlightLevel"
REQUESTED_FLIGHT_LEVEL_KEY = "requestedFlightLevel"
ROUTE_KEY = "route"
ROUTE_ELEMENT_NAME_KEY = "ROUTE_ELEMENT_NAME"
ROUTE_ELEMENT_TYPE_KEY = "ROUTE_ELEMENT_TYPE"
ROUTE_ELEMENT_SPEED_KEY = "ROUTE_ELEMENT_SPEED"
ROUTE_ELEMENT_LEVEL_KEY = "ROUTE_ELEMENT_LEVEL"
AIRCRAFT_KEY = "aircraft"

class ScenarioGenerator():
    """A scenario generator for I, X, Y airspace sectors"""

    # Default parameters:
    default_scenario_start_time = time.strptime("00:00:00", "%H:%M:%S") # Not to be confused with *aircraft* start time.

    # Fixed parameters:
    # TODO: update these based on the new lookup tables
    departure = "DEP"
    destination = "DEST"

    def __init__(self, sector_element, scenario_algorithm, aircraft_types = None, flight_levels = None, start_time = None):

        self.sector_element = sector_element
        self.scenario_algorithm = scenario_algorithm

        if start_time is None:
            start_time = ScenarioGenerator.default_scenario_start_time
        self.start_time = start_time


    # TODO: add an argument to specify which routes to be included in the scenario.
    def generate_scenario(self, duration, seed = None) -> dict:
        """Generates a list of aircraft creation data whose arrivals in the sector form a Poisson process."""

        self.scenario_algorithm.set_seed(seed)

        # Format the scenario start time.
        start_time = time.strftime("%H:%M:%S", self.start_time)

        ret = { START_TIME_KEY: start_time, AIRCRAFT_KEY: []}

        total_time = 0
        for aircraft in self.scenario_algorithm.aircraft_generator(self.sector_element):
            total_time += aircraft[START_TIME_KEY]
            if total_time > duration:
                return ret
            ret[AIRCRAFT_KEY].append(aircraft)
        return ret


    @staticmethod
    def serialize_route(scenario):
        """Make shapely.geometry.point.Point objects in scenario aircraft route serializable"""

        for aircraft in scenario[AIRCRAFT_KEY]:
            for i, _ in enumerate(aircraft[ROUTE_KEY]):
                aircraft[ROUTE_KEY][i] = tuple(
                    mapping(x) if isinstance(x, point.Point) else x
                    for x in aircraft[ROUTE_KEY][i]
                )
        return scenario


    @staticmethod
    def write_json_scenario(scenario, filename, path="."):
        """Write the JSON scenario object to a file"""

        scenario = ScenarioGenerator.serialize_route(scenario)

        extension = os.path.splitext(filename)[1]
        if extension.upper() != JSON_EXTENSION:
            filename = filename + "." + JSON_EXTENSION

        file = os.path.join(path, filename)


        with open(file, 'w') as f:
            dump(scenario, f, indent = 4)
