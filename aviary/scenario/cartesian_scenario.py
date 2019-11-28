"""
Scenario generation algorithm taking a Cartesian product
over aircraft types and flight levels.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
import aviary.scenario.scenario_generator as sg

class CartesianScenario(ScenarioAlgorithm):
    """A Cartesian scenario generator for I, X, Y airspace sectors"""

    def __init__(self, **kwargs):

        # Pass the keyword args to the superclass constructor.
        super().__init__(**kwargs)


    # Overriding abstract method
    def aircraft_generator(self) -> dict:
        """Generates a sequence of aircraft constituting a scenario."""

        for flight_level in self.flight_levels:
            for aircraft_type in self.aircraft_types:
                route = self.route()
                yield {
                    sg.AIRCRAFT_TIMEDELTA_KEY: 0,
                    sg.START_POSITION_KEY: route.fix_points()[0].coords[0],
                    sg.CALLSIGN_KEY: next(self.callsign_generator()),
                    sg.AIRCRAFT_TYPE_KEY: aircraft_type,
                    sg.DEPARTURE_KEY: self.departure_airport(route),
                    sg.DESTINATION_KEY: self.destination_airport(route),
                    sg.CURRENT_FLIGHT_LEVEL_KEY: flight_level,
                    sg.CLEARED_FLIGHT_LEVEL_KEY: flight_level,
                    sg.REQUESTED_FLIGHT_LEVEL_KEY: flight_level,
                    sg.ROUTE_KEY: route.serialize()
                }
