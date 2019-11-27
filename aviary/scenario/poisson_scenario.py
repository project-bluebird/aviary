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
    def aircraft_generator(self) -> dict:
        """Generates a sequence of aircraft constituting a scenario."""

        while True:
            current_flight_level = int(self.flight_level())
            route = self.route()
            start_position = route.fix_points()[0].coords[0]
            departure = self.departure_airport(route)
            destination = self.destination_airport(route)
            # truncate the route i.e. remove the starting position fix
            # note coords of start_position are in lon/lat order
            route.truncate(initial_lat=start_position[1], initial_lon=start_position[0])
            yield {
                sg.AIRCRAFT_TIMEDELTA_KEY: random.expovariate(lambd=self.arrival_rate),
                sg.START_POSITION_KEY: start_position,
                sg.CALLSIGN_KEY: next(self.callsign_generator()),
                sg.AIRCRAFT_TYPE_KEY: self.aircraft_type(),
                sg.DEPARTURE_KEY: departure,
                sg.DESTINATION_KEY: destination,
                sg.CURRENT_FLIGHT_LEVEL_KEY: current_flight_level,
                sg.CLEARED_FLIGHT_LEVEL_KEY: current_flight_level,
                sg.REQUESTED_FLIGHT_LEVEL_KEY: int(self.flight_level()),
                sg.ROUTE_KEY: route.serialize(),
            }
