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

class SectorType(Enum):
    I = "I",
    X = "X",
    Y = "Y"

class SectorShape:
    """A 2D sector shape with waypoint fixes"""

    ###
    ### Default fix names:
    ###

    # I fixes from top to bottom:
    #
    #   'spirt'
    #   'air'
    #   'water'
    #   'earth'
    #   'fiyre'
    #
    i_fix_names = ['spirt', 'air', 'water', 'earth', 'fiyre']

    # X fixes anticlockwise from the top:
    #
    #                  'sin'
    #                 'gates'
    # 'siren' 'witch' 'abyss' 'demon' 'satan'
    #                 'haunt'
    #                 'limbo'
    #
    x_fix_names = ['sin', 'gates', 'siren', 'witch', 'abyss', 'haunt', 'limbo', 'demon', 'satan']

    # Y fixes from the centre outwards starting in the top-left branch:
    #
    #       'ghost'              'god'
    #            'bishp'   'canon'
    #                  'tri'
    #                  'son'
    #                 'deacn'
    #
    y_fix_names = ['ghost', 'bishp', 'god', 'canon', 'tri', 'son', 'deacn']

    ###
    ###  Default route names:
    ###

    # I routes: 1) increasing in y-coordinate 2) decreasing in y-coordinate
    i_route_names = ['ascension', 'fallen']

    # X routes: 1) vertical increasing in y-coordinate 2) vertical descreasing in y-coordinate
    #           3) horizontal increasing in x-coordinate 4) horizontal descreasing in x-coordinate
    x_route_names = ['purgatory', 'blasphemer', 'damnation', 'redemption']

    # Y routes: 1) increasing in y-coordinate through left branch 2) decreasing in y-coordinate through left branch
    #           3) increasing in y-coordinate through right branch 4) decreasing in y-coordinate through right branch
    y_route_names = ['almighty', 'ethereal', 'everlasting', 'divine']

    @abstractmethod
    def routes(self) -> list:
        """
        Compute the valid routes through the sector.

        :return: A list of Route instances
        """
        pass


    @staticmethod
    def shape_constructor(type):
        """Parse a ShapeType (enum value) into a SectorShape constructor."""
        if type == SectorType.I:
            return IShape
        if type == SectorType.X:
            return XShape
        if type == SectorType.Y:
            return YShape
        raise ValueError(f'Invalid shape type: {type}.')


    def __init__(self,
                 sector_type: SectorType,
                 polygon: geom.base.BaseGeometry,
                 fix_names,
                 route_names,
                 length_nm,
                 airway_width_nm,
                 offset_nm
                 ):

        if not isinstance(sector_type, SectorType):
            raise KeyError("Type must be a SectorType")

        self._sector_type = sector_type
        self._polygon = polygon
        self._length_nm = length_nm
        self._airway_width_nm = airway_width_nm
        self._offset_nm = offset_nm

        fix_points = self.__fix_points__()

        if len(fix_names) != len(fix_points):
            raise ValueError(f'fix_names must have length {len(fix_points)}')

        self._fixes = dict(zip([fix_name.upper() for fix_name in fix_names], fix_points))

        self._route_names = [route_name.upper() for route_name in route_names]

        len_routes = len(self.routes())
        if len(route_names) != len_routes:
            raise ValueError(f'route_names must have length {len_routes}')


    @property
    def sector_type(self):
        """
        Sector type property

        :return: A SectorType enum value
        """
        return self._sector_type

    # Make the sector_type property immutable.
    @sector_type.setter
    def sector_type(self, sector_type):
        raise Exception("sector_type is immutable")

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
    def route_names(self):
        return self._route_names

    # Make the route_names property immutable.
    @route_names.setter
    def route_names(self, route_names):
        raise Exception("route_names are immutable")

    @property
    def length_nm(self):
        """
        Sector length property

        :return: The sector length in nautical miles
        """
        return self._length_nm

    # Make the length_nm property immutable.
    @length_nm.setter
    def length_nm(self, length_nm):
        raise Exception("length_nm is immutable")

    @property
    def airway_width_nm(self):
        """
        Airway width property

        :return: The airway width in nautical miles
        """
        return self._airway_width_nm

    # Make the airway_width_nm property immutable.
    @airway_width_nm.setter
    def airway_width_nm(self, airway_width_nm):
        raise Exception("airway_width_nm is immutable")

    @property
    def offset_nm(self):
        """
        Offset property

        :return: The external fix offset distance in nautical miles
        """
        return self._offset_nm

    # Make the offset_nm property immutable.
    @offset_nm.setter
    def offset_nm(self, offset_nm):
        raise Exception("offset_nm is immutable")


