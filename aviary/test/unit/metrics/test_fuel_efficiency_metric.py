import pytest

from aviary.metrics.fuel_efficiency_metric import fuel_efficiency_metric

def test_fuel_efficiency_metric():

    ## Requested to climb:

    # In the climb the best score is obtained at the requested flight level:
    result = fuel_efficiency_metric(current_flight_level=100, requested_flight_level=400, initial_flight_level=200)
    assert result == -1 # Score is always in the interval [-1, 0].

    result = fuel_efficiency_metric(current_flight_level=200, requested_flight_level=400, initial_flight_level=200)
    assert result == -1

    result = fuel_efficiency_metric(current_flight_level=300, requested_flight_level=400, initial_flight_level=200)
    assert result == -1/2

    result = fuel_efficiency_metric(current_flight_level=400, requested_flight_level=400, initial_flight_level=200)
    assert result == 0

    # Climbing above the requested flight level worsens, rather than improves,
    # the fuel efficiency metric score, to avoid perverse incentives.
    result = fuel_efficiency_metric(current_flight_level=500, requested_flight_level=400, initial_flight_level=200)
    assert result == -1/2


    ## Requested to descend:

    # In the descent the best score is obtained at the initial flight level:
    result = fuel_efficiency_metric(current_flight_level=500, requested_flight_level=200, initial_flight_level=400)
    assert result == -1/2 # Climbing when descent is requested results in a worse score.

    result = fuel_efficiency_metric(current_flight_level=400, requested_flight_level=200, initial_flight_level=400)
    assert result == 0

    result = fuel_efficiency_metric(current_flight_level=300, requested_flight_level=200, initial_flight_level=400)
    assert result == -1/2

    result = fuel_efficiency_metric(current_flight_level=200, requested_flight_level=200, initial_flight_level=400)
    assert result == -1 # Worst possible score at the requested flight level.

    result = fuel_efficiency_metric(current_flight_level=100, requested_flight_level=200, initial_flight_level=400)
    assert result == -1 # Score is always in the interval [-1, 0].

    ## Entered at requested flight level:

    # No commands sent to aircraft
    result = fuel_efficiency_metric(current_flight_level=200, requested_flight_level=200, initial_flight_level=200)
    assert result == 0
