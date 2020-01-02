#! python
"""
Script for generating an airspace sector GeoJSON file.

Author: Tim Hobson, thobson@turing.ac.uk
"""


import traceback
import argparse, sys

import aviary.sector.sector_shape as ss
from aviary.sector.sector_element import SectorElement
from aviary.utils.filename_helper import FilenameHelper

FILENAME_PREFIX = "sector"

#
# Help and usage instructions.
#
description = '''Run this script to generate an airspace sector GeoJSON file.
'''
#epilog = '''Generated file(s):'''
epilog = ''''''

def main():
    parser=argparse.ArgumentParser(description=description, epilog=epilog)

    #
    # Parse the command line arguments.
    #
    parser.add_argument('--sector_type', type=str, help='Sector type: I, X or Y', required=True)
    parser.add_argument('--sector_name', type=str, help='Sector name', required=True)
    parser.add_argument('--origin', type=str, help='Sector origin at a comma-separated latitude,longitude pair', required=True)
    parser.add_argument('--lower_limit', type=int, help='Sector lower flight level limit', required=True)
    parser.add_argument('--upper_limit', type=int, help='Sector upper flight level limit', required=True)

    parser.add_argument('--filename_prefix', type=str, help='Output filename prefix', default=FILENAME_PREFIX, required=False)
    parser.add_argument('--output_path', type=str, help='Output directory path', default=".", required=False)

    parser.add_argument('-d', dest='debug', help='Debug mode', action='store_true')

    args=parser.parse_args()

    print(">>>>> Generating sector GeoJSON >>>>>")

    # Default parameters:
    origin = tuple([float(x) for x in args.origin.split(",")])

    # Construct the sector.
    try:
        sector = SectorElement(type = ss.SectorType[args.sector_type],
                               name = args.sector_name,
                               origin = origin,
                               lower_limit = args.lower_limit,
                               upper_limit = args.upper_limit)
    except Exception as ex:
        print('ERROR: Sector construction attempt aborted due to error:')
        print(ex)
        if args.debug:
            print('Traceback:')
            tb = sys.exc_info()[2]
            print(traceback.print_tb(tb))
        else:
            print('Re-run with the debug flag -d for a stack trace.')
        exit()

    #old: filename = "-".join([args.filename_prefix, args.sector_name, args.sector_type, str(args.lower_limit), str(args.upper_limit)])
    filename = FilenameHelper.sector_output_filename(filename_prefix=args.filename_prefix,
                                                     sector_name=args.sector_name,
                                                     sector_type=args.sector_type,
                                                     lower_limit=args.lower_limit,
                                                     upper_limit=args.upper_limit)

    file = sector.write_geojson(filename = filename, path = args.output_path)

    print(f'SUCCESS! Wrote sector to {file}')

if __name__ == "__main__":
    main()
