"""
Provides simple trajectory prediction estimates.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

class LookupTrajectoryPredictor():
    """A class providing simple trajectory prediction via lookup tables for cruise speed, climb time & downtrack distance.

    Args:
        cruise_speed_lookup (pandas data frame): Lookup table for cruise speeds by flight level & aircraft type.
        climb_time_lookup (pandas data frame): Lookup table for climb time by flight level & aircraft type.
        downtrack_distance_lookup (pandas data frame): Lookup table for downtrack distance in the climb by flight level & aircraft type.

    Attributes:
        cruise_speed_lookup (pandas data frame): Lookup table for cruise speeds by flight level & aircraft type.
        climb_time_lookup (pandas data frame): Lookup table for climb time by flight level & aircraft type.
        downtrack_distance_lookup (pandas data frame): Lookup table for downtrack distance in the climb by flight level & aircraft type.
    """

    def __init__(self, cruise_speed_lookup, climb_time_lookup, downtrack_distance_lookup):

        self.cruise_speed_lookup = cruise_speed_lookup
        self.climb_time_lookup = climb_time_lookup
        self.downtrack_distance_lookup = downtrack_distance_lookup


    def cruise_speed(self, flight_level, aircraft_type):
        """Looks up the cruise speed in metres per second for a given flight level and aircraft type"""

        return self.cruise_speed_lookup.at[flight_level, aircraft_type]


    def climb_time_to_level(self, flight_level, aircraft_type):
        """Looks up the climb time in seconds for a given aircraft type"""

        return self.climb_time_lookup.at[flight_level, aircraft_type]


    def downtrack_distance_to_level(self, flight_level, aircraft_type):
        """Looks up the downtrack distance in metres for a given aircraft type"""

        return self.downtrack_distance_lookup.at[flight_level, aircraft_type]


    def climb_time_between_levels(self, lower_level, upper_level, aircraft_type):
        """Computes the time taken to climb between two levels"""

        return self.climb_time_to_level(upper_level, aircraft_type) - self.climb_time_to_level(lower_level, aircraft_type)


    def downtrack_distance_between_levels(self, lower_level, upper_level, aircraft_type):
        """Computes the downtrack distance in metres between two levels in the climb"""

        return self.downtrack_distance_to_level(upper_level, aircraft_type) - self.downtrack_distance_to_level(lower_level, aircraft_type)


