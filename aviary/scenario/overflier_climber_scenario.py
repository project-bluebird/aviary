"""
Scenario generation algorithm with a single overflier and a single climber.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import random

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
import aviary.scenario.scenario_generator as sg
from aviary.geo.geo_helper import GeoHelper

class OverflierClimberScenario(ScenarioAlgorithm):
    """An overflier-climber scenario generator for I, X, Y airspace sectors"""


    # TODO: take three lookup tables on construction.
    def __init__(self, **kwargs):

        # Pass the keyword args (including the random seed) to the superclass constructor.
        super().__init__(**kwargs)


    # Overriding abstract method
    def aircraft_generator(self, sector) -> dict:
        """Generates a sequence of two aircraft whose default trajectories intersect at the centre of the sector."""

        # Construct the route.
        overflier_route = self.route(sector)
        overflier_departure = self.departure_airport(overflier_route)
        overflier_destination = self.destination_airport(overflier_route)

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

        # Location of the central fix of the sector (which is the conflict point).
        lat1, lon1 = sector.centre_point()

        # Compute the initial position of the overflier. Note lon/lat order!
        o_lon2, o_lat2 = overflier_route[0][1].coords[0] # Initial waypoint position on the overflier's route
        overflier_lat_lon = GeoHelper.waypoint_location(lat1, lon1, o_lat2, o_lon2, overflier_horizontal_distance)

        # Truncate the route in light of the modified starting position.
        overflier_truncated_route = self.truncate_route(overflier_route, overflier_lat_lon[0], overflier_lat_lon[1])

        # Construct the overflier.
        yield {
            sg.START_TIME_KEY: 0,
            sg.START_POSITION_KEY: overflier_lat_lon,
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: overflier_aircraft_type,
            sg.DEPARTURE_KEY: overflier_departure,
            sg.DESTINATION_KEY: overflier_destination,
            sg.CURRENT_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.CLEARED_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.ROUTE_KEY: overflier_truncated_route
        }

        # Construct the climber, which flies the reverse route, starting below the overflier and whose requested
        # flight level is greater than or equal to that of the overflier.
        climber_route = overflier_route.copy()
        climber_route.reverse()

        # Compute the initial position of the climber. Note lon/lat order!
        c_lon2, c_lat2 = climber_route[0][1].coords[0] # Initial waypoint position on the climber's route
        climber_lat_lon = GeoHelper.waypoint_location(lat1, lon1, c_lat2, c_lon2, climber_horizontal_distance)

        # Truncate the route in light of the modified starting position.
        climber_truncated_route = self.truncate_route(climber_route, climber_lat_lon[0], climber_lat_lon[1])

        yield {
            sg.START_TIME_KEY: 0,
            sg.START_POSITION_KEY: climber_lat_lon,
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: climber_aircraft_type,
            sg.DEPARTURE_KEY: overflier_destination, # Reversed overflier departure/destination.
            sg.DESTINATION_KEY: overflier_departure,
            sg.CURRENT_FLIGHT_LEVEL_KEY: climber_current_flight_level,
            sg.CLEARED_FLIGHT_LEVEL_KEY: climber_current_flight_level,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: climber_requested_flight_level,
            sg.ROUTE_KEY: climber_truncated_route
        }

    def truncate_route(self, route, initial_lat, initial_lon):
        """Truncates a route in light of a given start position by removing fixes that are already passed."""

        # Retain only those route elements that are closer to the final fix than the start_position.
        final_lon, final_lat = route[-1][1].coords[0] # Note lon/lat order!
        return [i for i in route if GeoHelper.distance(final_lat, final_lon, i[1].coords[0][1], i[1].coords[0][0]) <
                GeoHelper.distance(final_lat, final_lon, initial_lat, initial_lon)]

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