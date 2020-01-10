
import pytest

from numpy import sin, pi
import shapely.geometry as geom

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

def test_i_polygon():

    length_nm = 100
    airway_width_nm = 40
    target = ss.IShape(length_nm = length_nm,
                       airway_width_nm = airway_width_nm)

    result = target.polygon

    assert isinstance(result, geom.polygon.BaseGeometry)

    assert result.bounds[0] == - airway_width_nm / 2
    assert result.bounds[1] == - length_nm / 2
    assert result.bounds[2] == airway_width_nm / 2
    assert result.bounds[3] == length_nm / 2

    longShape = ss.IShape(length_nm = 2 * length_nm,
                       airway_width_nm = airway_width_nm)
    wideShape = ss.IShape(length_nm = length_nm,
                       airway_width_nm = 2 * airway_width_nm)

    x, y = result.exterior.coords.xy
    long_x, long_y = longShape.polygon.exterior.coords.xy
    wide_x, wide_y = wideShape.polygon.exterior.coords.xy

    # Check that the "length" of the I shape runs along the y-axis, and the "width" along the x-axis.
    assert long_x == x
    assert long_y[0] < y[0]
    assert long_y[1] > y[1]
    assert long_y[2] > y[2]
    assert long_y[3] < y[3]

    assert wide_y == y
    assert wide_x[0] < x[0]
    assert wide_x[1] < x[1]
    assert wide_x[2] > x[2]
    assert wide_x[3] > x[3]


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
    assert(x.fixes['a'.upper()].y > x.fixes['b'.upper()].y)
    assert(x.fixes['b'.upper()].y > x.fixes['e'.upper()].y)
    assert(x.fixes['e'.upper()].y > x.fixes['f'.upper()].y)
    assert(x.fixes['f'.upper()].y > x.fixes['g'.upper()].y)

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
    assert(y.fixes['a'.upper()].y > y.fixes['b'.upper()].y)
    assert(y.fixes['b'.upper()].y > y.fixes['e'.upper()].y)
    assert(y.fixes['e'.upper()].y > y.fixes['f'.upper()].y)
    assert(y.fixes['f'.upper()].y > y.fixes['g'.upper()].y)

    # The route down the top-right branch decreasing in the y-coordinate is: c, d, e, f, g
    assert(y.fixes['c'.upper()].y > y.fixes['d'.upper()].y)
    assert(y.fixes['d'.upper()].y > y.fixes['e'.upper()].y)
    assert(y.fixes['e'.upper()].y > y.fixes['f'.upper()].y)
    assert(y.fixes['f'.upper()].y > y.fixes['g'.upper()].y)


def test_i_routes():

    length_nm = 10
    offset_nm = 25

    i = ss.IShape(length_nm=length_nm, offset_nm =  offset_nm)
    result = i.routes()

    assert isinstance(result, list)

    # There are two routes: ascending/descending along the y-axis.
    assert len(result) == 2

    # Each route contains five fixes.
    assert result[0].length() == 5
    assert result[1].length() == 5

    # Each route is a list of dictionary items (representing fixes) of the form: (name, Point).

    # result[0] is increasing along the y-axis
    assert result[0].fix_points()[0].y == -1 * (i.offset_nm + (length_nm / 2))
    assert result[0].fix_points()[1].y == -1 * (length_nm / 2)
    assert result[0].fix_points()[2].y == 0
    assert result[0].fix_points()[3].y == length_nm / 2
    assert result[0].fix_points()[4].y == i.offset_nm + (length_nm / 2)

    # result[1] is decreasing along the y-axis
    assert result[1].fix_points()[0].y == i.offset_nm + (length_nm / 2)
    assert result[1].fix_points()[1].y == length_nm / 2
    assert result[1].fix_points()[2].y == 0
    assert result[1].fix_points()[3].y == -1 * (length_nm / 2)
    assert result[1].fix_points()[4].y == -1 * (i.offset_nm + (length_nm / 2))


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
    assert result[0].fix_points()[0].y == -1 * (x.offset_nm + (length_nm / 2))
    assert result[0].fix_points()[1].y == -1 * (length_nm / 2)
    assert result[0].fix_points()[2].y == 0
    assert result[0].fix_points()[3].y == length_nm / 2
    assert result[0].fix_points()[4].y == x.offset_nm + (length_nm / 2)

    # result[1] is decreasing in the y-coordinate
    assert result[1].fix_points()[0].y == x.offset_nm + (length_nm / 2)
    assert result[1].fix_points()[1].y == length_nm / 2
    assert result[1].fix_points()[2].y == 0
    assert result[1].fix_points()[3].y == -1 * (length_nm / 2)
    assert result[1].fix_points()[4].y == -1 * (x.offset_nm + (length_nm / 2))


def test_y_routes():

    length_nm = 50
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
    assert result[0].fix_points()[0].x == pytest.approx(0)
    assert result[0].fix_points()[1].x == pytest.approx(0)
    assert result[0].fix_points()[2].x == pytest.approx(0)
    assert result[0].fix_points()[3].x < 0
    assert result[0].fix_points()[4].x < result[0].fix_points()[3].x

    # y-coordinates:
    assert result[0].fix_points()[0].y == -1 * (y.offset_nm + length_nm / 2)
    assert result[0].fix_points()[1].y == -1 * (length_nm / 2)
    assert result[0].fix_points()[2].y == pytest.approx(0) # Centre of the shape is at the origin
    assert result[0].fix_points()[3].y == pytest.approx(length_nm / 2 * sin(pi / 6))
    assert result[0].fix_points()[4].y == pytest.approx((y.offset_nm + length_nm / 2) * sin(pi / 6))

