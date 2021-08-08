#! python
"""
Script for generating an overflier-climber scenario.

Author: Tim Hobson, thobson@turing.ac.uk
"""


import traceback
import argparse, sys
import pandas

import aviary.constants as C
from aviary.trajectory.lookup_trajectory_predictor import LookupTrajectoryPredictor
from aviary.scenario.overflier_climber_scenario import OverflierClimberScenario
from aviary.scenario.overflier_climber_extended_scenario import OverflierClimberExtendedScenario
from aviary.scenario.scenario_generator import ScenarioGenerator

import aviary.sector.sector_element as se
from aviary.sector.sector_shape import SectorType
from aviary.utils.filename_helper import FilenameHelper

FILENAME_PREFIX = "overflier-climber-scenario"

def main(argv=None):
    #
    # Help and usage instructions.
    #
    description = '''Run this script to generate a seeded conflict scenario involving two aircraft: one overflier and one climber.
    '''
    #epilog = '''Generated file(s):'''
    epilog = ''''''
    parser=argparse.ArgumentParser(description=description, epilog=epilog)

    #
    # Parse the command line arguments.
    #
    parser.add_argument('--cruise_speed', type=str, help='Aircraft cruise speed lookup table in CSV format', required=True)
    parser.add_argument('--cruise_speed_index', type=str, help='Index column in the cruise speed lookup table', required=True)
    parser.add_argument('--climb_time', type=str, help='Aircraft climb time lookup table in CSV format', required=True)
    parser.add_argument('--climb_time_index', type=str, help='Index column in the climb time lookup table', required=True)
    parser.add_argument('--downtrack_distance', type=str, help='Aircraft downtrack distance lookup table in CSV format', required=True)
    parser.add_argument('--downtrack_distance_index', type=str, help='Index column in the downtrack distance lookup table', required=True)

    parser.add_argument('--sector_type', type=str, help='Sector type: I, X or Y', default="I", required=False)
    parser.add_argument('--aircraft_types', type=str, help='Comma-separated list of aircraft types', required=False)
    parser.add_argument('--flight_levels', type=str, help='Comma-separated list of integer flight levels', required=False)

    parser.add_argument('--thinking_time', type=float, help='Extended scenario "thinking time" in seconds', required=False)

    parser.add_argument('--filename_prefix', type=str, help='Output filename prefix', default=FILENAME_PREFIX, required=False)
    parser.add_argument('--output_path', type=str, help='Output directory path', default=".", required=False)

    parser.add_argument('--seed', type=int, help='Random seed', required=True)

    parser.add_argument('-d', dest='debug', help='Debug mode', action='store_true')

    args=parser.parse_args(argv)

    print(">>>>> Generating overflier-climber scenario >>>>>")

    #
    # Read the trajectory lookup tables.
    #
    try:
        cruise_speed_lookup = pandas.read_csv(args.cruise_speed, index_col = args.cruise_speed_index)
    except ValueError as ex:
        print(f'Invalid cruise speed command-line arguments:')
        print(ex)

    try:
        climb_time_lookup = pandas.read_csv(args.climb_time, index_col = args.climb_time_index)
    except ValueError as ex:
        print(f'Invalid climb time command-line arguments:')
        print(ex)

    try:
        downtrack_distance_lookup = pandas.read_csv(args.downtrack_distance, index_col = args.downtrack_distance_index)
    except ValueError as ex:
        print(f'Invalid downtrack distance command-line arguments:')
        print(ex)

    #print("Successfully read lookup tables for cruise speed, climb time and downtrack distance")

    # Construct the trajectory predictor instance.
    trajectory_predictor = LookupTrajectoryPredictor(cruise_speed_lookup = cruise_speed_lookup,
                                                    climb_time_lookup = climb_time_lookup,
                                                    downtrack_distance_lookup = downtrack_distance_lookup)

    # Handle the optional command-line arguments.

    aircraft_types = args.aircraft_types
    if not aircraft_types:
        aircraft_types = None
        print("INFO: Using default aircraft types")
    else:
        try:
            aircraft_types = [str(actype) for actype in aircraft_types.split(",")]
            print(f'INFO: Read aircraft types as: {aircraft_types}')
        except ValueError as ex:
            print(f'Invalid aircraft_types argument: {aircraft_types}')

    flight_levels = args.flight_levels
    if not flight_levels:
        flight_levels = None
        print("INFO: Using default flight levels")
    else:
        try:
            flight_levels = [int(fl) for fl in flight_levels.split(",")]
            print(f'INFO: Read flight levels as: {flight_levels}')
        except ValueError as ex:
            print(f'Invalid flight_levels argument: {flight_levels}')

    #
    # Construct the sector.
    #

    # Default parameters:
    lower_limit = C.DEFAULT_LOWER_LIMIT
    upper_limit = C.DEFAULT_UPPER_LIMIT

    if any([fl < lower_limit for fl in flight_levels]):
        raise ValueError(f'Flight levels must not be less than the sector lower limit of {lower_limit}')
    if any([fl > upper_limit for fl in flight_levels]):
        raise ValueError(f'Flight levels must not exceed the sector lower limit of {upper_limit}')

    sector_element = se.SectorElement(type = SectorType[args.sector_type],
                                name = C.DEFAULT_SECTOR_NAME,
                                origin = C.DEFAULT_ORIGIN,
                                lower_limit = lower_limit,
                                upper_limit = lower_limit)

    #
    # Construct the overflier-climber scenario algorithm.
    #

    # TODO: fix issue with callsign_prefixes = None (fails to get the default value for this argument)

    kwargs = {
        "trajectory_predictor": trajectory_predictor,
        "aircraft_types": aircraft_types,
        "callsign_prefixes": ["SPEEDBIRD", "VJ", "DELTA", "EZY"],
        "flight_levels": flight_levels,
        "seed": args.seed
    }

    if not args.thinking_time:
        algorithm = OverflierClimberScenario
    else:
        kwargs["thinking_time"] = args.thinking_time
        args.filename_prefix = args.filename_prefix + "-extended-" + str(int(args.thinking_time))
        algorithm = OverflierClimberExtendedScenario

    scenario_algorithm = algorithm(**kwargs, sector_element = sector_element)

    #
    # Construct the scenario generator.
    #
    scenario_generator = ScenarioGenerator(scenario_algorithm = scenario_algorithm)

    try:
        scenario = scenario_generator.generate_scenario(duration = 1)
    except Exception as ex:
        print('ERROR: Scenario generation attempt aborted due to error:')
        print(ex)
        if args.debug:
            print('Traceback:')
            tb = sys.exc_info()[2]
            print(traceback.print_tb(tb))
        else:
            print('Re-run with the debug flag -d for a stack trace.')
        return 1

    #
    # Generate the scenario.
    #
    filename = FilenameHelper.scenario_output_filename(filename_prefix=args.filename_prefix, seed=args.seed)
    file = scenario_generator.write_json_scenario(scenario = scenario, filename = filename, path = args.output_path)

    print(f'SUCCESS! Wrote scenario to {file}')
    return 0


if __name__ == "__main__":
    exit(main())
