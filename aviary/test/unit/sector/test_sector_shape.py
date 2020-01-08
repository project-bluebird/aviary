
import pytest

import aviary.sector.sector_shape as ss

def test_sector_type():

    i = ss.IShape()
    assert i.sector_type == ss.SectorType.I

    x = ss.XShape()
    assert x.sector_type == ss.SectorType.X

    y = ss.YShape()
    assert y.sector_type == ss.SectorType.Y

    # Test immutability of the sector_type
    with pytest.raises(Exception):
        i.sector_type = ss.SectorType.X

    assert i.sector_type == ss.SectorType.I


def test_i_route_names():

    route_names = ['up', 'down']
    target = ss.IShape(fix_names=['a', 'b', 'c', 'd', 'e'], route_names = route_names)

    assert target.route_names == [i.upper() for i in route_names]


def test_i_fixes():

    fix_names = ['a', 'b', 'c', 'd', 'e']
    i = ss.IShape(fix_names=fix_names)

    assert list(i.fixes.keys()) == [fix_name.upper() for fix_name in fix_names]

    # Check the I fix positions.
    for k in range(len(fix_names) - 1):
        current_fix = fix_names[k].upper()
        next_fix = fix_names[k + 1].upper()
        assert(i.fixes[current_fix].coords[0][1] > i.fixes[next_fix].coords[0][1])

    with pytest.raises(ValueError):
        ss.IShape(fix_names = ['a', 'b', 'c'])


def test_x_fixes():

    fix_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    x = ss.XShape(fix_names=fix_names)
    assert list(x.fixes.keys()) == [fix_name.upper() for fix_name in fix_names]

    # Check the X fix positions.
    # The vertical line decreasing in y-coordinate is: a, b, e, f, g
    assert(x.fixes['a'.upper()].coords[0][1] > x.fixes['b'.upper()].coords[0][1])
    assert(x.fixes['b'.upper()].coords[0][1] > x.fixes['e'.upper()].coords[0][1])
    assert(x.fixes['e'.upper()].coords[0][1] > x.fixes['f'.upper()].coords[0][1])
    assert(x.fixes['f'.upper()].coords[0][1] > x.fixes['g'.upper()].coords[0][1])

    # The horizontal line increasing in x-coordinate is: c, d, e, h, i
    assert(x.fixes['c'.upper()].coords[0][0] < x.fixes['d'.upper()].coords[0][0])
    assert(x.fixes['d'.upper()].coords[0][0] < x.fixes['e'.upper()].coords[0][0])
    assert(x.fixes['e'.upper()].coords[0][0] < x.fixes['h'.upper()].coords[0][0])
    assert(x.fixes['h'.upper()].coords[0][0] < x.fixes['i'.upper()].coords[0][0])


def test_y_fixes():

    fix_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    y = ss.YShape(fix_names=fix_names)
    assert list(y.fixes.keys()) == [fix_name.upper() for fix_name in fix_names]

    # Check the Y fix positions.
    # The route down the top-left branch decreasing in the y-coordinate is: a, b, e, f, g
    assert(y.fixes['a'.upper()].coords[0][1] > y.fixes['b'.upper()].coords[0][1])
    assert(y.fixes['b'.upper()].coords[0][1] > y.fixes['e'.upper()].coords[0][1])
    assert(y.fixes['e'.upper()].coords[0][1] > y.fixes['f'.upper()].coords[0][1])
    assert(y.fixes['f'.upper()].coords[0][1] > y.fixes['g'.upper()].coords[0][1])

    # The route down the top-right branch decreasing in the y-coordinate is: c, d, e, f, g
    assert(y.fixes['c'.upper()].coords[0][1] > y.fixes['d'.upper()].coords[0][1])
    assert(y.fixes['d'.upper()].coords[0][1] > y.fixes['e'.upper()].coords[0][1])
    assert(y.fixes['e'.upper()].coords[0][1] > y.fixes['f'.upper()].coords[0][1])
    assert(y.fixes['f'.upper()].coords[0][1] > y.fixes['g'.upper()].coords[0][1])


