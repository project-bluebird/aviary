"""
Scenario generation algorithm with Poisson aircraft arrivals.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import random

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm
from aviary.scenario.flight_phase import FlightPhase

import aviary.scenario.scenario_generator as sg


class IncrementalOcdScenario(ScenarioAlgorithm):
    """An incremental overflier-climber-descender scenario generation algorithm"""

    def __init__(self,
                 underlying_scenario,
                 seed,
                 overflier_prob = 1/3,
                 climber_prob = 1/3,
                 descender_prob = 1/3,
                 climber_initial_interval = 0.5,
                 climber_minimum_climb = 0.3,
                 descender_initial_interval=0.5,
                 descender_minimum_descent=0.3):
        """
        IncrementalOcdScenario class constructor.

        :param underlying_scenario: The underlying scenario
        :param seed: a random seed
        :param overflier_prob: number in (0, 1]. The probability of generating an overflier aircraft.
        :param climber_prob: number in (0, 1]. The probability of generating a climber aircraft.
        :param descender_prob: number in (0, 1]. The probability of generating a descender aircraft.
        :param climber_initial_interval (CII): number in (0, 1]. The range of possible flight levels from which initial FL will be picked for climbers (e.g. 0.5 means the first half will be included)
        :param climber_minimum_climb (CMC): number in (0, 1]. The range of ascents from which the requested FL will be picked (e.g. if CII is 0.5 and CMC is 0.3 then the requested FL will only include the top 20% of flight levels)
        :param descender_initial_interval (DII): number in (0, 1]. Similar to CII, but for descenders.
        :param descender_minimum_descent (DMD): number in (0, 1]. Similar to CMC, but for descenders.
        """

        if not isinstance(underlying_scenario, ScenarioAlgorithm):
            raise ValueError('underlying_scenario must be a ScenarioAlgorithm')

        if not sum([overflier_prob, climber_prob, descender_prob]) == 1:
            raise ValueError('aircraft phase probabilities must sum to 1')

        if sum([climber_initial_interval, climber_minimum_climb]) > 1:
            raise ValueError('climber initial interval plus minimum climb must be at most 1')

        if sum([descender_initial_interval, descender_minimum_descent]) > 1:
            raise ValueError('descender initial interval plus minimum descent must be at most 1')

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

    # Overriding abstract method
    def aircraft_generator(self) -> dict:
        """Generates a sequence of aircraft constituting a scenario."""

        for aircraft in self.underlying_scenario.aircraft_generator():
            yield aircraft

        yield self.aircraft()

    def aircraft(self):
        """Returns the additional aircraft in this scenario, beyond those in the underlying scenario."""

        # TODO. (Copied from PoissonScenario)

        route = self.route()
        start_position = route.fix_points()[0].coords[0]
        departure = self.departure_airport(route)
        destination = self.destination_airport(route)
        # truncate the route i.e. remove the starting position fix
        # note coords of start_position are in lon/lat order
        route.truncate(initial_lat=start_position[1], initial_lon=start_position[0])

        return {
            sg.AIRCRAFT_TIMEDELTA_KEY: 0,
            sg.START_POSITION_KEY: start_position,
            sg.CALLSIGN_KEY: next(self.callsign_generator()),
            sg.AIRCRAFT_TYPE_KEY: self.aircraft_type(),
            sg.DEPARTURE_KEY: departure,
            sg.DESTINATION_KEY: destination,
            sg.CURRENT_FLIGHT_LEVEL_KEY: 0,
            sg.CLEARED_FLIGHT_LEVEL_KEY: 0,
            sg.REQUESTED_FLIGHT_LEVEL_KEY: 0,
            sg.ROUTE_KEY: route.serialize(),
        }

    def flight_phase(self):
        """Picks a flight phase (overflier, climber or descender)."""

        u = random.uniform(0, 1)
        if u < self.overflier_prob:
            return FlightPhase.overflier
        if u - self.overflier_prob < self.climber_prob:
            return FlightPhase.climber
        return FlightPhase.descender
