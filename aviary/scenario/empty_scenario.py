"""
Scenario generation algorithm with Poisson aircraft arrivals.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import random

from aviary.scenario.scenario_algorithm import ScenarioAlgorithm

import aviary.scenario.scenario_generator as sg

class EmptyScenario(ScenarioAlgorithm):
    """An algorithm generating an empty scenario"""

    def __init__(self, **kwargs):

        # Pass the keyword args (including the random seed) to the superclass constructor.
        super().__init__(**kwargs)

    # Overriding abstract method
    def aircraft_generator(self) -> dict:
        """Generates an empty sequence."""

        return
        yield