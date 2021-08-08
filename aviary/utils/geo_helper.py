"""
Helper class for computing geometric and geographic quantities.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from shapely.geometry import Point
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
    def format_coordinates(geojson, key, float_precision, as_geojson = True):
        """
        Formats coordinates to apply a given float precision and work around an
        issue with __geo_interface__ unexpectedly returning a tuple of coordinate
        pairs rather than a list, which breaks deserialisation via geojson.load.
        """

        if not key in geojson:
            raise ValueError(f'Key {key} not found in geojson: {geojson}')

        # Ensure the coordinates are in a list, not a tuple.
        coords = list(geojson[key][COORDINATES_KEY])

        # Coordinates list may be nested.
        nested = False
        while (isinstance(coords, list) and len(coords) == 1):
            coords = coords[0]
            nested = True

        # Round to the given float precision, handling separately the cases of
        # a single coordinate pair versus a list of coordinate pairs.
        if isinstance(coords[0], float):
            rounded = tuple(round(num, float_precision) for num in coords)
        else:
            rounded = [tuple(round(num, float_precision) for num in longlat) for longlat in coords]

        if not as_geojson:
            return rounded

        # Wrap in a nested list as per GeoJSON spec:
        # http://wiki.geojson.org/GeoJSON_draft_version_6#Polygon
        if nested:
            geojson_element = []
            geojson_element.append(rounded)
        else:
            geojson_element = rounded

        geojson[key][COORDINATES_KEY] = geojson_element
        return geojson


    @staticmethod
    def waypoint_location(lat1, lon1, lat2, lon2, distance_m, geod = Geodesic.WGS84):
        """
        Computes the location of waypoint at a given distance (in metres) from
        point (lat1, lon1) in the direction of (lat2, lon2). Returns a Shapely Point.

        Based on the example at https://geographiclib.sourceforge.io/html/python/examples.html#computing-waypoints
        """

        l = geod.InverseLine(lat1, lon1, lat2, lon2)
        g = l.Position(distance_m, Geodesic.STANDARD)

        return Point(g['lon2'], g['lat2'])


    @staticmethod
    def distance(lat1, lon1, lat2, lon2, geod = Geodesic.WGS84):
        """
        Computes the distance in metres between two geographic points.

        Based on the example at https://geographiclib.sourceforge.io/html/python/examples.html#basic-geodesic-calculations
        """

        g = geod.Inverse(lat1, lon1, lat2, lon2)
        return g['s12']