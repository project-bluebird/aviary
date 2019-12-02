"""
Script for parsing a scenario.

Author: Tim Hobson, thobson@turing.ac.uk
"""


import traceback
import argparse, sys

from aviary.parser.bluesky_parser import ScenarioParser

#
# Help and usage instructions.
#
description = '''Run this script to parse a scenario into the BlueSky format.
'''
#epilog = '''Generated file(s):'''
epilog = ''''''
parser=argparse.ArgumentParser(description=description, epilog=epilog)

#
# Parse the command line arguments.
#
parser.add_argument('--sector_geojson', type=str, help='Path to an airspace sector GeoJSON file', required=True)
parser.add_argument('--scenario_json', type=str, help='Path to a scenario JSON file', required=True)

parser.add_argument('--output_path', type=str, help='Output directory path', default=".", required=False)

parser.add_argument('-d', dest='debug', help='Debug mode', action='store_true')

args=parser.parse_args()

print(">>>>> Parsing scenario >>>>>")

#
# Construct the scenario parser.
#
scenario_parser = ScenarioParser(
    sector_geojson = open(args.sector_geojson, "r"),
    scenario_json = open(args.scenario_json, "r")
)

#
# Generate the scenario.
#
filename = args.scenario_json
path = args.output_path
try:
    file = scenario_parser.write_bluesky_scenario(filename = filename, path = path)
except Exception as ex:
    print('ERROR: Scenario parsing attempt aborted due to error:')
    print(ex)
    if args.debug:
        print('Traceback:')
        tb = sys.exc_info()[2]
        print(traceback.print_tb(tb))
    else:
        print('Re-run with the debug flag -d for a stack trace.')
    exit()
print(f'SUCCESS! Wrote parsed BlueSky scenario to {file}')