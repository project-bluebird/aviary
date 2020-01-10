"""
Construction of I, X, Y airspace sector elements with upper & lower vertical limits.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from pyproj import Proj
from geojson import dump

from io import StringIO

from shapely.geometry import mapping, Point

import aviary.sector.sector_shape as ss
import aviary.parser.sector_parser as sp
from aviary.utils.geo_helper import GeoHelper
from aviary.utils.filename_helper import FilenameHelper

# DEFAULTS
DEFAULT_SECTOR_NAME = "SECTOR"
DEFAULT_ORIGIN = (-0.1275, 51.5)
DEFAULT_LOWER_LIMIT = 60
DEFAULT_UPPER_LIMIT = 460
FLOAT_PRECISION = 4

# CONSTANTS
ELLIPSOID = "WGS84"
GEOJSON_EXTENSION = "geojson"

# JSON keys
FEATURES_KEY = "features"
NAME_KEY = "name"
SHAPE_KEY = "shape"
ORIGIN_KEY = "origin"
TYPE_KEY = "type"
PROPERTIES_KEY = "properties"
LOWER_LIMIT_KEY = "lower_limit"
UPPER_LIMIT_KEY = "upper_limit"
ROUTES_KEY = "routes"
GEOMETRY_KEY = "geometry"
LATITUDE_KEY = "latitude"
LONGITUDE_KEY = "longitude"
LATITUDES_KEY = "latitudes"
LONGITUDES_KEY = "longitudes"
POINTS_KEY = "points"
CHILDREN_KEY = "children"
CHILDREN_NAMES_KEY = "names"

# JSON values
FEATURE_COLLECTION = "FeatureCollection"
FEATURE_VALUE = "Feature"
SECTOR_VALUE = "SECTOR"
FIX_VALUE = "FIX"
ROUTE_VALUE = "ROUTE"
SECTOR_VOLUME_VALUE = "SECTOR_VOLUME"
POLYGON_VALUE = "Polygon"
POINT_VALUE = "Point"

class SectorElement():
    """An elemental sector of airspace"""

    def __init__(self,
                 type,
                 name = DEFAULT_SECTOR_NAME,
                 origin = DEFAULT_ORIGIN,
                 lower_limit = DEFAULT_LOWER_LIMIT,
                 upper_limit = DEFAULT_UPPER_LIMIT,
                 **kwargs):
        """
        SectorElement constructor.

        :param type: a SectorType (enum)
        :param name: the name of the sector element
        :param origin: the origin coordinates as a (longitude, latitude) tuple
        :param lower_limit: the lower flight level limit
        :param upper_limit: the upper flight level limit
        """

        self.name = name
        self.origin = origin

        # Construct the proj-string (see https://proj.org/usage/quickstart.html)
        # Note the unit kmi is "International Nautical Mile" (for full list run $ proj -lu).
        proj_string = f'+proj=stere +lat_0={origin[1]} +lon_0={origin[0]} +k=1 +x_0=0 +y_0=0 +ellps={ELLIPSOID} +units=kmi +no_defs'

        self.projection = Proj(proj_string, preserve_units=True)

        # Construct the shape.
        f = ss.SectorShape.shape_constructor(type)
        shape = f(**kwargs)

        self.shape = shape
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit


    def polygon(self):
        """
        The sector polygon
        :return: a Shapely Polygon
        """

        return GeoHelper.__inv_project__(self.projection, geom=self.shape.polygon)

    def fix(self, fix_name):
        """The Point associated with a particular fix"""

        fixes = self.shape.fixes
        if not fix_name in list(fixes.keys()):
            raise ValueError(f'No fix exists named {fix_name}')

        return GeoHelper.__inv_project__(self.projection, geom = fixes[fix_name])


    def fix_location(self, fix_name):
        """The long/lat coordinates of a named fix"""

        return self.fix(fix_name).coords[0]

    def centre_point(self):
        """The long/lat coordinates of the centre point of the sector"""

        return self.polygon().centroid.coords[0]

    def routes(self):
        """Returns the valid routes through the sector

        Each route contains a list of fixes, and each fix is a (string, Point) pair
        where the string is the name of the fix and the Point is its geographical longitude-latitude coordinate.

        Note: the order of coordinates in a Point is longitude then latitude.

        :return: A list of Route instances.
        """

        # Return route objects.
        ret = self.shape.routes()
        for route in ret:
            route.projection = self.projection

        return ret


    @property
    def __geo_interface__(self) -> dict:
        """
        Implements the utils interface (see https://gist.github.com/sgillies/2217756#__geo_interface__)
        Returns a GeoJSON dictionary. For serialisation and deserialisation, use geojson.dumps and geojson.loads.
        """

        # Build the list of features: one for the boundary, one for each fix and one for each route.
        geojson = {TYPE_KEY: FEATURE_COLLECTION, FEATURES_KEY: []}
        geojson[FEATURES_KEY].append(self.sector_geojson())
        geojson[FEATURES_KEY].append(self.boundary_geojson())
        geojson[FEATURES_KEY].extend([route.geojson() for route in self.routes()])
        geojson[FEATURES_KEY].extend([self.waypoint_geojson(name) for name in self.shape.fixes.keys()])

        return geojson


    def hash_sector_coordinates(self, float_precision = FLOAT_PRECISION) -> str:
        """Returns hash of the sector boundary coordinates as string"""

        # Construct properly formatted coordinates before hashing.
        geojson = {
            GEOMETRY_KEY: mapping(self.polygon())
        }
        coords = GeoHelper.format_coordinates(geojson, key = GEOMETRY_KEY, float_precision = float_precision,
                                              as_geojson= False)
        return str(hash(tuple(coords)))


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
            - shape: "I", "X" or "Y"
            - origin: [long, lat]
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
                SHAPE_KEY: self.shape.sector_type.name,
                ORIGIN_KEY: self.origin,
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
            GEOMETRY_KEY: mapping(self.polygon()),
            PROPERTIES_KEY : {
                NAME_KEY: self.hash_sector_coordinates(),
                TYPE_KEY: SECTOR_VOLUME_VALUE,
                LOWER_LIMIT_KEY: self.lower_limit,
                UPPER_LIMIT_KEY: self.upper_limit,
                CHILDREN_KEY: {}
            }
        }

        geojson = GeoHelper.format_coordinates(geojson, key = GEOMETRY_KEY, float_precision = FLOAT_PRECISION)
        return geojson


    def contains(self, lon, lat, flight_level) -> bool:
        """
        Return a boolean indicating whether a point (lon, lat, flight_level) is inside the sector boundary.
        """

        point = Point(self.projection(lon, lat))
        return (
            self.shape.polygon.contains(point) and
            (self.lower_limit <= flight_level <= self.upper_limit)
            )


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
            GEOMETRY_KEY: mapping(self.fix(fix_name = name))
        }

        geojson = GeoHelper.format_coordinates(geojson, key = GEOMETRY_KEY, float_precision = FLOAT_PRECISION)
        return geojson


    def write_geojson(self, filename, path = "."):
        """Write the geojson object to a file"""

        file = FilenameHelper.construct_filename(filename=filename, desired_extension=GEOJSON_EXTENSION, path=path)

        with open(file, 'w') as f:
            dump(self, f, indent = 4)

        return file


    @staticmethod
    def deserialise(sector_geojson):
        """
        Deserialises a SectorElement instance from a GeoJSON.

        :param sector_geojson: Text stream from which a sector GeoJSON may be read.
        :return: a SectorElement instance
        """

        parser = sp.SectorParser(StringIO(sector_geojson))
        return SectorElement(type = parser.sector_type(),
                             name = parser.sector_name(),
                             origin = parser.sector_origin().coords[0],
                             lower_limit = parser.sector_lower_limit(),
                             upper_limit = parser.sector_upper_limit(),
                             fix_names = parser.fix_names(),
                             route_names = parser.route_names())




