
import pytest

from aviary.metrics.separation_metric import AircraftSeparation


def test_separation_score():

    metric = AircraftSeparation()

    lon1, lat1, alt1 = (0, 0, 0)
    lon2, lat2, alt2 = (0, 0, 0)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == -1

    lon2, lat2, alt2 = (5, 0, 0)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == 0

    lon2, lat2, alt2 = (0, 0, 1000)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == 0

    lon1, lat1, alt1 = (0, 5, 0)
    lon2, lat2, alt2 = (0, 0, 0)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == 0

    
