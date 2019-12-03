
import pytest

from aviary.metrics.separation_metric import pairwise_separation_metric, score

import aviary.metrics.utils as utils

_SCALE_FEET_TO_METERS = 1/utils._SCALE_METRES_TO_FEET


def test_score():

    result = score(0, 0, 1)
    assert result == -1

    result = score(5, 5, 10)
    assert result == -1

    result = score(7.5, 5, 10)
    assert result == -0.5

    result = score(10, 5, 10)
    assert result == 0

    result = score(15, 5, 10)
    assert result == 0


def test_separation_metric():

    lon1, lat1, alt1 = (0, 0, 0)
    lon2, lat2, alt2 = (0, 0, 0)

    assert pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2) == -1

    lon2, lat2, alt2 = (-.05, 0, 0)

    assert pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2) == -1

    lon2, lat2, alt2 = (0, -.1, 0)

    assert pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2) == pytest.approx(-0.8)

    lon2, lat2, alt2 = (0.15, 0, 0)

    assert pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2) == pytest.approx(-0.2)

    lon2, lat2, alt2 = (0, 0.2, 0)

    assert pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2) == 0

    lon2, lat2, alt2 = (0, 0, 1000 * _SCALE_FEET_TO_METERS)

    assert pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2) == -1

    lon2, lat2, alt2 = (0, 0, 1230 * _SCALE_FEET_TO_METERS)

    assert pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2) == pytest.approx(-0.77)

    lon2, lat2, alt2 = (0, 0, 1500 * _SCALE_FEET_TO_METERS)

    assert pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2) == pytest.approx(-0.5)

    lon2, lat2, alt2 = (0, 0, 2000 * _SCALE_FEET_TO_METERS)

    assert pairwise_separation_metric(lon1, lat1, alt1, lon2, lat2, alt2) == 0
