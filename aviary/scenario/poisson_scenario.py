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

        # Pass the keyword args (including the random seed) to the superclass constructor.
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
