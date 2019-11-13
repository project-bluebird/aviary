"""
Scenario generation algorithm with Poisson aircraft arrivals.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import random

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
import aviary.scenario.scenario_generator as sg

class PoissonScenario(ScenarioAlgorithm):
    """A Poisson scenario generator for I, X, Y airspace sectors"""


    def __init__(self, arrival_rate, **kwargs):

        super().__init__(**kwargs)
        self.arrival_rate = arrival_rate


    # Overriding abstract method
    def aircraft_generator(self, sector) -> dict:
        """Generates a sequence of aircraft constituting a scenario."""

        while True:
            current_flight_level = int(self.flight_level())
            yield {
                sg.START_TIME_KEY: random.expovariate(lambd = self.arrival_rate),
                sg.CALLSIGN_KEY: next(self.callsign_generator()),
                sg.AIRCRAFT_TYPE_KEY: self.aircraft_type(),
                sg.DEPARTURE_KEY: '', # ScenarioGenerator.departure, # TODO.
                sg.DESTINATION_KEY: '', # ScenarioGenerator.destination, # TODO.
                sg.CURRENT_FLIGHT_LEVEL_KEY: current_flight_level,
                sg.CLEARED_FLIGHT_LEVEL_KEY: current_flight_level,
                sg.REQUESTED_FLIGHT_LEVEL_KEY: int(self.flight_level()),
                sg.ROUTE_KEY: self.route(sector)
            }


    # def aircraft(self, callsign, aircraft_type, start_time, current_flight_level,
    #              cleared_flight_level, requested_flight_level, route_index) -> dict:
    #     """Returns all info required to create an aircraft, including its route."""
    #
    #     # Infer the start position from the route (i.e. take the first fix).
    #     route = self.sector_element.shape.routes()[route_index]
    #     start_position = route[0][0]
    #
    #     ret = {
    #         CALLSIGN_KEY: callsign,
    #         TYPE_KEY: aircraft_type,
    #         DEPARTURE_KEY: ScenarioGenerator.departure,
    #         DESTINATION_KEY: ScenarioGenerator.destination,
    #         START_POSITION_KEY: start_position,
    #         START_TIME_KEY: int(start_time),
    #         CURRENT_FLIGHT_LEVEL_KEY: int(current_flight_level),
    #         CLEARED_FLIGHT_LEVEL_KEY: int(cleared_flight_level),
    #         REQUESTED_FLIGHT_LEVEL_KEY: int(requested_flight_level),
    #         ROUTE_KEY: self.aircraft_route(route_index, level = requested_flight_level)
    #     }
    #     return ret
