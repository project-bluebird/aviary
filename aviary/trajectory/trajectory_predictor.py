"""
Abstract base class providing simple trajectory prediction estimates.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from abc import ABC, abstractmethod

# Declare global variable.
global_trajectory_predictor = None

class TrajectoryPredictor(ABC):
    """
    A class providing trajectory prediction via lookup tables for cruise speed, climb time & downtrack distance.
    """

    def __init__(self):
        pass


    @abstractmethod
    def cruise_speed(self, flight_level, aircraft_type):
        """Returns the cruise speed in metres per second for a given flight level and aircraft type"""
        pass


    @abstractmethod
    def climb_time_to_level(self, flight_level, aircraft_type):
        """Returns the climb time in seconds for a given aircraft type"""
        pass


    @abstractmethod
    def downtrack_distance_to_level(self, flight_level, aircraft_type):
        """Returns the downtrack distance in metres for a given aircraft type"""
        pass


    def climb_time_between_levels(self, lower_level, upper_level, aircraft_type):
        """Computes the time taken to climb between two levels"""

        return self.climb_time_to_level(upper_level, aircraft_type) - self.climb_time_to_level(lower_level, aircraft_type)


    def downtrack_distance_between_levels(self, lower_level, upper_level, aircraft_type):
        """Computes the downtrack distance in metres between two levels in the climb"""

        return self.downtrack_distance_to_level(upper_level, aircraft_type) - \
               self.downtrack_distance_to_level(lower_level, aircraft_type)
