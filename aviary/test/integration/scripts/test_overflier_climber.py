
import pytest
import os

from aviary.scripts.script_helper import ScriptHelper
from aviary.scenario.scenario_generator import ScenarioGenerator

def test_overflier_climber_script(cruise_speed_dataframe, climb_time_dataframe, downtrack_distance_dataframe):

    script = "aviary/scripts/overflier_climber.py"

    seed = 22
    flight_levels="200,300,360,400"
    aircraft_types = "B743,B744"
    sector_type = "X"

    filename_prefix = "test_overflier_climber"
    output_path = "aviary/test/integration/scripts"

    suppress_stdout = ">/dev/null 2>&1"

    # Write the CSV test fixtures to temporary files.
    cruise_speed_file = os.path.join(output_path, "cruise_speed.csv")
    cruise_speed_dataframe.to_csv(cruise_speed_file)

    climb_time_file = os.path.join(output_path, "climb_time.csv")
    climb_time_dataframe.to_csv(climb_time_file)

    downtrack_distance_file = os.path.join(output_path, "downtrack_distance.csv")
    downtrack_distance_dataframe.to_csv(downtrack_distance_file)

    cmd = f'python {script} ' \
          f'--cruise_speed={cruise_speed_file} --cruise_speed_index={cruise_speed_dataframe.index.name} ' \
          f'--climb_time={climb_time_file} --climb_time_index={climb_time_dataframe.index.name} ' \
          f'--downtrack_distance={downtrack_distance_file} --downtrack_distance_index={downtrack_distance_dataframe.index.name} ' \
          f'--seed={seed} --sector_type={sector_type} --flight_levels={flight_levels} --aircraft_types={aircraft_types} ' \
          f'--filename_prefix={filename_prefix} --output_path={output_path} ' \
          f'{suppress_stdout}'


    returned_value = os.system(cmd)

    # Expect no error.
    assert returned_value == 0

    filename = ScriptHelper.scenario_output_filename(filename_prefix=filename_prefix, seed=seed)
    output_file = ScenarioGenerator.json_filename(filename = filename, path = output_path)

    assert os.path.exists(output_file)
    assert os.path.exists(cruise_speed_file)
    assert os.path.exists(climb_time_file)
    assert os.path.exists(downtrack_distance_file)

    # Clean up.
    os.remove(output_file)
    os.remove(cruise_speed_file)
    os.remove(climb_time_file)
    os.remove(downtrack_distance_file)