def test_i_routes():

    length_nm = 10
    i = ss.IShape(length_nm=length_nm)
    result = i.routes()

    assert isinstance(result, list)

    # There are two routes: ascending/descending along the y-axis.
    assert len(result) == 2

    # Each route contains five fixes.
    assert result[0].length() == 5
    assert result[1].length() == 5

    # Each route is a list of dictionary items (representing fixes) of the form: (name, Point).

    # result[0] is increasing along the y-axis
    assert result[0].fix_points()[0].coords[0][1] == -1 * (i.offset_nm + (length_nm / 2))
    assert result[0].fix_points()[1].coords[0][1] == -1 * (length_nm / 2)
    assert result[0].fix_points()[2].coords[0][1] == 0
    assert result[0].fix_points()[3].coords[0][1] == length_nm / 2
    assert result[0].fix_points()[4].coords[0][1] == i.offset_nm + (length_nm / 2)

    # result[1] is decreasing along the y-axis
    assert result[1].fix_points()[0].coords[0][1] == i.offset_nm + (length_nm / 2)
    assert result[1].fix_points()[1].coords[0][1] == length_nm / 2
    assert result[1].fix_points()[2].coords[0][1] == 0
    assert result[1].fix_points()[3].coords[0][1] == -1 * (length_nm / 2)
    assert result[1].fix_points()[4].coords[0][1] == -1 * (i.offset_nm + (length_nm / 2))


def test_x_routes():

    length_nm = 10
    x = ss.XShape(length_nm=length_nm)
    result = x.routes()

    assert isinstance(result, list)

    # There are four routes: ascending/descending in the y-coordinate and ascending/descending in the x-coordinate.
    assert len(result) == 4

    # Each route contains five fixes.
    assert result[0].length() == 5
    assert result[1].length() == 5
    assert result[2].length() == 5
    assert result[3].length() == 5

    # Each element of 'result' is a list of dictionary items (representing fixes) of the form: (name, Point).

    # result[0] is increasing in the y-coordinate
    assert result[0].fix_points()[0].coords[0][1] == -1 * (x.offset_nm + (length_nm / 2))
    assert result[0].fix_points()[1].coords[0][1] == -1 * (length_nm / 2)
    assert result[0].fix_points()[2].coords[0][1] == 0
    assert result[0].fix_points()[3].coords[0][1] == length_nm / 2
    assert result[0].fix_points()[4].coords[0][1] == x.offset_nm + (length_nm / 2)

    # result[1] is decreasing in the y-coordinate
    assert result[1].fix_points()[0].coords[0][1] == x.offset_nm + (length_nm / 2)
    assert result[1].fix_points()[1].coords[0][1] == length_nm / 2
    assert result[1].fix_points()[2].coords[0][1] == 0
    assert result[1].fix_points()[3].coords[0][1] == -1 * (length_nm / 2)
    assert result[1].fix_points()[4].coords[0][1] == -1 * (x.offset_nm + (length_nm / 2))


def test_y_routes():

    length_nm = 10
    y = ss.YShape(length_nm=length_nm)
    result = y.routes()

    assert isinstance(result, list)

    # There are four routes: two along each of the Y branches.
    assert len(result) == 4

    # Each route contains five fixes.
    assert result[0].length() == 5
    assert result[1].length() == 5
    assert result[2].length() == 5
    assert result[3].length() == 5

    # Each element of 'result' is a list of dictionary items (representing fixes) of the form: (name, Point).

    # result[0] is increasing in the y-coordinate and up the left branch of the Y.

    # x-coordinates:
    assert result[0].fix_points()[0].coords[0][0] == pytest.approx(0)
    assert result[0].fix_points()[1].coords[0][0] == pytest.approx(0)
    assert result[0].fix_points()[2].coords[0][0] == pytest.approx(0)
    assert result[0].fix_points()[3].coords[0][0] < 0
    assert result[0].fix_points()[4].coords[0][0] < result[0].fix_points()[3].coords[0][0]

    # y-coordinates:
    assert result[0].fix_points()[0].coords[0][1] == -1 * (y.offset_nm + (length_nm / 4))
    assert result[0].fix_points()[1].coords[0][1] == -1 * (length_nm / 4)
    assert result[0].fix_points()[2].coords[0][1] == pytest.approx(length_nm / 4)
    assert result[0].fix_points()[3].coords[0][1] == pytest.approx(length_nm / 2)
    assert result[0].fix_points()[4].coords[0][1] == pytest.approx(y.offset_nm)

