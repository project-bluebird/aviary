"""
Helper class for computing geometric and geographic quantities.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from shapely.ops import transform
from functools import partial

from geographiclib.geodesic import Geodesic

COORDINATES_KEY = "coordinates"

class GeoHelper():
    """Helper class containing geometric and geographic functions"""

    @staticmethod
    def __inv_project__(projection, geom):
        """Helper for doing an inverse geometric projection"""

        return transform(partial(projection, inverse=True), geom)


    @staticmethod
    def fix_geometry_coordinates_tuple(geojson, key):
        """
        Works around an issue with __geo_interface__ unexpectedly returning a
        tuple of coordinates rather than a list.
        """

        if not key in geojson:
            raise ValueError(f'Key {key} not found in geojson: {geojson}')

        geojson[key][COORDINATES_KEY] = list(geojson[key][COORDINATES_KEY])
        return geojson


    @staticmethod
    def waypoint_location(lat1, lon1, lat2, lon2, distance_m, geod = Geodesic.WGS84):
        """
        Computes the location of waypoint at a given distance (in metres) from
        point (lat1, lon1) in the direction of (lat2, lon2).

        Based on the example at https://geographiclib.sourceforge.io/html/python/examples.html#computing-waypoints
        """

        l = geod.InverseLine(lat1, lon1, lat2, lon2)
        g = l.Position(distance_m, Geodesic.STANDARD)
        return g['lon2'], g['lat2']


    @staticmethod
    def distance(lat1, lon1, lat2, lon2, geod = Geodesic.WGS84):
        """
        Computes the distance in metres between two geographic points.

        Based on the example at https://geographiclib.sourceforge.io/html/python/examples.html#basic-geodesic-calculations
        """

        g = geod.Inverse(lat1, lon1, lat2, lon2)
        return g['s12']