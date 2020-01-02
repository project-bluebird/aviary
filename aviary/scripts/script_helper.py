"""
Helper class for scenario generation scripts.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

class ScriptHelper():
    """Helper class implementing scenario generation script output filename conventions"""

    @staticmethod
    def scenario_output_filename(filename_prefix, seed):
        """Returns the scenario generation script output filename without directory path or extension"""

        return filename_prefix + "-" + str(seed)


    @staticmethod
    def sector_output_filename(filename_prefix, sector_name, sector_type, lower_limit, upper_limit):
        """Returns the sector geojson generation script output filename without directory path or extension"""

        return "-".join([filename_prefix, sector_name, sector_type, str(lower_limit), str(upper_limit)])


