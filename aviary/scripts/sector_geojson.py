"""
Script for generating an airspace sector GeoJSON file.

Author: Tim Hobson, thobson@turing.ac.uk
"""


import traceback
import argparse, sys

import aviary.sector.sector_shape as ss
from aviary.sector.sector_element import SectorElement

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

    # Construct the sector shape.
    if args.sector_type == 'I':
        shape = ss.IShape()
    elif args.sector_type == 'X':
        shape = ss.XShape()
    elif args.sector_type == 'Y':
        shape = ss.YShape()
    else:
        raise ValueError(f'Invalid sector_type argument: {args.sector_type}.')

    # Construct the sector.

    # Default parameters:
    origin = tuple([float(x) for x in args.origin.split(",")])

    try:
        sector = SectorElement(args.sector_name, origin, shape, args.lower_limit, args.upper_limit)
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

    filename = "-".join([args.filename_prefix, args.sector_name, args.sector_type, str(args.lower_limit), str(args.upper_limit)])
    file = sector.write_geojson(filename = filename, path = args.output_path)

    print(f'SUCCESS! Wrote sector to {file}')

if __name__ == "__main__":
    main()
