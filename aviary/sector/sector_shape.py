"""
Construction of 2D polygons (including I, X, Y shapes) for use as
cross-sections of airspace sector elements.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import os
from enum import Enum
from pyproj import Proj

import pandas as pd
import shapely.geometry as geom
from shapely.ops import cascaded_union
from shapely.affinity import rotate, translate
from abc import abstractmethod

import aviary.constants as C
from aviary.sector.route import Route
from aviary.utils.geo_helper import GeoHelper
from aviary.utils.airtools import *

# Default sector dimensions:
LENGTH_NM = 50
AIRWAY_WIDTH_NM = 10
OFFSET_NM = 10

EPSILON = 1e-10 # Small number used as a tolerance when determining routes.


class SectorShape:

    def format_fixes(self, fix_names, fix_points):
        """
        Format fixes.

        :param fix_names: list of str
        :param fix_points: list of geom.Point
        """
        if len(fix_names) != len(fix_points):
            raise ValueError(f'fix_names must have length {len(fix_points)}')
        return dict(zip([fix_name.upper() for fix_name in fix_names], fix_points))

    def format_route(self, fix_list):
        """
        Format route from list of fixes to a Route instance.

        :param route: list of (str, geom.Point)
        :return: A Route class instance
        """
        return Route(fix_list = fix_list)

    def get_routes_connectivity():
        pass

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
    """A 2D sector shape with waypoint fixes

    :param polygon: geom.polygon.BaseGeometry
    :param fix_names: list of str
    :param fix_points: list of geom.Point
    :param routes: list of lists of (str, geom.Point)
    """

    def __init__(self, polygon, fix_names, fix_points, routes,
                       sector_type='',
                       lower_limit = C.DEFAULT_LOWER_LIMIT,
                       upper_limit = C.DEFAULT_UPPER_LIMIT,):

        self._polygon = polygon
        self._fixes = self.format_fixes(fix_names, fix_points)
        self._routes = [self.format_route(route) for route in routes]
        self.sector_type = sector_type
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

class ConstructShape(SectorShape):

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

    # X routes: 1) vertical increasing in y-coordinate 2) vertical descreasing in y-coordinate
    #           3) horizontal increasing in x-coordinate 4) horizontal descreasing in x-coordinate


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

    def __init__(self, sector_type, lower_limit = C.DEFAULT_LOWER_LIMIT,
                upper_limit = C.DEFAULT_UPPER_LIMIT,length_nm = LENGTH_NM,
                airway_width_nm = AIRWAY_WIDTH_NM, offset_nm = OFFSET_NM,
                fix_names = None, origin = C.DEFAULT_ORIGIN):

        assert sector_type == "I" or sector_type == "X" or sector_type == "Y", f"Unsupported sector type: {sector_type}, choose one of 'I', 'X' or 'Y'"

        self.sector_type = sector_type
        self.length_nm = length_nm
        self.airway_width_nm = airway_width_nm
        self.offset_nm = offset_nm
        self.origin = origin
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

        proj_string = f'+proj=stere +lat_0={self.origin[1]} +lon_0={self.origin[0]} +k=1 +x_0=0 +y_0=0 +ellps={C.ELLIPSOID} +units=kmi +no_defs'
        self.projection = Proj(proj_string)

        if self.sector_type == "I":
            if airway_width_nm > length_nm:
                raise ValueError(f'I sector width {airway_width_nm} must not exceed length {length_nm}')
            if fix_names is None:
                fix_names = self.i_fix_names
            polygon = self.i_shape()
            fix_points = self.i_fix_points(polygon)
            routes = self.i_routes(dict(zip(fix_names, fix_points)))

        elif self.sector_type == "X":
            if fix_names is None:
                fix_names = self.x_fix_names
            polygon = self.x_shape()
            fix_points = self.x_fix_points(polygon)
            routes = self.x_routes(dict(zip(fix_names, fix_points)))

        elif self.sector_type == "Y":
            if fix_names is None:
                fix_names = self.y_fix_names
            polygon = self.y_shape()
            fix_points = self.y_fix_points(polygon)
            routes = self.y_routes(dict(zip(fix_names, fix_points)))

        # apply projection before saving
        self._polygon = self.transform(polygon)
        transform_fixes = [self.transform(fix) for fix in fix_points]
        self._fixes = self.format_fixes(fix_names, transform_fixes)
        transform_routes = []
        for route in routes:
            transform_route = [(fix[0].upper(), self.transform(fix[1])) for fix in route]
            transform_routes.append(transform_route)
        self._routes = [self.format_route(route) for route in transform_routes]

    def transform(self, geom):
        """
        Project geom (Polygon or Point)
        """

        return GeoHelper.__inv_project__(self.projection, geom=geom)

    def i_shape(self, airway_width_nm=None, length_nm=None):
        """
        I shaped polygon
        """
        if airway_width_nm is None:
            airway_width_nm = self.airway_width_nm
        if length_nm is None:
            length_nm = self.length_nm
        points = [(-0.5 * airway_width_nm, -0.5 * length_nm),
                  (-0.5 * airway_width_nm, 0.5 * length_nm),
                  (0.5 * airway_width_nm, 0.5 * length_nm),
                  (0.5 * airway_width_nm, -0.5 * length_nm)]
        return geom.Polygon(points)

    def x_shape(self):
        """
        X shaped polygon
        """
        return cascaded_union([self.i_shape(), rotate(self.i_shape(), 90)])

    def y_shape(self):
        """
        Y shaped polygon
        """
        i_shape = self.i_shape(length_nm = self.length_nm / 2, airway_width_nm = self.airway_width_nm)
        x_mid, y_mid = i_shape.centroid.coords[0]
        x_min, y_min, x_max, y_max = i_shape.bounds
        offset_polygon = cascaded_union([i_shape, rotate(i_shape, -120, origin=(x_mid, y_max)), rotate(i_shape, 120, origin=(x_mid, y_max))])

        # Shift the polygon so its centre is at the origin.
        return translate(offset_polygon, xoff = 0.0, yoff = - self.length_nm / 4)

    def i_fix_points(self, polygon):
        """Compute the locations of the I fixes"""

        x_min, y_min, x_max, y_max = polygon.bounds
        x_mid, y_mid = polygon.centroid.coords[0]

        fix_points = [geom.Point(x_mid, y_max + self.offset_nm), # top exterior
                  geom.Point(x_mid, y_max), # top
                  geom.Point(x_mid, y_mid), # middle
                  geom.Point(x_mid, y_min), # bottom
                  geom.Point(x_mid, y_min - self.offset_nm)] # bottom exterior

        return fix_points

    def x_fix_points(self, polygon):
        """Compute the locations of the X fixes"""

        x_mid, y_mid = polygon.centroid.coords[0]
        x_min, y_min, x_max, y_max = polygon.bounds

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

    def y_fix_points(self, polygon):
        """Compute the locations of the Y fixes"""

        coords = list(polygon.exterior.coords)
        xy_min, xy_max = self.__minmax_xy__(coords)
        xmin, ymin = xy_min
        bottom = self.__get_centre__([geom.Point(pt) for pt in self.__get_coords__(coords, xmin)])
        bottom = geom.Point(polygon.centroid.coords[0][0], bottom.coords[0][1])
        _x, _y = bottom.coords[0]
        bottom_outer = geom.Point(_x, _y - self.offset_nm)

        origin = polygon.centroid
        fix_points = [rotate(bottom_outer, angle=-120, origin=origin), # left exterior
                      rotate(bottom, -120, origin=origin), # left
                      rotate(bottom_outer, angle=120, origin=origin), # right exterior
                      rotate(bottom, 120, origin=origin), # right
                      origin, # middle
                      bottom, # bottom
                      bottom_outer] # bottom exterior

        return fix_points

    def i_routes(self, fixes):
        """
        Compute the valid routes through the I sector.

        :return: A list of Route instances
        """

        # Order by increasing y-coordinate to get the "ascending" route.
        ascending_fix_list = sorted(list(fixes.items()), key = lambda item : item[1].coords[0][1])

        return [ascending_fix_list, ascending_fix_list[::-1]]

    def x_routes(self, fixes):
        """
        Compute the valid routes through the X sector.

        :return: A list of Route instances
        """

        # Get the fixes on the vertical line (i.e. with zero x coordinate).
        vertical_fixes = list(filter(lambda item : abs(item[1].coords[0][0]) < EPSILON, fixes.items()))
        # Get the fixes on the horizontal line (i.e. with zero y coordinate).
        horizontal_fixes = list(filter(lambda item : abs(item[1].coords[0][1]) < EPSILON, fixes.items()))

        # Order by increasing y-coordinate to get the "ascending_y" route.
        ascending_y_fix_list = sorted(vertical_fixes, key = lambda item : item[1].coords[0][1])
        # Order by increasing x-coordinate to get the "ascending_x" route.
        ascending_x_fix_list = sorted(horizontal_fixes, key = lambda item : item[1].coords[0][0])

        return [ascending_y_fix_list, ascending_y_fix_list[::-1],
                ascending_x_fix_list, ascending_x_fix_list[::-1]]

    def y_routes(self, fixes):
        """
        Compute the valid routes through the Y sector.

        :return: A list of Route instances
        """

        # Get the fixes on the vertical line (i.e. with zero x coordinate).
        vertical_fixes = list(filter(lambda item : abs(item[1].coords[0][0]) < EPSILON, fixes.items()))

        # Get the fixes on the left arm, possibly including the vertical fixes.
        all_left_fixes = list(filter(lambda item : item[1].coords[0][0] < 0, fixes.items()))

        # Get the fixes strictly on the left arm (not including the vertical fixes).
        left_fixes = list(filter(lambda item : item[0] not in [it[0] for it in vertical_fixes], all_left_fixes))

        # Get the fixes in the route along the left arm.
        left_route_fixes = vertical_fixes
        left_route_fixes.extend(left_fixes)

        # Get the fixes in the route along the right arm.
        right_route_fixes = list(filter(lambda item : item[0] not in [it[0] for it in left_fixes], fixes.items()))

        # Order by increasing y-coordinate to get the "ascending_y" route.
        left_ascending_y_fix_list = sorted(left_route_fixes, key = lambda item : item[1].coords[0][1])
        right_ascending_y_fix_list = sorted(right_route_fixes, key = lambda item : item[1].coords[0][1])

        return [left_ascending_y_fix_list, left_ascending_y_fix_list[::-1],
                right_ascending_y_fix_list, right_ascending_y_fix_list[::-1]]

    def create_fixes(self, fix_names, fix_points):
        if len(fix_names) != len(fix_points):
            raise ValueError(f'fix_names must have length {len(fix_points)}')
        return dict(zip([fix_name.upper() for fix_name in fix_names],
                                [self.transform(fix) for fix in fix_points]))

    def __minmax_xy__(self, coords):
        min_x, min_y = min([y for x, y in coords]), min([x for x, y in coords])
        max_x, max_y = max([y for x, y in coords]), max([x for x, y in coords])
        return [(min_x, min_y), (max_x, max_y)]

    def __get_coords__(self, coords, match):
        return [(x, y) for x, y in coords if x == match or y == match]

    def __get_centre__(self, coords):
        return geom.Point(geom.GeometryCollection(coords).centroid.coords[0])


class RealWorldShape(SectorShape):

    def __init__(self, sector_name, sector_part=1, boundary_limit=0.25,
                    sectors_path='sectors.csv', waypoints_path='waypoints.csv',
                    routes_path=None):

        self._sector_type = sector_name
        sector, floor, ceil = self.load_sector(sectors_path, sector_name, sector_part)
        self._polygon = sector
        self.lower_limit = floor
        self.upper_limit = ceil

        all_waypoints = self.load_waypoints(waypoints_path)
        sector_bbox = self.make_bound_box(sector, boundary_limit)
        # load waypoints which are inside the sector bounding box
        fix_names, fix_points = self.get_boundary_waypoints(sector_bbox, all_waypoints)
        self._fixes = self.format_fixes(fix_names, fix_points)

        if routes_path:
            all_routes = self.load_routes(routes_path)
            routes = self.get_boundary_routes(all_routes, fix_names)
            self._routes = [self.format_route(route) for route in routes]
        else:
            self._routes = []

    def load_sector(self, file_path, sector_name, sector_part):

        sectors = pd.read_csv(file_path)
        sector_polygon = sectors[(sectors['sectorname'] == sector_name) &
                        (sectors['part'] == sector_part)]
        sector_polygon['geometry'] = sector_polygon['vertices_deg_min_sec'].apply(extract_polygon)

        return sector_polygon[['geometry', 'floor_fl', 'ceiling_fl']].values[0]

    def load_waypoints(self, file_path):

        wpts = pd.read_csv(file_path)
        wpts['lat_dd'] = wpts['lat'].apply(decimal_degrees)
        wpts['long_dd'] = wpts['long'].apply(decimal_degrees)
        wpts['geometry'] = [geom.Point(lon,lat) for lon,lat in zip(wpts['long_dd'], wpts['lat_dd'])]
        fix_dict = wpts.set_index('waypointname')['geometry'].to_dict()

        return fix_dict

    def load_routes(self, file_path):

        return pd.read_csv(file_path)

    def make_bound_box(self, sector_polygon, boundlim):
        """
        Take in an arbitary sector shape (polygon with long and lat)
        Output a bounding quadrilateral based on polygon boundaries.
        Buffer zone is calculated in degrees.
        """

        bounding_box = list(sector_polygon.bounds)
        op_bb = geom.box(bounding_box[0]-boundlim,
                         bounding_box[1]-boundlim,
                         bounding_box[2]+boundlim,
                         bounding_box[3]+boundlim)
        return op_bb

    def get_boundary_waypoints(self, boundary_polygon, waypoints):
        """
        Return all waypoints (fix_names, fix_points) in a given boundary polygon.
        """
        boundary_waypoints = {}
        for wpt_name, wpt_pos in waypoints.items():
            if boundary_polygon.contains(wpt_pos) or boundary_polygon.intersects(wpt_pos):
                boundary_waypoints[wpt_name]=wpt_pos
        boundary_fix_names = list(boundary_waypoints.keys())
        boundary_fix_points = list(boundary_waypoints.values())
        return boundary_fix_names, boundary_fix_points

    def get_boundary_routes(self, routes, fix_names):
        """
        Read and load all routes data and output those that pass through any of
        the fix_names (where fix_names are fixes within some boundary region of interest).
        Return each route as a list of (str, shapely.point.Point) pairs
        """
        if len(fix_names) == 0:
            raise ValueError(f'There are no waypoints within the specified boundary')

        # routes that pass through the sector
        full_routes = routes[routes['Route_Points'].str.contains("|".join(fix_names), regex=True)]
        bounded_routes = []
        for route in full_routes['Route_Points'].str.split(";").to_list():
            route_fix_names = [wpt for wpt in route if wpt in fix_names]
            fix_points = [self._fixes[fix] for fix in route_fix_names]
            fix_list = list(zip(route_fix_names, fix_points))
            bounded_routes.append(fix_list)
        return bounded_routes
