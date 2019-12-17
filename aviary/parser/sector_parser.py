"""
Sector (GeoJSON) parser.
"""

import aviary.sector.sector_element as se
import aviary.geo.geo_helper as gh

import geojson
import jsonpath_rw_ext as jp

import shapely.geometry as geom

class SectorParser:
    """A parser of GeoJSON sectors """

    def __init__(self, sector_geojson):
        """
        Sector parser constructor.

        :param sector_geojson: Text stream from which a sector GeoJSON may be read.
        """

        # Decode the sector geoJSON strings.
        sector = geojson.load(sector_geojson)

        if se.FEATURES_KEY not in sector:
            raise ValueError(f"Sector geojson must contain {se.FEATURES_KEY} element")

        self.sector = sector

    def features_of_type(self, type_value):
        """
        Filters the features to retain those whose 'type', inside a 'properties' element, matches the given type_value.
        Returns a list of features dictionaries.
        """

        return jp.match(
            f"$..{se.FEATURES_KEY}[?@.{se.PROPERTIES_KEY}.{se.TYPE_KEY}=={type_value}]",
            self.sector,
        )

    def fix_features(self):
        """
        Filters the features to retain those with 'type': 'FIX'.
        Returns a list of dictionaries.
        """

        return self.features_of_type(type_value=se.FIX_VALUE)

    def properties_of_type(self, type_value):
        """
        Filters the features to retain those whose 'type', inside a 'properties' element, matches the given type_value.
        Returns a list of properties dictionaries.
        """

        return jp.match(
            f"$..{se.FEATURES_KEY}[?@.{se.PROPERTIES_KEY}.{se.TYPE_KEY}=={type_value}].{se.PROPERTIES_KEY}",
            self.sector,
        )

    def sector_volume_properties(self):
        """
        Filters the features to retain properties of those with 'type': 'SECTOR_VOLUME'.
        Returns a list of dictionaries.
        """

        return self.properties_of_type(type_value=se.SECTOR_VOLUME_VALUE)

    def geometries_of_type(self, type_value):
        """
        Filters the features to retain those whose 'type', inside a 'geometry' element, matches the given type_value.
        Returns a list of geometries dictionaries.
        """

        return jp.match(
            f"$..{se.FEATURES_KEY}[?@.{se.GEOMETRY_KEY}.{se.TYPE_KEY}=={type_value}].{se.GEOMETRY_KEY}",
            self.sector,
        )

    def polygon_geometries(self):
        """
        Filters the features to retain geometries of those with 'type': 'Polygon'.
        Returns a list of dictionaries.
        """

        return self.geometries_of_type(type_value=se.POLYGON_VALUE)

    def sector_polygon(self):
        """
        Returns a dictionary containing the coordinates of the sector polygon.
        """

        polygons = self.polygon_geometries()
        if len(polygons) != 1:
            raise Exception(
                f"Expected precisely one polygon; found {len(polygons)} polygons."
            )
        return polygons[0]

    def sector_name(self):
        """
        Returns the sector name.
        """

        return self.properties_of_type(type_value=se.SECTOR_VALUE)[0][se.NAME_KEY]

    def sector_centroid(self):
        """
        Returns the centroid of the sector polygon.
        :return: a shapely.geometry.point.Point object representing the centroid of the sector.
        """

        # Determine the centroid of the sector polygon.
        coords = self.sector_polygon()[gh.COORDINATES_KEY]

        while len(coords) == 1:
            coords = coords[0]

        polygon = geom.Polygon(coords)
        return polygon.centroid
