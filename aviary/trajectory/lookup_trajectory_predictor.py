"""
Provides simple trajectory prediction estimates via lookup tables.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk


import aviary.trajectory.trajectory_predictor as tp

class LookupTrajectoryPredictor(tp.TrajectoryPredictor):
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

        if not aircraft_type in self.cruise_speed_lookup.columns:
            raise ValueError(f'Aircraft type {aircraft_type} not found in cruise speed lookup table.')
        return self.cruise_speed_lookup.at[flight_level, aircraft_type]


    def climb_time_to_level(self, flight_level, aircraft_type):
        """Looks up the climb time in seconds for a given aircraft type"""

        if not aircraft_type in self.cruise_speed_lookup.columns:
            raise ValueError(f'Aircraft type {aircraft_type} not found in climb time lookup table.')
        return self.climb_time_lookup.at[flight_level, aircraft_type]


    def downtrack_distance_to_level(self, flight_level, aircraft_type):
        """Looks up the downtrack distance in metres for a given aircraft type"""

        if not aircraft_type in self.cruise_speed_lookup.columns:
            raise ValueError(f'Aircraft type {aircraft_type} not found in downtrack distance lookup table.')
        return self.downtrack_distance_lookup.at[flight_level, aircraft_type]


    @staticmethod
    def load_trajectory_lookups(cruise_speed_lookup, climb_time_lookup, downtrack_distance_lookup):
        """
        Static method to load trajectory lookup data. Assigns to the global_trajectory_predictor variable.

        :param cruise_speed_lookup (pandas data frame): Lookup table for cruise speeds by flight level & aircraft type. 
        :param climb_time_lookup (pandas data frame): Lookup table for climb time by flight level & aircraft type. 
        :param downtrack_distance_lookup (pandas data frame): Lookup table for downtrack distance in the climb by flight level & aircraft type.
        """

        # Assign to the global trajectory predictor variable.
        tp.global_trajectory_predictor = LookupTrajectoryPredictor(cruise_speed_lookup=cruise_speed_lookup,
                                                                   climb_time_lookup=climb_time_lookup,
                                                                   downtrack_distance_lookup=downtrack_distance_lookup)
