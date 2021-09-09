"""
Construction of 2D polygons (including I, X, Y shapes) for use as
cross-sections of airspace sector elements.

TODO:
    - support gluing together simple I, X, Y elements to construct more complex sector shapes.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk


from enum import Enum

import shapely.geometry as geom
from shapely.ops import cascaded_union
from shapely.affinity import rotate, translate
from abc import abstractmethod

from aviary.sector.route import Route

# Default sector dimensions:
LENGTH_NM = 50
AIRWAY_WIDTH_NM = 10
OFFSET_NM = 10

EPSILON = 1e-10 # Small number used as a tolerance when determining routes.


class SectorShape:
    """A 2D sector shape with waypoint fixes"""

    @property
    def polygon(self):
        """
        Polygon property.

        :return: A Shapely BaseGeometry instance
        """
        return self._polygon

    # Make the polygon property immutable.
    @polygon.setter
    def polygon(self, polygon):
        raise Exception("polygon is immutable")

    @property
    def fixes(self) -> dict:
        """
        Fixes property.

        :return: A dictionary keyed by fix name with each value a Shapely Point instance
        """
        return self._fixes

    # Make the fixes property immutable.
    @fixes.setter
    def fixes(self, fixes):
        raise Exception("fixes are immutable")

    @property
    def routes(self):
        return self._routes

    # Make the routes property immutable.
    @routes.setter
    def routes(self, routes):
        raise Exception("routes are immutable")

class PolygonShape(SectorShape):

    """
    :param polygon: geom.polygon.BaseGeometry
    :param fixes: dictionary, {str:geom.Point}
    :param routes: list of aviary.sector.Route objects
    """

    def __init__(self, polygon, fixes, routes):

        assert isinstance(polygon, geom.polygon.BaseGeometry), "Sector polygon must be a Shapely polygon object"
        assert isinstance(fixes, dict), "Invalid fixes format, expected a dictionary"
        assert isinstance(routes, list), "Invalid routes format, expected a list"

        assert all(isinstance(fix, str) for fix in fixes.keys()), "Fix names must be strings"
        assert all(isinstance(fix, geom.Point) for fix in fixes.values()), "Fix coordinates must be Shapely Point objects"

        fix_names = fixes.keys()
        for route in routes:
            assert isinstance(route, Route), "Each route must be aviary.sector.Route class"
            for fix in route.fix_names():
                assert fix in fix_names, f"Route fix {fix} must be in included in fixes"

        self._polygon = polygon
        self._fixes = fixes
        self._routes = routes

class IShape(SectorShape):

    # I fixes from top to bottom:
    #
    #   'spirt'
    #   'air'
    #   'water'
    #   'earth'
    #   'fiyre'
    #
    i_fix_names = ['spirt', 'air', 'water', 'earth', 'fiyre']

    def __init__(self, length_nm = LENGTH_NM, fix_names = None,
                 airway_width_nm = AIRWAY_WIDTH_NM, offset_nm = OFFSET_NM):

        if airway_width_nm > length_nm:
            raise ValueError(f'I sector width {airway_width_nm} must not exceed length {length_nm}')

        self.length_nm = length_nm
        self.airway_width_nm = airway_width_nm
        self.offset_nm = offset_nm
        self.sector_type = "I"

        if fix_names is None:
            fix_names = self.i_fix_names

        # Set the polygon points
        points = [(-0.5 * airway_width_nm, -0.5 * length_nm),
                  (-0.5 * airway_width_nm, 0.5 * length_nm),
                  (0.5 * airway_width_nm, 0.5 * length_nm),
                  (0.5 * airway_width_nm, -0.5 * length_nm)]

        self._polygon = geom.Polygon(points)

        fix_points = self.__fix_points__()
        if len(fix_names) != len(fix_points):
            raise ValueError(f'fix_names must have length {len(fix_points)}')

        self._fixes = dict(zip([fix_name.upper() for fix_name in fix_names], fix_points))
        self._routes = self.__routes__()

    def __fix_points__(self):
        """Compute the locations of the fixes """

        x_min, y_min, x_max, y_max = self.polygon.bounds
        x_mid, y_mid = self.polygon.centroid.coords[0]

        fix_points = [geom.Point(x_mid, y_max + self.offset_nm), # top exterior
                  geom.Point(x_mid, y_max), # top
                  geom.Point(x_mid, y_mid), # middle
                  geom.Point(x_mid, y_min), # bottom
                  geom.Point(x_mid, y_min - self.offset_nm)] # bottom exterior

        return fix_points

    def __routes__(self):
        """
        Compute the valid routes through the sector.

        :return: A list of Route instances
        """

        # Order by increasing y-coordinate to get the "ascending" route.
        ascending_fix_list = sorted(list(self.fixes.items()), key = lambda item : item[1].coords[0][1])
        ascending_y = Route(fix_list = ascending_fix_list)
        # Reverse the order of fixes to get the "descending" route.
        descending_y = Route(fix_list = ascending_fix_list[::-1])
        return [ascending_y, descending_y]

class XShape(SectorShape):

    # X fixes anticlockwise from the top:
    #
    #                  'sin'
    #                 'gates'
    # 'siren' 'witch' 'abyss' 'demon' 'satan'
    #                 'haunt'
    #                 'limbo'
    #
    x_fix_names = ['sin', 'gates', 'siren', 'witch', 'abyss', 'haunt', 'limbo', 'demon', 'satan']

    # X routes: 1) vertical increasing in y-coordinate 2) vertical descreasing in y-coordinate
    #           3) horizontal increasing in x-coordinate 4) horizontal descreasing in x-coordinate

    def __init__(self, length_nm = LENGTH_NM, fix_names = None,
                 airway_width_nm = AIRWAY_WIDTH_NM, offset_nm = OFFSET_NM):

        self.length_nm = length_nm
        self.airway_width_nm = airway_width_nm
        self.offset_nm = offset_nm
        self.sector_type = "X"

        if fix_names is None:
            fix_names = self.x_fix_names

        i = IShape(length_nm = length_nm, airway_width_nm = airway_width_nm, offset_nm = offset_nm)
        polygon = cascaded_union([i.polygon, rotate(i.polygon, 90)])

        self._polygon = polygon

        fix_points = self.__fix_points__()
        if len(fix_names) != len(fix_points):
            raise ValueError(f'fix_names must have length {len(fix_points)}')

        self._fixes = dict(zip([fix_name.upper() for fix_name in fix_names], fix_points))
        self._routes = self.__routes__()

    def __fix_points__(self):

        x_mid, y_mid = self.polygon.centroid.coords[0]
        x_min, y_min, x_max, y_max = self.polygon.bounds

        fix_points = [geom.Point(x_mid, y_max + self.offset_nm), # top exterior
                      geom.Point(x_mid, y_max), # top
                      geom.Point(x_min - self.offset_nm, y_mid), # left exterior
                      geom.Point(x_min, y_mid), # left
                      geom.Point(x_mid, y_mid), # middle
                      geom.Point(x_mid, y_min), # bottom
                      geom.Point(x_mid, y_min - self.offset_nm), # bottom exterior
                      geom.Point(x_max, y_mid), # right
                      geom.Point(x_max + self.offset_nm, y_mid)] # right exterior

        return fix_points

    def __routes__(self):
        """
        Compute the valid routes through the sector.

        :return: A list of Route instances
        """

        # Get the fixes on the vertical line (i.e. with zero x coordinate).
        vertical_fixes = list(filter(lambda item : abs(item[1].coords[0][0]) < EPSILON, self.fixes.items()))
        # Get the fixes on the horizontal line (i.e. with zero y coordinate).
        horizontal_fixes = list(filter(lambda item : abs(item[1].coords[0][1]) < EPSILON, self.fixes.items()))

        # Order by increasing y-coordinate to get the "ascending_y" route.
        ascending_y_fix_list = sorted(vertical_fixes, key = lambda item : item[1].coords[0][1])
        ascending_y = Route(
            # name = self.route_names[0],
            fix_list = ascending_y_fix_list
        )
        descending_y = Route(
            # name = self.route_names[1],
            fix_list = ascending_y_fix_list[::-1]
        )

        # Order by increasing x-coordinate to get the "ascending_x" route.
        ascending_x_fix_list = sorted(horizontal_fixes, key = lambda item : item[1].coords[0][0])
        ascending_x = Route(fix_list = ascending_x_fix_list)
        descending_x = Route(fix_list = ascending_x_fix_list[::-1])

        return [ascending_y, descending_y, ascending_x, descending_x]

class YShape(SectorShape):

    # Y fixes from the centre outwards starting in the top-left branch:
    #
    #       'ghost'              'god'
    #            'bishp'   'canon'
    #                  'tri'
    #                  'son'
    #                 'deacn'
    #
    y_fix_names = ['ghost', 'bishp', 'god', 'canon', 'tri', 'son', 'deacn']

    # Y routes: 1) increasing in y-coordinate through left branch 2) decreasing in y-coordinate through left branch
    #           3) increasing in y-coordinate through right branch 4) decreasing in y-coordinate through right branch

    def __init__(self, length_nm = LENGTH_NM, fix_names = None,
                 airway_width_nm = AIRWAY_WIDTH_NM, offset_nm = OFFSET_NM):

        self.length_nm = length_nm
        self.airway_width_nm = airway_width_nm
        self.offset_nm = offset_nm
        self.sector_type = "Y"

        if fix_names is None:
            fix_names = self.y_fix_names

        # Use an I shape of half length here, so Y sector scale matches that of I & X.
        i = IShape(length_nm = length_nm / 2, airway_width_nm = airway_width_nm, offset_nm = offset_nm)
        x_mid, y_mid = i.polygon.centroid.coords[0]
        x_min, y_min, x_max, y_max = i.polygon.bounds
        offset_polygon = cascaded_union([i.polygon, rotate(i.polygon, -120, origin=(x_mid, y_max)), rotate(i.polygon, 120, origin=(x_mid, y_max))])

        # Shift the polygon so its centre is at the origin.
        polygon = translate(offset_polygon, xoff = 0.0, yoff = - length_nm / 4)

        self._polygon = polygon

        fix_points = self.__fix_points__()
        if len(fix_names) != len(fix_points):
            raise ValueError(f'fix_names must have length {len(fix_points)}')

        self._fixes = dict(zip([fix_name.upper() for fix_name in fix_names], fix_points))
        self._routes = self.__routes__()

    def __fix_points__(self):

        coords = list(self.polygon.exterior.coords)
        xy_min, xy_max = self.minmax_xy(coords)
        xmin, ymin = xy_min
        bottom = self.__get_centre__([geom.Point(pt) for pt in self.__get_coords__(coords, xmin)])
        bottom = geom.Point(self.polygon.centroid.coords[0][0], bottom.coords[0][1])
        _x, _y = bottom.coords[0]
        bottom_outer = geom.Point(_x, _y - self.offset_nm)

        origin = self.polygon.centroid
        fix_points = [rotate(bottom_outer, angle=-120, origin=origin), # left exterior
                      rotate(bottom, -120, origin=origin), # left
                      rotate(bottom_outer, angle=120, origin=origin), # right exterior
                      rotate(bottom, 120, origin=origin), # right
                      origin, # middle
                      bottom, # bottom
                      bottom_outer] # bottom exterior

        return fix_points

    def minmax_xy(self, coords):
        min_x, min_y = min([y for x, y in coords]), min([x for x, y in coords])
        max_x, max_y = max([y for x, y in coords]), max([x for x, y in coords])
        return [(min_x, min_y), (max_x, max_y)]

    def __get_coords__(self, coords, match):
        return [(x, y) for x, y in coords if x == match or y == match]

    def __get_centre__(self, coords):
        return geom.Point(geom.GeometryCollection(coords).centroid.coords[0])

    def __routes__(self):
        """
        Compute the valid routes through the sector.

        :return: A list of Route instances
        """

        # Get the fixes on the vertical line (i.e. with zero x coordinate).
        vertical_fixes = list(filter(lambda item : abs(item[1].coords[0][0]) < EPSILON, self.fixes.items()))

        # Get the fixes on the left arm, possibly including the vertical fixes.
        all_left_fixes = list(filter(lambda item : item[1].coords[0][0] < 0, self.fixes.items()))

        # Get the fixes strictly on the left arm (not including the vertical fixes).
        left_fixes = list(filter(lambda item : item[0] not in [it[0] for it in vertical_fixes], all_left_fixes))

        # Get the fixes in the route along the left arm.
        left_route_fixes = vertical_fixes
        left_route_fixes.extend(left_fixes)

        # Get the fixes in the route along the right arm.
        right_route_fixes = list(filter(lambda item : item[0] not in [it[0] for it in left_fixes], self.fixes.items()))

        # Order by increasing y-coordinate to get the "ascending_y" route.
        left_ascending_y_fix_list = sorted(left_route_fixes, key = lambda item : item[1].coords[0][1])
        left_ascending_y = Route(fix_list = left_ascending_y_fix_list)
        left_descending_y = Route(fix_list = left_ascending_y_fix_list[::-1])

        right_ascending_y_fix_list = sorted(right_route_fixes, key = lambda item : item[1].coords[0][1])
        right_ascending_y = Route(fix_list = right_ascending_y_fix_list)
        right_descending_y = Route(fix_list = right_ascending_y_fix_list[::-1])

        return [left_ascending_y, left_descending_y, right_ascending_y, right_descending_y]
