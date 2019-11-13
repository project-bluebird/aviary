"""
Scenario generation algorithm with Poisson aircraft arrivals.
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

class PoissonScenario(ScenarioAlgorithm):
    """A Poisson scenario generator for I, X, Y airspace sectors"""


    def __init__(self, arrival_rate, seed = None):

        super().__init__(seed = seed)
        self.arrival_rate = arrival_rate


    # Overriding abstract method
    def generate_aircraft(self, sector) -> dict:
        """Generates a sequence of aircraft constituting a scenario."""

        while True:
            yield {
                sg.START_TIME_KEY: np.random.exponential(scale=1/self.arrival_rate),
                sg.CALLSIGN_KEY: self.callsign(),
                sg.AIRCRAFT_TYPE_KEY: self.aircraft_type(),
                # TODO: generate random flight levels
                # sg.CURRENT_FLIGHT_LEVEL_KEY: int(current_flight_level),
                # sg.CLEARED_FLIGHT_LEVEL_KEY: int(cleared_flight_level),
                # sg.REQUESTED_FLIGHT_LEVEL_KEY: int(requested_flight_level),
                sg.ROUTE_KEY: self.aircraft_route(route_index, level=requested_flight_level)
            }

    # TODO: move this back to scenario_generator:
    # TODO: add an argument to specify which routes to be included in the scenario.
    def generate_scenario(self, duration, seed = None) -> dict:
        """Generates a list of aircraft creation data whose arrivals in the sector form a Poisson process."""

        # Format the scenario start time.
        start_time = time.strftime("%H:%M:%S", self.start_time)

        interarrival_times = self.exponential_interarrival_times(arrival_rate = arrival_rate, duration = duration, seed = seed)

        n = len(interarrival_times)
        callsigns = self.callsigns(n = n, seed = seed)
        np.random.seed(seed=seed)
        aircraft_types = np.random.choice(self.aircraft_types, n, replace=True)

        # Randomly select from the available routes.
        np.random.seed(seed=seed)
        route_indices = np.random.choice(range(0, len(self.sector_element.shape.routes())), size = n, replace = True)  # With replacement.

        # Infer the aircraft start times from the interarrival times.
        # TODO: should these be added to the scenario start time?
        start_times = np.around(np.cumsum(interarrival_times)).astype(int)

        # Randomly select from the available flight levels to get the current level for each aircraft.
        np.random.seed(seed=seed)
        current_flight_levels = np.random.choice(self.flight_levels, size = n, replace = True)

        # Assume cleared flight level is always equal to current flight level.
        cleared_flight_levels = current_flight_levels
        np.random.seed(seed=seed)

        # Randomly select requested flight levels from the man/max available flight levels.
        requested_flight_levels = np.random.choice([min(self.flight_levels), max(self.flight_levels)], size = n, replace = True)

        # old:
        ret = {
            START_TIME_KEY: start_time,
            AIRCRAFT_KEY: [self.aircraft(callsign = callsign,
                                         aircraft_type = aircraft_type,
                                         start_time = start_time,
                                         current_flight_level = current_flight_level,
                                         cleared_flight_level = cleared_flight_level,
                                         requested_flight_level = requested_flight_level,
                                         route_index = route_index
                                         )
                           for callsign, aircraft_type, start_time, current_flight_level,
                               cleared_flight_level, requested_flight_level, route_index
                           in zip(callsigns, aircraft_types, start_times, current_flight_levels,
                                  cleared_flight_levels, requested_flight_levels, route_indices)]
        }
        return ret

    # TODO: decide what exactly the interface should be.
    #   Does this 'aircraft' method belong in an abstract base class called ScenarioAlgorithm?
    #   Perhaps the methods here should be:
    #    - start times
    #    - initial flight level
    #    - requested flight level
    #    - route name

    def aircraft(self, callsign, aircraft_type, start_time, current_flight_level,
                 cleared_flight_level, requested_flight_level, route_index) -> dict:
        """Returns all info required to create an aircraft, including its route."""

        # Infer the start position from the route (i.e. take the first fix).
        route = self.sector_element.shape.routes()[route_index]
        start_position = route[0][0]

        ret = {
            CALLSIGN_KEY: callsign,
            TYPE_KEY: aircraft_type,
            DEPARTURE_KEY: ScenarioGenerator.departure,
            DESTINATION_KEY: ScenarioGenerator.destination,
            START_POSITION_KEY: start_position,
            START_TIME_KEY: int(start_time),
            CURRENT_FLIGHT_LEVEL_KEY: int(current_flight_level),
            CLEARED_FLIGHT_LEVEL_KEY: int(cleared_flight_level),
            REQUESTED_FLIGHT_LEVEL_KEY: int(requested_flight_level),
            ROUTE_KEY: self.aircraft_route(route_index, level = requested_flight_level)
        }
        return ret



    # old:
    # def exponential_interarrival_times(self, duration, seed = None):
    #     """Generates exponential interarrival times"""
    #
    #     interarrival_times = []
    #     np.random.seed(seed = seed)
    #     while sum(interarrival_times) < duration:
    #         interarrival_times.append(np.random.exponential(scale = 1 / self.arrival_rate))
    #
    #     # Guard against an empty list of interarrival times.
    #     if not interarrival_times:
    #         raise Exception('Empty interrarival times. Try increasing scenario duration and/or arrival rate.')
    #
    #     return interarrival_times




