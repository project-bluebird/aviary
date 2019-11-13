"""
Abstract base class representing a scenario generation algorithm.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk


from abc import ABC, abstractmethod

import time
import random
import itertools
import numpy as np

class ScenarioAlgorithm(ABC):
    """A scenario generation algorithm"""

    # Default parameters:
    default_aircraft_types = ["B747"] # Types of aircraft available (by default).
    default_flight_levels = [200, 240, 280, 320, 360, 400]
    callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"]

    def __init__(self, aircraft_types = None, flight_levels = None, callsign_prefixes = None, seed = None):

        ScenarioAlgorithm.set_seed(seed)

        if aircraft_types is None:
            aircraft_types = ScenarioAlgorithm.default_aircraft_types
        self.aircraft_types = aircraft_types

        if flight_levels is None:
            flight_levels = ScenarioAlgorithm.default_flight_levels
        self.flight_levels = flight_levels

        if callsign_prefixes is None:
            callsign_prefixes = ScenarioAlgorithm.callsign_prefixes
        self.callsign_prefixes = callsign_prefixes

    @abstractmethod
    def aircraft_generator(self, sector) -> dict:
        pass

    @staticmethod
    def set_seed(seed):
        random.seed(seed)

    def route(self, sector):
        """Return a random route"""

        return random.choice(sector.shape.routes())


    def flight_level(self):
        """Returns a random flight level"""

        return random.choice(self.flight_levels)


    def aircraft_type(self):
        """Returns a random aircraft type"""

        return random.choice(self.aircraft_types)


    def callsign_generator(self):
        """Generates a random sequence of unique callsigns"""

        seen = set()

        k = 3
        while True:
            suffix = ''.join([str(x) for x in random.sample(range(0, 10), k = k)])
            prefix = random.choice(self.callsign_prefixes)
            ret = prefix + suffix

            if ret in seen:
                k = k + 1
            else:
                yield ret
                seen.add(ret)
