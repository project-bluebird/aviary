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
    """
    An overflier-climber scenario generator for I, X, Y airspace sectors

    Args:
        trajectory_predictor: Simple trajectory predictor offering cruise speed, climb time and downtrack distance estimates.

    Attributes:
        trajectory_predictor: Simple trajectory predictor offering cruise speed, climb time and downtrack distance estimates.
    """


    def __init__(self, trajectory_predictor, **kwargs):

        # Pass the keyword args (including the random seed) to the superclass constructor.
        super().__init__(**kwargs)

        self.trajectory_predictor = trajectory_predictor


    # Overriding abstract method
    def aircraft_generator(self, sector) -> dict:
        """Generates a sequence of two aircraft whose default trajectories intersect at the centre of the sector."""

        # Construct the overflier's route.
        overflier_route = self.route(sector)
        overflier_departure = self.departure_airport(overflier_route)
        overflier_destination = self.destination_airport(overflier_route)

        # Construct the climber's route, which is the reverse of the overflier's.
        climber_route = overflier_route.copy()
        climber_route.reverse()

        # Select the flight levels.
        overflier_flight_level = self.overflier_flight_level()
        climber_current_flight_level = self.climber_current_flight_level(overflier_flight_level)
        climber_requested_flight_level = self.climber_requested_flight_level(overflier_flight_level)

        # Compute the time taken for the climber to reach the overflier's flight level
        climber_aircraft_type = self.aircraft_type()
        climb_time_to_conflict_level = self.trajectory_predictor.climb_time_between_levels(lower_level=climber_current_flight_level,
                                                                      upper_level=overflier_flight_level,
                                                                      aircraft_type=climber_aircraft_type)

        # Compute the distance travelled by the overflier during the climber's climb.
        overflier_aircraft_type = self.aircraft_type()
        overflier_true_airspeed = self.trajectory_predictor.cruise_speed(overflier_flight_level, overflier_aircraft_type)

        # Get the horizontal distances travelled prior to the conflict.
        overflier_horizontal_distance = climb_time_to_conflict_level * overflier_true_airspeed
        climber_horizontal_distance = self.trajectory_predictor.downtrack_distance_between_levels(lower_level=climber_current_flight_level,
                                                                                      upper_level=overflier_flight_level,
                                                                                      aircraft_type=climber_aircraft_type)

        # Location of the central fix of the sector (which is the conflict point).
        lat1, lon1 = sector.centre_point()

        # Get the position of the first fix on the overflier's route. Note lon/lat order!
        o_lon2, o_lat2 = overflier_route.fix_points()[0].coords[0]

        # Compute the initial position of the overflier.
        # Note: this assumes that the route is a straight line from the initial fix to the central fix (conflict point).
        overflier_lat_lon = GeoHelper.waypoint_location(lat1, lon1, o_lat2, o_lon2, overflier_horizontal_distance)

        # Truncate the route in light of the modified starting position.
        overflier_route.truncate(initial_lat = overflier_lat_lon[0], initial_lon = overflier_lat_lon[1])

        # Construct the overflier.
        yield {
            sg.AIRCRAFT_TIMEDELTA_KEY: 0,
            sg.START_POSITION_KEY: tuple(i for i in reversed(overflier_lat_lon)), # Order is (lon, lat).
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: overflier_aircraft_type,
            sg.DEPARTURE_KEY: overflier_departure,
            sg.DESTINATION_KEY: overflier_destination,
            sg.CURRENT_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.CLEARED_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: overflier_flight_level,
            sg.ROUTE_KEY: overflier_route.serialize()
        }

        # Construct the climber, which starts below the overflier and whose requested
        # flight level is greater than or equal to that of the overflier.

        # Get the position of the first fix on the climber's route. Note lon/lat order!
        c_lon2, c_lat2 = climber_route.fix_points()[0].coords[0]

        # Compute the initial position of the climber.
        # Note: this assumes that the route is a straight line from the initial fix to the central fix (conflict point).
        climber_lat_lon = GeoHelper.waypoint_location(lat1, lon1, c_lat2, c_lon2, climber_horizontal_distance)

        # Truncate the route in light of the modified starting position.
        climber_route.truncate(initial_lat = climber_lat_lon[0], initial_lon = climber_lat_lon[1])

        yield {
            sg.AIRCRAFT_TIMEDELTA_KEY: 0,
            sg.START_POSITION_KEY: tuple(i for i in reversed(climber_lat_lon)), # Order is (lon, lat)
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: climber_aircraft_type,
            sg.DEPARTURE_KEY: overflier_destination, # Reversed overflier departure/destination.
            sg.DESTINATION_KEY: overflier_departure,
            sg.CURRENT_FLIGHT_LEVEL_KEY: climber_current_flight_level,
            sg.CLEARED_FLIGHT_LEVEL_KEY: climber_current_flight_level,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: climber_requested_flight_level,
            sg.ROUTE_KEY: climber_route.serialize()
        }


    def overflier_flight_level(self):
        """Returns a random flight level, excluding the minimum level"""

        if len(set(self.flight_levels)) < 2:
            raise ValueError('flight_levels must contain at least two distinct elements')

        return random.choice([x for x in self.flight_levels if x > min(self.flight_levels)])


    def climber_current_flight_level(self, overflier_flight_level):
        """Returns a random flight level, exceeding the overflier flight level"""

        return random.choice([x for x in self.flight_levels if x < overflier_flight_level])


    def climber_requested_flight_level(self, overflier_flight_level):
        """Returns a random flight level, equal to or exceeding the overflier flight level"""

        return random.choice([x for x in self.flight_levels if x >= overflier_flight_level])

