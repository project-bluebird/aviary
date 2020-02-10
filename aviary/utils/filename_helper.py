"""
Helper class implementing file naming conventions.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

import os

class FilenameHelper():
    """Helper class implementing file naming conventions"""

    @staticmethod
    def construct_filename(filename, desired_extension, path="."):
        """Constructs a full path filename with extension"""

        if not filename.lower().endswith(desired_extension):
            filename = filename + "." + desired_extension

        return os.path.join(path, filename)


    @staticmethod
    def scenario_output_filename(filename_prefix, seed):
        """Returns the scenario generation script output filename without directory path or extension"""

        return filename_prefix + "-" + str(seed)


    @staticmethod
    def sector_output_filename(filename_prefix, sector_name, sector_type, lower_limit, upper_limit):
        """Returns the sector geojson generation script output filename without directory path or extension"""

        return "-".join([filename_prefix, sector_name, sector_type, str(lower_limit), str(upper_limit)])


