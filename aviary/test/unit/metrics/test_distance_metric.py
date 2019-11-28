
import pytest

import aviary.metrics.distance_metric as dm


class ConcreteMetric(dm.DistanceMetric):

    def score(self):
        pass


@pytest.fixture
def target():
    return ConcreteMetric()


def test_horizontal_distance(target):
    
    lat1 = 51.507389
    lon1 = 0.127806

    lat2 = 50.6083
    lon2 = -1.9608

    result = target.horizontal_distance_m(lon1, lat1, lon2, lat2)
    assert result == pytest.approx(1000 * 176.92, 0.01)

    result_nm = target.horizontal_distance_nm(lon1, lat1, lon2, lat2)
    assert result_nm == pytest.approx(round(result/dm._ONE_NM))


def test_vertical_distance(target):

    alt = 123456789.123456789
    assert target.vertical_distance_m(alt, alt) == 0
    assert target.vertical_distance_ft(alt, alt) == 0

    assert target.vertical_distance_m(300, 150) == 150
    assert target.vertical_distance_ft(300, 150) == 150 * dm._SCALE_METRES_TO_FEET
