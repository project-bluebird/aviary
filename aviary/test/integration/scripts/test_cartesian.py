
import os

import aviary.scenario.scenario_generator as sg
from aviary.utils.filename_helper import FilenameHelper

from aviary.scripts.cartesian import main

def test_cartesian_script(tmpdir):

    seed = 22
    flight_levels="200,220,240,260,280,300"
    aircraft_types = "B77W,A320,A346"
    filename_prefix = "test_cartesian"

    assert not main((
        f"--seed={seed}",
        f"--flight_levels={flight_levels}",
        f"--aircraft_types={aircraft_types}",
        f"--filename_prefix={filename_prefix}",
        f"--output_path={tmpdir}",
    ))

    filename = FilenameHelper.scenario_output_filename(filename_prefix=filename_prefix, seed=seed)
    output_file = FilenameHelper.construct_filename(filename = filename, desired_extension=sg.JSON_EXTENSION,
                                                    path = tmpdir)
    assert os.path.exists(output_file)
