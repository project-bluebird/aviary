"""
Scenario generation algorithm with a single overflier and a single climber.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import random

from geopy import Point
from geopy.distance import distance, VincentyDistance

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
import aviary.scenario.scenario_generator as sg

class OverflierClimberScenario(ScenarioAlgorithm):
    """An overflier-climber scenario generator for I, X, Y airspace sectors"""


    # TODO: take three lookup tables on construction.
    def __init__(self, **kwargs):

        # Pass the keyword args (including the random seed) to the superclass constructor.
        super().__init__(**kwargs)


    # Overriding abstract method
    def aircraft_generator(self, sector) -> dict:
        """Generates a sequence of aircraft constituting a scenario."""

        # Construct the route.
        route = self.route(sector)
        overflier_departure = self.departure_airport(route)
        overflier_destination = self.destination_airport(route)

        # Select the flight levels.
        overflier_flight_level = self.overflier_flight_level()
        climber_current_flight_level = random.choice([x for x in self.flight_levels if x < overflier_flight_level])
        climber_requested_flight_level = random.choice([x for x in self.flight_levels if x >= overflier_flight_level])

        # Compute the time taken for the climber to reach the overflier's flight level
        climber_aircraft_type = self.aircraft_type()
        climb_time_to_conflict_level = self.climb_time_between_levels(lower_level=climber_current_flight_level,
                                                                      upper_level=overflier_flight_level,
                                                                      aircraft_type=climber_aircraft_type)

        # Compute the distance travelled by the overflier during the climber's climb.
        overflier_aircraft_type = self.aircraft_type()
        overflier_true_airspeed = self.cruise_speed(overflier_flight_level, overflier_aircraft_type)

        # Get the horizontal distances travelled prior to the conflict.
        overflier_horizontal_distance = climb_time_to_conflict_level * overflier_true_airspeed
        climber_horizontal_distance = self.downtrack_distance_between_levels(lower_level=climber_current_flight_level,
                                                                                      upper_level=overflier_flight_level,
                                                                                      aircraft_type=climber_aircraft_type)

        # Compute the initial positions of both aircraft.
        # TODO FROM HERE.
        # NOTE that this function VincentyDistance was bugfixed in geopy 1.13.0 but deprectaed in 1.14.0 (with no replacement?)
        bearing = 0 # TODO: get the bearing from the centre waypoint to the next waypoint for the overflier
        overflier_initial_lat_lon = VincentyDistance(miles=distMiles).destination(Point(lat1, lon1), bearing) # TODO.


        # Construct the overflier.
        yield {
            sg.START_TIME_KEY: 0,
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: overflier_aircraft_type,
            sg.DEPARTURE_KEY: overflier_departure,
            sg.DESTINATION_KEY: overflier_destination,
            sg.CURRENT_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.CLEARED_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.ROUTE_KEY: route
        }


        # Construct the climber, which flies the reverse route, starting below the overflier and whose requested
        # flight level is greater than or equal to that of the overflier.
        route.reverse()
        yield {
            sg.START_TIME_KEY: 0,
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: climber_aircraft_type,
            sg.DEPARTURE_KEY: overflier_destination, # Reversed overflier departure/destination.
            sg.DESTINATION_KEY: overflier_departure,
            sg.CURRENT_FLIGHT_LEVEL_KEY: climber_current_flight_level,
            sg.CLEARED_FLIGHT_LEVEL_KEY: climber_current_flight_level,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: climber_requested_flight_level,
            sg.ROUTE_KEY: route # Reversed overflier route.
        }


    def overflier_flight_level(self):
        """Returns a random flight level, excluding the minimum level"""

        if len(set(self.flight_levels)) < 2:
            raise ValueError('flight_levels must contain at least two distinct elements')

        return random.choice([x for x in self.flight_levels if x > min(self.flight_levels)])


    def climb_time_between_levels(self, lower_level, upper_level, aircraft_type):
        """Computes the time taken to climb between two levels"""

        return self.climb_time_to_level(upper_level, aircraft_type) - self.climb_time_to_level(lower_level, aircraft_type)


    def climb_time_to_level(self, level, aircraft_type):
        """Looks up the climb time in seconds for a given aircraft type"""
        # TODO: from the lookup table.
        return 0


    def downtrack_distance_between_levels(self, lower_level, upper_level, aircraft_type):
        """Computes the downtrack distance in metres between two levels in the climb"""

        return self.downtrack_distance_to_level(upper_level, aircraft_type) - self.downtrack_distance_to_level(lower_level, aircraft_type)


    def downtrack_distance_to_level(self, level, aircraft_type):
        """Looks up the downtrack distance in metres for a given aircraft type"""
        # TODO: from the lookup table.
        return 0


    def cruise_speed(self, flight_level, aircraft_type):
        """Looks up the cruise speed in metres per second for a given flight level and aircraft type"""
        # TODO: from the lookup table.
        return 0