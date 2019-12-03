"""
Scenario parser for the BlueSky simulator.
"""

import aviary.sector.sector_element as se
import aviary.sector.route as rt
import aviary.scenario.scenario_generator as sg
import aviary.geo.geo_helper as gh

from datetime import datetime, timedelta
import os.path
import numpy as np
import json
import geojson
import jsonpath_rw_ext as jp

from pyproj import Geod
import shapely.geometry as geom

from itertools import compress, chain

BS_PROMPT = ">"
BS_DEFWPT_PREFIX = "00:00:00.00" + BS_PROMPT
BS_POLY = "POLYALT"
BS_DEFINE_WAYPOINT = "DEFWPT"
BS_CREATE_AIRCRAFT = "CRE"
BS_AIRCRAFT_POSITION = "POS"
BS_FLIGHT_LEVEL = "FL"
BS_ADD_WAYPOINT = "ADDWPT"
BS_ASAS_OFF = "ASAS OFF"
BS_PAN = "PAN"
BS_SCENARIO_EXTENSION = "scn"

# Shapely returns coordinates as [long, lat]
# --> make sure to pass correct values to BlueSky (as lat/lon)
LONG_INDEX = 0
LAT_INDEX = 1

class ScenarioParser:
    """A parser of geoJSON sectors and JSON scenarios for translation into BlueSky format"""

    # Default parameters:
    default_speed = 200  # TODO: temporary!

    def __init__(self, sector_geojson, scenario_json):
        """
        Scenario parser constructor.

        :param sector_geojson: Text stream from which a sector GeoJSON may be read.
        :param scenario_json: Text stream from which a scenario JSON may be read.
        """

        # Deserialise the sector geoJSON and scenario JSON strings.
        sector = geojson.load(sector_geojson)

        if se.FEATURES_KEY not in sector:
            raise ValueError(f"Sector geojson must contain {se.FEATURES_KEY} element")

        self.sector = sector

        scenario = json.load(scenario_json)

        if sg.AIRCRAFT_KEY not in scenario:
            raise ValueError(f"Scenario json must contain {sg.AIRCRAFT_KEY} element")

        self.scenario = scenario

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

    def polyalt_lines(self):
        """
        Parses a geoJSON sector definition for sector polygon & altitude information and returns a list containing a BlueSky POLYALT commands of the form, one for each sector in the geoJSON:
        f'00:00:00.00>POLYGON {sector_name} {upper_limit} {lower_limit} {lat1} {lon1} ... {latN} {lonN}'
        Currently supports only single-sector scenarios.
        """

        start_time = self.scenario[sg.START_TIME_KEY] + ".00"

        sectors = self.sector_volume_properties()
        if len(sectors) != 1:
            raise Exception(
                f"Expected precisely one sector; found {len(sectors)} sectors."
            )
        sector = sectors[0]

        upper_limit = BS_FLIGHT_LEVEL + str(sector[se.UPPER_LIMIT_KEY])
        lower_limit = BS_FLIGHT_LEVEL + str(sector[se.LOWER_LIMIT_KEY])

        line = f"{start_time}{BS_PROMPT}{BS_POLY} {self.sector_name()} {upper_limit} {lower_limit}"

        # Parse lat/long info.
        polygon = self.sector_polygon()
        for coords_list in polygon[gh.COORDINATES_KEY]:

            # Coordinates list may be nested.
            coords = coords_list
            while len(coords) == 1:
                coords = coords[0]

            # Note: longitudes appear first!
            latlongs = list(
                chain.from_iterable(
                    [[coord[LAT_INDEX], coord[LONG_INDEX]] for coord in coords]
                )
            )

            line = f'{line} {" ".join(str(latlong) for latlong in latlongs)}'

        # Return a list containing the single line.
        return [line]

    def create_aircraft_lines(self):
        """
        Parses a JSON scenario definition for aircraft information and returns a list of CRE commands of the form:
        f'HH:MM:SS.00>CRE {callsign} {aircraft_type} {lat} {lon} {heading} {flight_level} {knots}'
        """

        aircraft = self.scenario[sg.AIRCRAFT_KEY]

        # aircraft_initial_position() returns long/lat --> return to lat/lon order
        return [
            f'{self.aircraft_start_time(ac[sg.CALLSIGN_KEY]).strftime("%H:%M:%S") + ".00"}{BS_PROMPT}{BS_CREATE_AIRCRAFT} {ac[sg.CALLSIGN_KEY]} {ac[sg.AIRCRAFT_TYPE_KEY]} {self.aircraft_initial_position(ac[sg.CALLSIGN_KEY])[LAT_INDEX]} {self.aircraft_initial_position(ac[sg.CALLSIGN_KEY])[LONG_INDEX]} {self.aircraft_heading(ac[sg.CALLSIGN_KEY])} {BS_FLIGHT_LEVEL + str(ac[sg.CURRENT_FLIGHT_LEVEL_KEY])} {ScenarioParser.default_speed}'
            for ac in aircraft
        ]

    def define_waypoint_lines(self):
        """
        Parses a geoJSON sector definition for waypoint information and returns a list of BlueSky DEFWPT commands
        of the form:
        f'00:00:00.00>DEFWPT {wp_name} {lat} {lon} {wp_type}'
        where {wp_type} is optional.
        """

        fixes = self.fix_features()

        # fix coordinates are in long/lat --> turn to lat/lon
        return [
            f"{BS_DEFWPT_PREFIX}{BS_DEFINE_WAYPOINT} {fix[se.PROPERTIES_KEY][se.NAME_KEY]} {fix[se.GEOMETRY_KEY][gh.COORDINATES_KEY][LAT_INDEX]} {fix[se.GEOMETRY_KEY][gh.COORDINATES_KEY][LONG_INDEX]}"
            for fix in fixes
        ]

    def add_waypoint_lines(self):
        """
        Returns a list of BlueSky add waypoint (ADDWPT) commands of the form:
        f'HH:MM:SS.00>ADDWPT {callsign} {waypoint_name} [{flight_level}]'
        where {flight_level} is optional.
        """

        aircraft = self.scenario[sg.AIRCRAFT_KEY]
        callsigns = [ac[sg.CALLSIGN_KEY] for ac in aircraft]

        nested_list = [
            self.add_aircraft_waypoint_lines(callsign) for callsign in callsigns
        ]

        # Flatten the nested list.
        return list(chain.from_iterable(nested_list))

    def add_aircraft_waypoint_lines(self, callsign):
        """
        Returns a list of BlueSky add waypoint (ADDWPT) commands, for a particular aircraft, of the form:
        f'HH:MM:SS.00>ADDWPT {callsign} {waypoint_name}'
        """

        aircraft_start_time = self.aircraft_start_time(callsign)

        # Wait for 1 second after aircraft creation before adding waypoints to its route.
        add_waypoint_time = aircraft_start_time + timedelta(seconds=1)
        start_time = add_waypoint_time.strftime("%H:%M:%S") + ".00"

        route = self.route(callsign)
        waypoint_names = [route_element[rt.FIX_NAME_KEY] for route_element in route]

        return [
            f"{start_time}{BS_PROMPT}{BS_ADD_WAYPOINT} {callsign} {waypoint_name}"
            for waypoint_name in waypoint_names
        ]

    def asas_off_lines(self):
        """
        Returns a list containing a single BlueSky ASAS OFF command.
        """

        start_time = self.scenario[sg.START_TIME_KEY] + ".00"
        return [f"{start_time}{BS_PROMPT}{BS_ASAS_OFF}"]

    def pan_lines(self):
        """
        Returns a list containing a single BlueSky PAN command of the form:
        00:00:00.00>PAN {lat} {long}
        """

        centroid_coords = self.sector_centroid().coords[0]

        latitude = centroid_coords[LAT_INDEX]
        longitude = centroid_coords[LONG_INDEX]

        start_time = self.scenario[sg.START_TIME_KEY] + ".00"
        return [f"{start_time}{BS_PROMPT}{BS_PAN} {latitude} {longitude}"]

    def all_lines(self):
        """
        Returns a list containing all lines in the BlueSky scenario, sorted by timestamp.
        """

        lines = []
        lines.extend(self.pan_lines())
        lines.extend(self.polyalt_lines())
        lines.extend(self.define_waypoint_lines())
        lines.extend(self.create_aircraft_lines())
        lines.extend(self.add_waypoint_lines())
        lines.extend(self.asas_off_lines())

        # Sort lines by timestamp only (*not* the whole line else waypoints are added in incorrect order).
        # BlueSky expects this and will behave erratically if they're not properly sorted.
        return sorted(lines, key=lambda x: x[: len(BS_DEFWPT_PREFIX)])

    def write_bluesky_scenario(self, filename, path="."):

        name, extension = os.path.splitext(filename)
        if extension.lower() != BS_SCENARIO_EXTENSION.lower():
            filename = name + "." + BS_SCENARIO_EXTENSION

        file = os.path.join(path, filename)
        with open(file, "w") as f:
            for item in self.all_lines():
                f.write("%s\n" % item)
        return file

    def aircraft_property(self, callsign, property_key):
        """
        Parses the JSON scenario definition to extract a particular JSON element for the given aircraft.
        :param callsign: an aircraft callsign
        """

        try:
            ret = [
                aircraft[property_key]
                for aircraft in jp.match("$..{}".format(sg.AIRCRAFT_KEY), self.scenario)[0]
                if aircraft[sg.CALLSIGN_KEY] == callsign
            ]
        except Exception:
            raise ValueError(f'Failed to find property {property_key} for aircraft {callsign}.')

        if len(ret) != 1:
            raise Exception(
                f"Expected a single aircraft property {property_key} for aircraft {callsign}. Found {len(ret)}."
            )

        return ret[0]

    def route(self, callsign):
        """
        Parses the JSON scenario definition to extract the route JSON element for the given aircraft.
        :param callsign: an aircraft callsign
        """

        return self.aircraft_property(callsign=callsign, property_key=sg.ROUTE_KEY)

    def aircraft_initial_position(self, callsign):
        """Get the starting positions [long, lat] of the given aircraft."""

        return self.aircraft_property(callsign, property_key=sg.START_POSITION_KEY)

    def aircraft_start_time(self, callsign):
        """
        Returns the datetime object representing the given aircraft's *absolute* start time.
        """

        return datetime.strptime(
            self.aircraft_property(callsign=callsign, property_key=sg.START_TIME_KEY),
            "%H:%M:%S",
        )

    def aircraft_heading(self, callsign):
        """
        Returns the aircraft heading at the start of the scenario. This is the direction from the start position to the first next waypoint on route (second waypoint if starting position is at first waypoint on route).
        """

        from_wpt = self.aircraft_initial_position(callsign)

        # get the coordinates of the first waypoint
        # if this is the same as the starting position, get coordinates of second waypoint
        route_coordinates = [
            wpt[se.GEOMETRY_KEY][gh.COORDINATES_KEY] for wpt in self.route(callsign)
        ]
        to_wpt = route_coordinates[0]
        if from_wpt == to_wpt:
            to_wpt = route_coordinates[1]

        return self.bearing(from_wpt, to_wpt)

    def bearing(self, from_waypoint, to_waypoint):
        """Computes the compass bearing between two waypoints"""

        geodesic = Geod(ellps=se.ELLIPSOID)

        # Note: order of arguments is long, lat.
        fwd_azimuth, back_azimuth, distance = geodesic.inv(
            from_waypoint[LONG_INDEX],
            from_waypoint[LAT_INDEX],
            to_waypoint[LONG_INDEX],
            to_waypoint[LAT_INDEX],
        )

        return fwd_azimuth
