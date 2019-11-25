"""
Construction of I, X, Y airspace sector elements with upper & lower vertical limits.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from pyproj import Proj

from shapely.ops import transform
from shapely.geometry import LineString

from functools import partial

from geojson import dump

import os.path

from aviary.geo.geo_helper import GeoHelper

# CONSTANTS
ELLIPSOID = "WGS84"
GEOJSON_EXTENSION = "geojson"

# JSON keys
FEATURES_KEY = "features"
NAME_KEY = "name"
TYPE_KEY = "type"
PROPERTIES_KEY = "properties"
LOWER_LIMIT_KEY = "lower_limit"
UPPER_LIMIT_KEY = "upper_limit"
ROUTES_KEY = "routes"
GEOMETRY_KEY = "geometry"
COORDINATES_KEY = "coordinates"
LATITUDE_KEY = "latitude"
LONGITUDE_KEY = "longitude"
LATITUDES_KEY = "latitudes"
LONGITUDES_KEY = "longitudes"
POINTS_KEY = "points"
CHILDREN_KEY = "children"
CHILDREN_NAMES_KEY = "names"

# JSON values
FEATURE_VALUE = "Feature"
SECTOR_VALUE = "SECTOR"
FIX_VALUE = "FIX"
ROUTE_VALUE = "ROUTE"
SECTOR_VOLUME_VALUE = "SECTOR_VOLUME"
POLYGON_VALUE = "Polygon"
POINT_VALUE = "Point"

class SectorElement():
    """An elemental sector of airspace"""

    def __init__(self, name, origin, shape, lower_limit, upper_limit):

        self.name = name

        # Construct the proj-string (see https://proj.org/usage/quickstart.html)
        # Note the unit kmi is "International Nautical Mile" (for full list run $ proj -lu).
        proj_string = f'+proj=stere +lat_0={origin[0]} +lon_0={origin[1]} +k=1 +x_0=0 +y_0=0 +ellps={ELLIPSOID} +units=kmi +no_defs'

        self.projection = Proj(proj_string, preserve_units=True)
        self.shape = shape
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def centre_point(self):
        """The lat/lon coordinates of the centre point of the sector"""

        return tuple(i for i in reversed(self.__inv_project__(self.shape.polygon.centroid).coords[0]))

    def fix_location(self, fix_name):
        """The lat/lon coordinates of a named fix"""

        fixes = self.shape.fixes
        if not fix_name in list(fixes.keys()):
            raise ValueError(f'No fix exists named {fix_name}')

        return tuple(i for i in reversed(self.__inv_project__(fixes[fix_name]).coords[0]))

    def routes(self):
        """Returns the valid routes through the sector

        Each route is a list of fixes, and each fix is a (string, Point) pair
        where the string is the name of the fix and the Point is its geographical longitude-latitude coordinate.

        Note: the order of coordinates in a Point is longitude then latitude.
        """

        shape_routes = self.shape.routes()
        return [[(i[0], self.__inv_project__(i[1])) for i in route] for route in shape_routes]

    @staticmethod
    def truncate_route(route, initial_lat, initial_lon):
        """Truncates a route in light of a given start position by removing fixes that are already passed."""

        # Retain only those route elements that are closer to the final fix than the start_position.
        final_lon, final_lat = route[-1][1].coords[0] # Note lon/lat order!
        return [i for i in route if GeoHelper.distance(final_lat, final_lon, i[1].coords[0][1], i[1].coords[0][0]) <
                GeoHelper.distance(final_lat, final_lon, initial_lat, initial_lon)]

    @property
    def __geo_interface__(self) -> dict:
        """
        Implements the geo interface (see https://gist.github.com/sgillies/2217756#__geo_interface__)
        Returns a GeoJSON dictionary. For serialisation and deserialisation, use geojson.dumps and geojson.loads.
        """

        # Build the list of features: one for the boundary, one for each fix and one for each route.
        geojson = {FEATURES_KEY: []}
        geojson[FEATURES_KEY].append(self.sector_geojson())
        geojson[FEATURES_KEY].append(self.boundary_geojson())
        geojson[FEATURES_KEY].extend([self.route_geojson(route_index) for route_index in range(0, len(self.shape.route_names))])
        geojson[FEATURES_KEY].extend([self.waypoint_geojson(name) for name in self.shape.fixes.keys()])

        return geojson

    def hash_sector_coordinates(self) -> str:
        """Returns hash of the sector boundary coordinates as string"""
        return str(hash(self.__inv_project__(self.shape.polygon).__geo_interface__[COORDINATES_KEY][0]))

    def sector_geojson(self) -> dict:
        """
        Return a GeoJSON dictionary representing the sector. The sector has an
        associated sector volume (child property) that describes the sector boundaries.
        The ID of the sector volume is a hash of the sector coordinates.

        A sector includes elements:
        - type: "Feature"
        - geometry: {}
        - properties:
            - name: e.g. "HELL"
            - type: "SECTOR"
            - children: {
                "SECTOR_VOLUME": {"names": [<hash of sector boundary coordinates>]},
                "ROUTE":{"names": [<shape route names>]}
                }
        """

        geojson = {
            TYPE_KEY: FEATURE_VALUE,
            PROPERTIES_KEY: {
                NAME_KEY: self.name,
                TYPE_KEY: SECTOR_VALUE,
                CHILDREN_KEY: {
                    SECTOR_VOLUME_VALUE : {CHILDREN_NAMES_KEY: [self.hash_sector_coordinates()]},
                    ROUTE_VALUE: {CHILDREN_NAMES_KEY: self.shape.route_names}
                }
            },
            GEOMETRY_KEY: {}
        }

        return geojson

    def boundary_geojson(self) -> dict:
        """
        Return a GeoJSON dictionary representing the sector boundary (volume).

        A sector volume includes elements:
        - type: "Feature"
        - geometry: A Polygon feature whore properties are a list of long/lat coordinates defining the sector boundaries
        - properties:
            - name: ID derived from hashing the volume's coordinates
            - type: "SECTOR_VOLUME"
            - lower_limit: e.g. 150
            - upper_limit: e.g. 400
            - children: {}
        """

        geojson = {
            TYPE_KEY : FEATURE_VALUE,
            GEOMETRY_KEY : self.__inv_project__(self.shape.polygon).__geo_interface__,
            PROPERTIES_KEY : {
                NAME_KEY: self.hash_sector_coordinates(),
                TYPE_KEY: SECTOR_VOLUME_VALUE,
                LOWER_LIMIT_KEY: self.lower_limit,
                UPPER_LIMIT_KEY: self.upper_limit,
                CHILDREN_KEY: {}
            }
        }

        geojson = self.fix_geometry_coordinates_tuple(geojson)
        return geojson


    def waypoint_geojson(self, name) -> dict:
        """
        Return a GeoJSON dictionary representing the waypoints (fixes)

        A waypoint includes elements:
        - type: "Feature"
        - geometry: a Point feature with a list of long/lat coordinates
        - properties:
            - name: e.g. "LIMBO"
            - type: "FIX"
        """

        geojson = {
            TYPE_KEY: FEATURE_VALUE,
            PROPERTIES_KEY: {
                NAME_KEY: name.upper(),
                TYPE_KEY: FIX_VALUE
            },
            GEOMETRY_KEY: self.__inv_project__(self.shape.fixes[name]).__geo_interface__
        }

        geojson = self.fix_geometry_coordinates_tuple(geojson)
        return geojson

    def route_geojson(self, route_index) -> dict:
        """
        Returns a GeoJSON dictionary representing a route

        :param route_index: the list index of the route within self.shape.routes()

        A route includes elements:
        - type: "Feature"
        - geometry: a LineString feature whose properties are a list of points, with long/lat coordinates
        - properties:
           - name: e.g. "DAMNATION"
           - type: "ROUTE"
           - children: {"FIX": {"names": [<route fix names>]}}
        """

        route = self.shape.routes()[route_index]
        fix_names = [fix_item[0] for fix_item in route]
        geojson = {
            TYPE_KEY: FEATURE_VALUE,
            PROPERTIES_KEY: {
                NAME_KEY: self.shape.route_names[route_index],
                TYPE_KEY: ROUTE_VALUE,
                CHILDREN_KEY: {
                    FIX_VALUE: {
                        CHILDREN_NAMES_KEY: fix_names
                    }
                }
            },
            GEOMETRY_KEY: self.__inv_project__(LineString([fix_item[1] for fix_item in route])).__geo_interface__
        }

        # Fix issue with __geo_interface__ unexpectedly returning a tuple of coordinates rather than a list.
        geojson = self.fix_geometry_coordinates_tuple(geojson)
        return geojson

    def fix_geometry_coordinates_tuple(self, geojson):
        """Works around an issue with __geo_interface__ unexpectedly returning a tuple of coordinates rather than a list"""

        geojson[GEOMETRY_KEY][COORDINATES_KEY] = list(geojson[GEOMETRY_KEY][COORDINATES_KEY])
        return geojson

    def __inv_project__(self, geom):
        """Helper for doing an inverse geometric projection"""

        return transform(partial(self.projection, inverse=True), geom)

    def write_geojson(self, filename, path = "."):
        """Write the geojson object to a file"""

        extension = os.path.splitext(filename)[1]
        if extension.upper() != GEOJSON_EXTENSION:
            filename = filename + "." + GEOJSON_EXTENSION

        file = os.path.join(path, filename)

        with open(file, 'w') as f:
            dump(self, f, indent = 4)

        return file
