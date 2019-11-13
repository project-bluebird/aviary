"""
Scenario generation algorithm with a single overflier and a single climber.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
import aviary.scenario.scenario_generator as sg

class OverflierClimberScenario(ScenarioAlgorithm):
    """An overflier-climber scenario generator for I, X, Y airspace sectors"""


    def __init__(self, **kwargs):

        # Pass the keyword args (including the random seed) to the superclass constructor.
        super().__init__(**kwargs)


    # Overriding abstract method
    def aircraft_generator(self, sector) -> dict:
        """Generates a sequence of aircraft constituting a scenario."""

        # TODO:
        # - expect kwargs for the time to conflict
        # -

        # Construct the overflier.
        route = self.route(sector)
        overflier_flight_level = int(0) # TODO: pick any except the lowest flight level
        yield {
            sg.START_TIME_KEY: 0,
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: self.aircraft_type(),
            sg.DEPARTURE_KEY: '',  # ScenarioGenerator.departure, # TODO.
            sg.DESTINATION_KEY: '',  # ScenarioGenerator.destination, # TODO.
            sg.CURRENT_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.CLEARED_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.ROUTE_KEY: route
        }

        # Construct the climber, which flies the reverse route, starting below the overflier and whose requested
        # flight level is greater than or equal to that of the overflier.
        climber_current_flight_level = int(0) # TODO: pick any below the overflier_flight_level
        climber_requested_flight_level = int(0)  # TODO: pick any equal to or above the overflier_flight_level
        route.reverse()
        yield {
            sg.START_TIME_KEY: 0,
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: self.aircraft_type(),
            sg.DEPARTURE_KEY: '',  # ScenarioGenerator.departure, # TODO.
            sg.DESTINATION_KEY: '',  # ScenarioGenerator.destination, # TODO.
            sg.CURRENT_FLIGHT_LEVEL_KEY: climber_current_flight_level,
            sg.CLEARED_FLIGHT_LEVEL_KEY: climber_current_flight_level,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: climber_requested_flight_level,
            sg.ROUTE_KEY: route
        }






