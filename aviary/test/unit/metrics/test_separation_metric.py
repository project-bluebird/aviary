
import pytest

from aviary.metrics.separation_metric import AircraftSeparation

_SCALE_METRES_TO_FEET = 3.280839895

def test_separation_score():

    metric = AircraftSeparation()

    lon1, lat1, alt1 = (0, 0, 0)
    lon2, lat2, alt2 = (0, 0, 0)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == -1

    lon2, lat2, alt2 = (-.05, 0, 0)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == -1

    lon2, lat2, alt2 = (0, -.1, 0)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == -0.8

    lon2, lat2, alt2 = (0.15, 0, 0)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == -0.2

    lon2, lat2, alt2 = (0, 0.2, 0)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == 0

    lon2, lat2, alt2 = (0, 0, 1000/_SCALE_METRES_TO_FEET)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == -1

    lon2, lat2, alt2 = (0, 0, 1230/_SCALE_METRES_TO_FEET)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == -0.77

    lon2, lat2, alt2 = (0, 0, 1500/_SCALE_METRES_TO_FEET)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == -0.5

    lon2, lat2, alt2 = (0, 0, 2000/_SCALE_METRES_TO_FEET)

    assert metric.score(lon1, lat1, alt1, lon2, lat2, alt2) == 0
