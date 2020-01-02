"""
Helper class for scenario generation scripts.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

class ScriptHelper():
    """Helper class implementing scenario generation script output filename conventions"""

    @staticmethod
    def output_filename(filename_prefix, seed):
        """Returns the script output filename without directory path or extension"""

        return filename_prefix + "-" + str(seed)



