"""
Helper class for computing geometric and geographic quantities.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from geographiclib.geodesic import Geodesic

class GeoHelper():
    """Helper class containing geometric and geographic functions"""

    @staticmethod
    def waypoint_location(lat1, lon1, lat2, lon2, distance_m, geod = Geodesic.WGS84):
        """
        Computes the location of waypoint at a given distance (in metres) between two points.
        Based on the example at https://geographiclib.sourceforge.io/html/python/examples.html#computing-waypoints
        """

        l = geod.InverseLine(lat1, lon1, lat2, lon2)
        s = min(distance_m, l.s13)
        g = l.Position(s, Geodesic.STANDARD)
        return g['lat2'], g['lon2']


    @staticmethod
    def distance(lat1, lon1, lat2, lon2, geod = Geodesic.WGS84):
        """
        Computes the distance in metres between two geographic points.
        Based on the example at https://geographiclib.sourceforge.io/html/python/examples.html#basic-geodesic-calculations
        """

        g = geod.Inverse(lat1, lon1, lat2, lon2)
        return g['s12']