class IShape(SectorShape):

    def __init__(self, length_nm = LENGTH_NM, fix_names = None, route_names = None,
                 airway_width_nm = AIRWAY_WIDTH_NM, offset_nm = OFFSET_NM):

        if airway_width_nm > length_nm:
            raise ValueError(f'I sector width {airway_width_nm} must not exceed length {length_nm}')

        if fix_names is None:
            fix_names = self.i_fix_names

        if route_names is None:
            route_names = self.i_route_names

        # Set the polygon points
        points = [(-0.5 * airway_width_nm, -0.5 * length_nm),
                  (-0.5 * airway_width_nm, 0.5 * length_nm),
                  (0.5 * airway_width_nm, 0.5 * length_nm),
                  (0.5 * airway_width_nm, -0.5 * length_nm)]

        super(IShape, self).__init__(sector_type = SectorType.I,
                                     polygon = geom.Polygon(points),
                                     fix_names = fix_names,
                                     route_names = route_names,
                                     length_nm = length_nm,
                                     airway_width_nm = airway_width_nm,
                                     offset_nm = offset_nm)

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

    def routes(self):
        """
        Compute the valid routes through the sector.

        :return: A list of Route instances
        """

        # Order by increasing y-coordinate to get the "ascending" route.
        ascending_fix_list = sorted(list(self.fixes.items()), key = lambda item : item[1].coords[0][1])
        ascending_y = Route(
            name = self.route_names[0],
            fix_list = ascending_fix_list
        )
        # Reverse the order of fixes to get the "descending" route.
        descending_y = Route(
            name = self.route_names[1],
            fix_list = ascending_fix_list[::-1]
        )
        return [ascending_y, descending_y]

class XShape(SectorShape):

    def __init__(self, length_nm = LENGTH_NM, fix_names = None, route_names = None,
                 airway_width_nm = AIRWAY_WIDTH_NM, offset_nm = OFFSET_NM):

        if fix_names is None:
            fix_names = self.x_fix_names

        if route_names is None:
            route_names = self.x_route_names

        i = IShape(length_nm = length_nm, airway_width_nm = airway_width_nm, offset_nm = offset_nm)
        polygon = cascaded_union([i.polygon, rotate(i.polygon, 90)])

        super(XShape, self).__init__(sector_type = SectorType.X,
                                     polygon = polygon,
                                     fix_names = fix_names,
                                     route_names = route_names,
                                     length_nm = length_nm,
                                     airway_width_nm = airway_width_nm,
                                     offset_nm = offset_nm)

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

    def routes(self):
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
            name = self.route_names[0],
            fix_list = ascending_y_fix_list
        )
        descending_y = Route(
            name = self.route_names[1],
            fix_list = ascending_y_fix_list[::-1]
        )

        # Order by increasing x-coordinate to get the "ascending_x" route.
        ascending_x_fix_list = sorted(horizontal_fixes, key = lambda item : item[1].coords[0][0])
        ascending_x = Route(
            name = self.route_names[2],
            fix_list = ascending_x_fix_list
        )
        descending_x = Route(
            name = self.route_names[3],
            fix_list = ascending_x_fix_list[::-1]
        )

        return [ascending_y, descending_y, ascending_x, descending_x]

class YShape(SectorShape):

    def __init__(self, length_nm = LENGTH_NM, fix_names = None, route_names = None,
                 airway_width_nm = AIRWAY_WIDTH_NM, offset_nm = OFFSET_NM):

        if fix_names is None:
            fix_names = self.y_fix_names

        if route_names is None:
            route_names = self.y_route_names

        # Use an I shape of half length here, so Y sector scale matches that of I & X.
        i = IShape(length_nm = length_nm / 2, airway_width_nm = airway_width_nm, offset_nm = offset_nm)
        x_mid, y_mid = i.polygon.centroid.coords[0]
        x_min, y_min, x_max, y_max = i.polygon.bounds
        offset_polygon = cascaded_union([i.polygon, rotate(i.polygon, -120, origin=(x_mid, y_max)), rotate(i.polygon, 120, origin=(x_mid, y_max))])

        # Shift the polygon so its centre is at the origin.
        polygon = translate(offset_polygon, xoff = 0.0, yoff = - length_nm / 4)

        super(YShape, self).__init__(sector_type = SectorType.Y,
                                     polygon = polygon,
                                     fix_names = fix_names,
                                     route_names = route_names,
                                     length_nm = length_nm,
                                     airway_width_nm = airway_width_nm,
                                     offset_nm = offset_nm)

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

    def routes(self):
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
        left_ascending_y = Route(
            name = self.route_names[0],
            fix_list = left_ascending_y_fix_list
        )
        left_descending_y = Route(
            name = self.route_names[1],
            fix_list = left_ascending_y_fix_list[::-1]
        )

        right_ascending_y_fix_list = sorted(right_route_fixes, key = lambda item : item[1].coords[0][1])
        right_ascending_y = Route(
            name = self.route_names[2],
            fix_list = right_ascending_y_fix_list
        )
        right_descending_y = Route(
            name = self.route_names[3],
            fix_list = right_ascending_y_fix_list[::-1]
        )

        return [left_ascending_y, left_descending_y, right_ascending_y, right_descending_y]