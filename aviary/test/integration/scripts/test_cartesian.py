
import pytest
import os

from aviary.scripts.script_helper import ScriptHelper
from aviary.scenario.scenario_generator import ScenarioGenerator

def test_cartesian_script():

    script = "aviary/scripts/cartesian.py"

    seed = 22
    flight_levels="200,220,240,260,280,300"
    aircraft_types = "B77W,A320,A346"

    filename_prefix = "test_cartesian"
    output_path = "aviary/test/integration/scripts"

    suppress_stdout = ">/dev/null 2>&1"

    cmd = f'python {script} --seed={seed} --flight_levels={flight_levels} --aircraft_types={aircraft_types} ' \
          f'--filename_prefix={filename_prefix} --output_path={output_path} ' \
          f'{suppress_stdout}'

    returned_value = os.system(cmd)

    # Expect no error.
    assert returned_value == 0

    filename = ScriptHelper.output_filename(filename_prefix=filename_prefix, seed=seed)
    file = ScenarioGenerator.json_filename(filename = filename, path = output_path)

    assert os.path.exists(file)

    # Clean up.
    os.remove(file)

