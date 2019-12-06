"""
Abstract base class representing a scenario generation algorithm.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk


from abc import ABC, abstractmethod

import random


class ScenarioAlgorithm(ABC):
    """A scenario generation algorithm"""

    # Default parameters:
    default_aircraft_types = ["B77W", "A320", "A346"] # Types of aircraft available (by default).
    default_flight_levels = [200, 240, 280, 320, 360, 400]
    default_callsign_prefixes = ["SPEEDBIRD", "VJ", "DELTA", "EZY"]

    def __init__(
        self, sector_element, aircraft_types=None, flight_levels=None, callsign_prefixes=None, seed=None
    ):

        self.seed = seed
        # TODO: make set_seed non-static and use the instance variable instead of an argument.
        # TODO: Also make ScenarioGenerator independent of the seed, except via a set_seed method that sets the seed in the algorithm.
        ScenarioAlgorithm.set_seed(seed)

        self.sector_element = sector_element
        self.seen_callsigns = set()

        if aircraft_types is None:
            aircraft_types = ScenarioAlgorithm.default_aircraft_types
        self.aircraft_types = aircraft_types

        if flight_levels is None:
            flight_levels = ScenarioAlgorithm.default_flight_levels
        self.flight_levels = flight_levels

        if callsign_prefixes is None:
            callsign_prefixes = ScenarioAlgorithm.default_callsign_prefixes
        self.callsign_prefixes = callsign_prefixes

    @property
    def aircraft_types(self):
        return self._aircraft_types

    @aircraft_types.setter
    def aircraft_types(self, aircraft_types):
        assert (
            aircraft_types
            and isinstance(aircraft_types, list)
            and all(isinstance(at, str) for at in aircraft_types)
        ), "Incorrect input {} for aircraft_types".format(aircraft_types)
        self._aircraft_types = aircraft_types

    @property
    def flight_levels(self):
        return self._flight_levels

    @flight_levels.setter
    def flight_levels(self, flight_levels):
        assert (
            flight_levels
            and isinstance(flight_levels, list)
            and all(
                (isinstance(fl, int) and fl % 10 == 0 and fl > 0)
                for fl in flight_levels
            )
        ), "Incorrect input {} for flight_levels".format(flight_levels)
        self._flight_levels = flight_levels

    @property
    def callsign_prefixes(self):
        return self._callsign_prefixes

    @callsign_prefixes.setter
    def callsign_prefixes(self, callsign_prefixes):
        assert (
            callsign_prefixes
            and isinstance(callsign_prefixes, list)
            and all((isinstance(cp, str) and len(cp) >= 2) for cp in callsign_prefixes)
        ), "Incorrect input {} for callsign_prefixes".format(callsign_prefixes)
        self._callsign_prefixes = callsign_prefixes

    @abstractmethod
    def aircraft_generator(self) -> dict:
        pass

    @staticmethod
    def set_seed(seed):
        random.seed(seed)

    def reset_seen_callsigns(self):
        """
        Resets the set of seen callsigns (used to prevent duplicates).
        After resetting, duplicate callsigns (with the set generated before the reset) may occur."""
        self.seen_callsigns = set()

    def route(self):
        """Returns a random route"""

        # Note: use the sector routes() method, *not* the shape routes().
        return random.choice(self.sector_element.routes())

    def flight_level(self):
        """Returns a random flight level"""

        return random.choice(self.flight_levels)

    def aircraft_type(self):
        """Returns a random aircraft type"""

        return random.choice(self.aircraft_types)

    def callsign_generator(self):
        """Generates a random sequence of unique callsigns"""

        k = 3
        while True:
            suffix = "".join([str(x) for x in random.sample(range(0, 10), k=k)])
            prefix = random.choice(self.callsign_prefixes)
            ret = prefix + suffix

            if ret in self.seen_callsigns:
                k = k + 1
            else:
                self.seen_callsigns.add(ret)
                yield ret

    def departure_airport(self, route):
        """Returns a suitable departure airport for the given route"""

        # TODO: currently a dummy implementation
        return "DEP"

    def destination_airport(self, route):
        """Returns a suitable destination airport for the given route"""

        # TODO: currently a dummy implementation
        return "DEST"
