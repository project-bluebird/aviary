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

import aviary.sector.sector_element as se

# CONSTANTS
JSON_EXTENSION = "json"

# JSON keys
CALLSIGN_KEY = "callsign"
TYPE_KEY = "type"
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

    # moved to ScenarioAlgorithm:
    # default_aircraft_types = ["B747"] # Types of aircraft available (by default).
    # default_flight_levels = [200, 240, 280, 320, 360, 400]

    # Fixed parameters:
    # TODO: update these based on the new lookup tables
    departure = "DEP"
    destination = "DEST"
    # callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"]

    def __init__(self, sector_element, scenario_algorithm, aircraft_types = None, flight_levels = None, start_time = None):

        self.sector_element = sector_element
        self.scenario_algorithm = scenario_algorithm

        if aircraft_types is None:
            aircraft_types = ScenarioGenerator.default_aircraft_types
        self.aircraft_types = aircraft_types

        if flight_levels is None:
            flight_levels = ScenarioGenerator.default_flight_levels
        self.flight_levels = flight_levels

        if start_time is None:
            start_time = ScenarioGenerator.default_scenario_start_time
        self.start_time = start_time


    # # old:
    # def aircraft_route(self, route_index, level = 0) -> list:
    #     """Represents an aircraft's route as a list of route elements."""
    #
    #     # Get the names of the fixes on the requested route.
    #     fix_names = [fix_items[0] for fix_items in self.sector_element.shape.routes()[route_index]]
    #
    #     # Target flight level is always applied to the last two route elements only.
    #     ret = [self.route_element(fix_name) for fix_name in fix_names[:len(fix_names) - 2]]
    #     ret.extend([self.route_element(fix_name, level) for fix_name in fix_names[-2:]])
    #     return ret


    @staticmethod
    def aircraft_route(self, route, level = 0) -> list:
        """Represents an aircraft's route as a list of route elements with target flight levels."""

        # Get the names of the fixes on the requested route.
        fix_names = [fix_items[0] for fix_items in route]

        # Target flight level is always applied to the last two route elements only.
        ret = [self.route_element(fix_name) for fix_name in fix_names[:len(fix_names) - 2]]
        ret.extend([self.route_element(fix_name, level) for fix_name in fix_names[-2:]])
        return ret


    @staticmethod
    def route_element(self, fix_name, level = 0) -> dict:
        """Returns a dictionary representing a route element.
        Each route element has a name, a type (always 'FIX') and a target flight level."""

        route_element = {
            ROUTE_ELEMENT_NAME_KEY: fix_name,
            ROUTE_ELEMENT_TYPE_KEY: se.FIX_VALUE,
            ROUTE_ELEMENT_LEVEL_KEY: int(level)
        }
        return route_element


    # old:
    # @staticmethod
    # def callsigns(self, n, seed = None):
    #     """Generates a list of up to 900 unique callsigns"""
    #
    #     np.random.seed(seed=seed)
    #     suffixes = np.random.choice(range(0, 1000), size = n, replace = False) # without replacement.
    #     np.random.seed(seed=seed)
    #     prefixes = np.random.choice(ScenarioGenerator.callsign_prefixes, size = n, replace=True)
    #
    #     return [pre + suf for pre, suf in zip(prefixes, [str(suffix) for suffix in suffixes])]
    #
    # moved:
    # @staticmethod
    # def callsign(self, n, seed = None):
    #     """Generates a list of up to 900 unique callsigns"""
    #
    #     np.random.seed(seed=seed)
    #     suffixes = np.random.choice(range(0, 1000), size = n, replace = False) # without replacement.
    #     np.random.seed(seed=seed)
    #     prefixes = np.random.choice(ScenarioGenerator.callsign_prefixes, size = n, replace=True)
    #
    #     return [pre + suf for pre, suf in zip(prefixes, [str(suffix) for suffix in suffixes])]


    @staticmethod
    def write_json_scenario(self, scenario, filename, path="."):
        """Write the JSON scenario object to a file"""

        extension = os.path.splitext(filename)[1]
        if extension.upper() != JSON_EXTENSION:
            filename = filename + "." + JSON_EXTENSION

        file = os.path.join(path, filename)

        with open(file, 'w') as f:
            dump(scenario, f, indent = 4)
