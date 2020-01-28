"""
Sector (GeoJSON) parser.
"""

import aviary.constants as C
import aviary.sector.sector_shape as ss
import aviary.sector.sector_element as se
import aviary.utils.geo_helper as gh

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

        if C.FEATURES_KEY not in sector:
            raise ValueError(f"Sector geojson must contain {C.FEATURES_KEY} element")

        self.sector = sector

    def features_of_type(self, type_value):
        """
        Filters the features to retain those whose 'type', inside a 'properties' element, matches the given type_value.
        Returns a list of features dictionaries.
        """

        return jp.match(
            f"$..{C.FEATURES_KEY}[?@.{C.PROPERTIES_KEY}.{C.TYPE_KEY}=={type_value}]",
            self.sector,
        )

    def properties_of_type(self, type_value):
        """
        Filters the features to retain those whose 'type', inside a 'properties' element, matches the given type_value.
        Returns a list of properties dictionaries.
        """

        return jp.match(
            f"$..{C.FEATURES_KEY}[?@.{C.PROPERTIES_KEY}.{C.TYPE_KEY}=={type_value}].{C.PROPERTIES_KEY}",
            self.sector,
        )

    def fix_features(self):
        """
        Filters the features to retain those with 'type': 'FIX'.
        Returns a list of dictionaries.
        """

        return self.features_of_type(type_value=C.FIX_VALUE)

    def fix_names(self):
        """
        Returns the names of the fixes in the sector as a list of strings.
        """

        return [p[C.NAME_KEY] for p in self.properties_of_type(type_value=C.FIX_VALUE)]

    def route_names(self):
        """
        Returns the names of the routes in the sector as a list of strings.
        """

        return [p[C.NAME_KEY] for p in self.properties_of_type(type_value=C.ROUTE_VALUE)]

    def sector_volume_properties(self):
        """
        Filters the features to retain properties of those with 'type': 'SECTOR_VOLUME'.
        Returns a list of dictionaries.
        """

        return self.properties_of_type(type_value=C.SECTOR_VOLUME_VALUE)

    def geometries_of_type(self, type_value):
        """
        Filters the features to retain those whose 'type', inside a 'geometry' element, matches the given type_value.
        Returns a list of geometries dictionaries.
        """

        return jp.match(
            f"$..{C.FEATURES_KEY}[?@.{C.GEOMETRY_KEY}.{C.TYPE_KEY}=={type_value}].{C.GEOMETRY_KEY}",
            self.sector,
        )

    def polygon_geometries(self):
        """
        Filters the features to retain geometries of those with 'type': 'Polygon'.
        Returns a list of dictionaries.
        """

        return self.geometries_of_type(type_value=C.POLYGON_VALUE)

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

        return self.properties_of_type(type_value=C.SECTOR_VALUE)[0][C.NAME_KEY]

    def sector_type(self):
        """
        Returns the sector type (SectorType enum).
        """

        return ss.SectorType[self.properties_of_type(type_value=C.SECTOR_VALUE)[0][C.SHAPE_KEY]]

    def sector_origin(self):
        """
        Returns the sector origin.
        :return: a shapely.geometry.point.Point object representing the origin of the sector.
        """

        origin = self.properties_of_type(type_value=C.SECTOR_VALUE)[0][C.ORIGIN_KEY]
        return geom.Point(origin[0], origin[1])

    def sector_lower_limit(self):
        """
        Returns the sector lower flight level limit.
        :return: an integer.
        """

        return int(self.properties_of_type(type_value=C.SECTOR_VOLUME_VALUE)[0][C.LOWER_LIMIT_KEY])

    def sector_upper_limit(self):
        """
        Returns the sector upper flight level limit.
        :return: an integer.
        """

        return int(self.properties_of_type(type_value=C.SECTOR_VOLUME_VALUE)[0][C.UPPER_LIMIT_KEY])

    def sector_length_nm(self):
        """
        Returns the parsed sector length.
        :return: an integer.
        """

        return int(self.properties_of_type(type_value=C.SECTOR_VOLUME_VALUE)[0][C.LENGTH_NM_KEY])

    def sector_airway_width_nm(self):
        """
        Returns the parsed sector airway width.
        :return: an integer.
        """

        return int(self.properties_of_type(type_value=C.SECTOR_VOLUME_VALUE)[0][C.AIRWAY_WIDTH_NM_KEY])

    def waypoint_offset_nm(self):
        """
        Returns the parsed waypoint offset.
        :return: an integer.
        """

        return int(self.properties_of_type(type_value=C.SECTOR_VOLUME_VALUE)[0][C.OFFSET_NM_KEY])

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

