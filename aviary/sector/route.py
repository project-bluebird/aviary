"""
Represents a route through a sector shape or element.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from shapely.geometry import LineString, mapping

import aviary.constants as C
from aviary.utils.geo_helper import GeoHelper

FIX_NAME_KEY = "fixName"

class Route():
    """A route through a sector.

    Each route is a list of fixes, and each fix is a (string, Point) pair
    where the string is the name of the fix and the Point is its x-y coordinate.

    Optionally a projection function may be included, in which case the instance
    represents a route through a (projected) sector element. If the projection
    attribute is None, the route is through a (flat, 2D) sector shape.

    """

    def __init__(self,
                fix_list):
                # projection = None):
        """
        Route class constructor.

        :param fix_list: A list of (str, shapely.point.Point) pairs
        :param projection: (optional) a pyproj Projection object
        """

        self.fix_list = fix_list
        # self.projection = projection


    def copy(self):
        """Returns a deep copy of a Route instance"""

        return Route(fix_list = self.fix_list.copy())#, projection = self.projection)


    def reverse(self):
        """Reverses the Route instance"""

        self.fix_list = self.fix_list[::-1]


    def length(self):
        """Returns the number of fixes in the route"""

        return len(self.fix_list)


    def fix_names(self):
        """Returns the names of the fixes in the route"""

        return [i[0] for i in self.fix_list]


    def fix_points(self):
        """Returns the coordinates of the fixes in the route"""

        # Project the coordinates unless the projection attribute is not None or unprojected is True.
        # if unprojected or self.projection is None:
        return [i[1] for i in self.fix_list]

        # return [GeoHelper.__inv_project__(self.projection, geom=i[1]) for i in self.fix_list]


    @property
    def __geo_interface__(self) -> dict:
        """
        Implements the utils interface (see https://gist.github.com/sgillies/2217756#__geo_interface__)
        Returns a GeoJSON dictionary. For serialisation and deserialisation, use geojson.dumps and geojson.loads.
        """
        return self.geojson()

    def hash_route(self) -> str:
        """Returns hash of the sector route (fix names)"""
        return str(hash(tuple(self.fix_names())))

    def geojson(self) -> dict:
        """
        Returns a GeoJSON dictionary representing the route

        A route includes elements:
        - type: "Feature"
        - geometry: a LineString feature whose properties are a list of points, with long/lat coordinates
        - properties:
           - name: e.g. "DAMNATION"
           - type: "ROUTE"
           - children: {"FIX": {"names": [<route fix names>]}}
        """

        geojson = {
            C.TYPE_KEY: C.FEATURE_VALUE,
            C.PROPERTIES_KEY: {
                C.NAME_KEY: self.hash_route(),
                C.TYPE_KEY: C.ROUTE_VALUE,
                C.CHILDREN_KEY: {
                    C.FIX_VALUE: {
                        C.CHILDREN_NAMES_KEY: self.fix_names()
                    }
                }
            },
            #TODO: remove transform AND figure out correct format (LINESTRING??)
            # C.GEOMETRY_KEY: mapping(GeoHelper.__inv_project__(self.projection,
            #     geom = LineString(self.fix_points(unprojected = True))))
            C.GEOMETRY_KEY: mapping(LineString(self.fix_points()))
        }

        # Format the coordinates.
        geojson = GeoHelper.format_coordinates(geojson, key = C.GEOMETRY_KEY, float_precision = C.FLOAT_PRECISION)
        return geojson


    def serialize(self):
        """Serialises the route instance as a JSON string"""

        return [
            {
                FIX_NAME_KEY: self.fix_names()[i],
                C.GEOMETRY_KEY: mapping(self.fix_points()[i])
            }
            for i in range(self.length())
        ]

    def next_waypoint(self, lat, lon):
        """ Returns the name of the next waypoint on the route (i.e. the fix to which the aircraft is currently heading)
        given a current position.

        :param lat: Current latitude
        :param lon: Current longitude
        :return: The name of the waypoint on the route, or None if the last waypoint is passed.
        """

        # Make a copy of the route to avoid side effects.
        truncated = self.copy()
        truncated.truncate(lat, lon)

        if truncated.length() == 0:
            return None

        return truncated.fix_names()[0]

    def truncate(self, initial_lat, initial_lon):
        """Truncates this route in light of a given start position by removing fixes that are already passed."""

        # if not self.projection:
        #     raise ValueError("Truncate route operation requires a non-empty projection attribute.")

        def fix_latitude(i):
            return self.fix_points()[i].coords[0][1]

        def fix_longitude(i):
            return self.fix_points()[i].coords[0][0]

        def distance_to_fix(i):
            return GeoHelper.distance(lat1=initial_lat, lon1=initial_lon, lat2=fix_latitude(i), lon2=fix_longitude(i))

        # Handle the case that the aircraft has passed the final fix (using only distances!).
        distance_to_final_fix = distance_to_fix(-1)
        distance_to_penultimate_fix = distance_to_fix(-2)
        distance_between_final_fixes = GeoHelper.distance(lat1=fix_latitude(-1), lon1 = fix_longitude(-1),
                                                          lat2=fix_latitude(-2), lon2 = fix_longitude(-2))

        if distance_to_final_fix < distance_to_penultimate_fix and distance_to_penultimate_fix > distance_between_final_fixes:
            self.fix_list = []
            return

        # Retain only those route elements that are closer to the final fix than the initial position.
        final_lon, final_lat = self.fix_points()[-1].coords[0]  # Note lon/lat order!
        self.fix_list = [self.fix_list[i] for i in range(self.length()) if
                         GeoHelper.distance(lat1 = final_lat, lon1 = final_lon, lat2 = fix_latitude(i), lon2 = fix_longitude(i)) <
                         GeoHelper.distance(lat1 = final_lat, lon1 = final_lon, lat2 = initial_lat, lon2 = initial_lon)]
