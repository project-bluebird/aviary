"""
Scenario generation algorithm with a single overflier and a single climber.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import random

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
from aviary.scenario.overflier_climber_scenario import OverflierClimberScenario
import aviary.scenario.scenario_generator as sg
from aviary.geo.geo_helper import GeoHelper

class OverflierClimberExtendedScenario(ScenarioAlgorithm):
    """
    An extended overflier-climber scenario generator for I, X, Y airspace sectors.

    The extended scenario is similar to the simple overflier-climber scenario implemented in OverflierClimberScenario,
    except that the start positions of both aircraft are modified to include an additional separation of arbitrary
    duration (the "thinking time").

    This modification has the effect of making an immediate climb potentially optimal (whereas in the simple
    overflier-climber scenario such a policy would lead, by construction, to a loss of separation).

    This algorithm assumes that each aircraft's route is a straight line path to the sector centre,
    as is the case in an I, X or Y sector element.

    Args:
        trajectory_predictor: Simple trajectory predictor offering cruise speed, climb time and downtrack distance estimates.

    Attributes:
        trajectory_predictor: Simple trajectory predictor offering cruise speed, climb time and downtrack distance estimates.
    """


    def __init__(self, trajectory_predictor, thinking_time, **kwargs):

        # Call the superclass constructor.
        super().__init__(**kwargs)

        self.trajectory_predictor = trajectory_predictor

        if not thinking_time > 0:
            raise ValueError(f'Invalid thinking_time argument: {thinking_time}')

        self.thinking_time = thinking_time

        if len(set(self.flight_levels)) < 3:
            raise ValueError("Extended overflier-climber scenario requires at least 3 flight levels.")

        # Choose three different flight levels.
        levels = random.sample(set(self.flight_levels), k = 3)
        levels.sort()

        self.low = levels[0]
        self.mid =levels[1]
        self.high = levels[2]

        # Instantiate an OverflierClimber algorithm with only the low & mid flight levels.
        self.overflier_climber = OverflierClimberScenario(trajectory_predictor = trajectory_predictor,
                                                          aircraft_types=self.aircraft_types,
                                                          flight_levels=[self.low, self.mid],
                                                          callsign_prefixes=self.callsign_prefixes,
                                                          seed=self.seed)


    # Overriding abstract method
    def aircraft_generator(self, sector) -> dict:
        """Generates a sequence of two aircraft whose default trajectories intersect at the centre of the sector."""

        # Generate the overflier, followed by the climber.
        is_overflier = True
        for aircraft in self.overflier_climber.aircraft_generator(sector):

            yield self.extend_aircraft(aircraft, is_overflier = is_overflier, sector = sector)
            is_overflier = False


    def extend_aircraft(self, aircraft, is_overflier, sector):

        # Check that the flight level is as expected.
        if is_overflier:
            expected_flight_level = self.mid
        else:
            expected_flight_level = self.low

        if aircraft[sg.CURRENT_FLIGHT_LEVEL_KEY] != expected_flight_level:
            raise Exception(f'Unexpected flight level: {aircraft[sg.CURRENT_FLIGHT_LEVEL_KEY]}. Expected: {expected_flight_level}')

        # Get the aircraft's cruise speed.
        true_airspeed = self.trajectory_predictor.cruise_speed(flight_level = aircraft[sg.CURRENT_FLIGHT_LEVEL_KEY],
                                                               aircraft_type = aircraft[sg.AIRCRAFT_TYPE_KEY])

        # Modify the aircraft's start position by winding back a distance
        # determined by its cruise speed and the thinking time.

        windback_distance = true_airspeed * self.thinking_time

        lat1, lon1 = sector.centre_point()
        # Note: here it is assumed that the aircraft travels on a straight line
        # to the sector centre (as is the case in an I, X or Y sector element).
        lon2, lat2 = aircraft[sg.START_POSITION_KEY]
        lat_lon = GeoHelper.waypoint_location(lat1, lon1, lat2, lon2, windback_distance)

        aircraft[sg.START_POSITION_KEY] = tuple(i for i in reversed(lat_lon)), # Order is (lon, lat).

        # If the aircraft is the climber, set the requested flight level to 'high'
        if not is_overflier:
            aircraft[sg.REQUESTED_FLIGHT_LEVEL_KEY] = self.high

        return aircraft

