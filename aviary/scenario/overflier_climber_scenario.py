"""
Scenario generation algorithm with a single overflier and a single climber.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

# import os.path
import time
import numpy as np

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
import aviary.scenario.scenario_generator as sg

# from json import dump
#
# import aviary.sector.sector_element as se
#
# # JSON keys
# CALLSIGN_KEY = "callsign"
# TYPE_KEY = "type"
# DEPARTURE_KEY = "departure"
# DESTINATION_KEY = "destination"
# START_POSITION_KEY = "startPosition"
# START_TIME_KEY = "startTime"
# CURRENT_FLIGHT_LEVEL_KEY = "currentFlightLevel"
# CLEARED_FLIGHT_LEVEL_KEY = "clearedFlightLevel"
# REQUESTED_FLIGHT_LEVEL_KEY = "requestedFlightLevel"
# ROUTE_KEY = "route"
# ROUTE_ELEMENT_NAME_KEY = "ROUTE_ELEMENT_NAME"
# ROUTE_ELEMENT_TYPE_KEY = "ROUTE_ELEMENT_TYPE"
# ROUTE_ELEMENT_SPEED_KEY = "ROUTE_ELEMENT_SPEED"
# ROUTE_ELEMENT_LEVEL_KEY = "ROUTE_ELEMENT_LEVEL"
# AIRCRAFT_KEY = "aircraft"

class OverflierClimberScenario(ScenarioAlgorithm):
    """An overflier-climber scenario generator for I, X, Y airspace sectors"""


    def __init__(self):

        super().__init__()


    # Overriding abstract method
    def generate_aircraft(self, sector) -> dict:
        """Generates a sequence of aircraft constituting a scenario."""

        # TODO:
        # - expect kwargs for the time to conflict
        # - check for an I sector (for now)
        # -

        yield {
            sg.START_TIME_KEY: 0,
            sg.CALLSIGN_KEY: self.callsign(),
            sg.AIRCRAFT_TYPE_KEY: self.aircraft_type(),
            # TODO: generate random flight levels
            # sg.CURRENT_FLIGHT_LEVEL_KEY: int(current_flight_level),
            # sg.CLEARED_FLIGHT_LEVEL_KEY: int(cleared_flight_level),
            # sg.REQUESTED_FLIGHT_LEVEL_KEY: int(requested_flight_level),
            sg.ROUTE_KEY: self.aircraft_route(route_index, level=requested_flight_level)
        }






