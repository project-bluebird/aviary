"""
Scenario generation algorithm with Poisson aircraft arrivals.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import random
import numpy as np

import shapely.geometry as geom

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
from aviary.scenario.flight_phase import FlightPhase

import aviary.scenario.scenario_generator as sg

from aviary.utils.geo_helper import GeoHelper

class IncrementalOcdScenario(ScenarioAlgorithm):
    """An incremental overflier-climber-descender scenario generation algorithm"""

    def __init__(self,
                 underlying_scenario,
                 seed,
                 overflier_prob = 1/3,
                 climber_prob = 1/3,
                 descender_prob = 1/3,
                 climber_cfl_range = 0.5,
                 climber_minimum_climb = 0.3,
                 descender_cfl_range=0.5,
                 descender_minimum_descent=0.3,
                 overflier_cfl_range=0.5,
                 start_position_distribution=np.array([1, 0]),
                 discrete_start_positions=False
                 ):
        """
        IncrementalOcdScenario class constructor.

        :param underlying_scenario: The underlying scenario
        :param seed: a random seed
        :param overflier_prob: number in (0, 1]. The probability of generating an overflier aircraft.
        :param climber_prob: number in (0, 1]. The probability of generating a climber aircraft.
        :param descender_prob: number in (0, 1]. The probability of generating a descender aircraft.
        :param climber_cfl_range (CCFLR): number in (0, 1]. The range of possible flight levels from which initial FL will be picked for climbers (e.g. 0.5 means the first half will be included)
        :param climber_minimum_climb (CMC): number in (0, 1]. The range of ascents from which the requested FL will be picked (e.g. if CCFLR is 0.5 and CMC is 0.3 then the requested FL will only include the top 20% of flight levels)
        :param descender_cfl_range (DCFLR): number in (0, 1]. Similar to CCFLR, but for descenders.
        :param descender_minimum_descent (DMD): number in (0, 1]. Similar to CMC, but for descenders.
        :param overflier_cfl_range: number in (0, 1]. The range of possible flight levels from which initial FL will be picked for overfliers (e.g. 0.5 means the first half will be included)
        :param start_position_distribution: a probability distribution as a numpy array. The probability of starting in each route segement (also defines the number of segments).
        :param discrete_start_positions: boolean. If True, start positions are at the discrete endpoints of the route segements.
        """

        if not isinstance(underlying_scenario, ScenarioAlgorithm):
            raise ValueError('underlying_scenario must be a ScenarioAlgorithm')

        if sum([overflier_prob, climber_prob, descender_prob]) != 1:
            raise ValueError('aircraft phase probabilities must sum to 1')

        if sum([climber_cfl_range, climber_minimum_climb]) > 1:
            raise ValueError('climber initial interval plus minimum climb must be at most 1')

        if sum([descender_cfl_range, descender_minimum_descent]) > 1:
            raise ValueError('descender initial interval plus minimum descent must be at most 1')

        if np.sum(start_position_distribution) != 1:
            raise ValueError('invalid initial position distribution')

        # Pass the keyword args (including the random seed) to the superclass constructor.
        super().__init__(
            sector_element=underlying_scenario.sector_element,
            aircraft_types=underlying_scenario.aircraft_types,
            flight_levels=underlying_scenario.flight_levels,
            callsign_prefixes=underlying_scenario.callsign_prefixes,
            seed=seed
        )

        self.underlying_scenario = underlying_scenario
        self.overflier_prob = overflier_prob
        self.climber_prob = climber_prob
        self.descender_prob = descender_prob

        self.climber_cfl_range = climber_cfl_range
        self.climber_minimum_climb = climber_minimum_climb
        self.descender_cfl_range = descender_cfl_range
        self.descender_minimum_descent = descender_minimum_descent
        self.overflier_cfl_range = overflier_cfl_range

        self.initial_position_distribution = start_position_distribution
        self.discrete_initial_positions = discrete_start_positions

        # Choose the route for the incremental aircraft.
        self.set_seed()
        self.route = self.choose_route()

    # Overriding abstract method
    def aircraft_generator(self) -> dict:
        """Generates a sequence of aircraft constituting a scenario."""

        for aircraft in self.underlying_scenario.aircraft_generator():
            yield aircraft

        yield self.aircraft()

    def aircraft(self):
        """Returns the additional aircraft in this scenario, beyond those in the underlying scenario."""

        self.set_seed()
        phase = self.choose_flight_phase()
        self.set_seed()
        current_fl, requested_fl = self.choose_flight_levels(phase)
        cleared_fl = current_fl

        # TODO. (Copied from PoissonScenario)
        self.set_seed()
        start_position = self.choose_start_position()

        self.set_seed()
        departure = self.choose_departure_airport(self.route)
        self.set_seed()
        destination = self.choose_destination_airport(self.route)
        # truncate the route i.e. remove the starting position fix
        # note coords of start_position are in lon/lat order
        self.route.truncate(initial_lat=start_position[1], initial_lon=start_position[0])

        return {
            sg.AIRCRAFT_TIMEDELTA_KEY: 0,
            sg.START_POSITION_KEY: start_position,
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: self.choose_aircraft_type(),
            sg.DEPARTURE_KEY: departure,
            sg.DESTINATION_KEY: destination,
            sg.CURRENT_FLIGHT_LEVEL_KEY: current_fl,
            sg.CLEARED_FLIGHT_LEVEL_KEY: cleared_fl,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: requested_fl,
            sg.ROUTE_KEY: self.route.serialize(),
        }

    def choose_flight_phase(self):
        """Picks a flight phase (overflier, climber or descender)."""

        u = random.uniform(0, 1)
        if u < self.overflier_prob:
            return FlightPhase.overflier
        if u - self.overflier_prob < self.climber_prob:
            return FlightPhase.climber
        return FlightPhase.descender

    def choose_flight_levels(self, flight_phase):
        """Picks a current flight level, given a flight phase"""

        if flight_phase == FlightPhase.overflier:
            cfl = self.choose_flight_level(exclude_lowest=1 - self.overflier_cfl_range)
            return cfl, cfl
        if flight_phase == FlightPhase.climber:
            cfl = self.choose_flight_level(exclude_highest=1 - self.climber_cfl_range)
            rfl = self.choose_flight_level(exclude_lowest=self.climber_cfl_range + self.climber_minimum_climb)
            return cfl, rfl
        if flight_phase == FlightPhase.descender:
            cfl = self.choose_flight_level(exclude_lowest=1 - self.descender_cfl_range)
            rfl = self.choose_flight_level(exclude_highest=self.descender_cfl_range + self.descender_minimum_descent)
            return cfl, rfl
        raise ValueError("flight_phase enum value expected")

    def choose_start_position(self):
        """Picks an aircraft starting position"""

        segment_startpoint, segment_endpoint = self.choose_route_segment()

        # If initial positions are discrete, return the start of the chosen route segment.
        if self.discrete_initial_positions:
            return segment_startpoint

        # If initial positions are continuous, return a uniform random sample along the chosen route segment.
        offset = np.random.uniform(low=0.0, high=self.segment_length(), size = 1)
        return GeoHelper.waypoint_location(lat1=segment_startpoint.y, lon1=segment_startpoint.x,
                                           lat2=segment_endpoint.y, lon2=segment_endpoint.x, distance_m=offset)

    def choose_route_segment(self):
        """Picks a route segment for the aircraft start position"""

        # Choose the route segment index, and compute the distance from the segment
        # start point to the following route fix.
        pre_fix_i, windback_distance = self._pre_fix_index()

        # Compute the start and end points of the chosen segment.
        fixes = self.route.fix_points()
        pre_fix = fixes[pre_fix_i]
        post_fix = fixes[pre_fix_i + 1]
        segment_startpoint = GeoHelper.waypoint_location(lat1=post_fix.y, lon1=post_fix.x,
                                    lat2=pre_fix.y, lon2=pre_fix.x,
                                    distance_m=windback_distance)
        segment_endpoint = GeoHelper.waypoint_location(lat1=segment_startpoint.y, lon1=segment_startpoint.x,
                                    lat2=post_fix.y, lon2=post_fix.x,
                                    distance_m=self.segment_length())

        return segment_startpoint, segment_endpoint

    def _pre_fix_index(self):
        """
        Returns a tuple containing:
            - the index of the "pre-fix", the fix preceding the start point of the chosen route segment
            - the "windback distance" from the fix *after* the pre-fix to the start of the chosen route segment
        """

        # Pick a segment index, and compute the length of each route segment in metres.
        self.set_seed()
        segment_index = self.choose_segment_index()
        segment_length = self.segment_length()

        # Identify the "post-fix" index, i.e. that of the first fix *after* the start of the route segment.
        fixes = self.route.fix_points()
        post_fix_index = 0
        post_fix_distance = 0
        while True:
            # If the distance to the post_fix is at least as big as the distance to the route segment start, then break.
            if post_fix_distance > segment_index * segment_length:
                break
            post_fix_index += 1
            lon1, lat1 = fixes[post_fix_index - 1].x, fixes[post_fix_index - 1].y
            lon2, lat2 = fixes[post_fix_index].x, fixes[post_fix_index].y
            post_fix_distance += GeoHelper.distance(lat1=lat1, lon1=lon1, lat2=lat2, lon2=lon2)

        windback_distance = post_fix_distance - (segment_index * segment_length)

        return post_fix_index - 1, windback_distance

    def choose_segment_index(self):
        """Picks a route segment for the aircraft start position according to the initial_position_distribution."""

        segment_indices = range(0, len(self.initial_position_distribution))
        return np.random.choice(a=segment_indices, size=1, p=self.initial_position_distribution)[0]

    def segment_length(self):
        """
        Computes the physical length of each route segment in metres.
        """

        span = self.route.span()
        return span/len(self.initial_position_distribution)


