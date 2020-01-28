
from pathlib import Path

from aviary.scripts.overflier_climber import main
from aviary.utils.filename_helper import FilenameHelper
import aviary.scenario.scenario_generator as sg

def test_overflier_climber_script(
    cruise_speed_dataframe,
    climb_time_dataframe,
    downtrack_distance_dataframe,
    tmpdir
):

    seed = 22
    flight_levels="200,300,360,400"
    aircraft_types = "B743,B744"
    sector_type = "X"
    filename_prefix = "test_overflier_climber"

    # Write the CSV test fixtures to temporary files.
    cruise_speed_file = Path(tmpdir, "cruise_speed.csv")
    cruise_speed_dataframe.to_csv(cruise_speed_file)

    climb_time_file = Path(tmpdir, "climb_time.csv")
    climb_time_dataframe.to_csv(climb_time_file)

    downtrack_distance_file = Path(tmpdir, "downtrack_distance.csv")
    downtrack_distance_dataframe.to_csv(downtrack_distance_file)
    
    assert not main((
        f'--cruise_speed={cruise_speed_file}',
        f'--cruise_speed_index={cruise_speed_dataframe.index.name}',
        f'--climb_time={climb_time_file}',
        f'--climb_time_index={climb_time_dataframe.index.name}',
        f'--downtrack_distance={downtrack_distance_file}',
        f'--downtrack_distance_index={downtrack_distance_dataframe.index.name}',
        f'--seed={seed}',
        f'--sector_type={sector_type}',
        f'--flight_levels={flight_levels}',
        f'--aircraft_types={aircraft_types}',
        f'--filename_prefix={filename_prefix}',
        f'--output_path={tmpdir}',
    ))

    filename = FilenameHelper.scenario_output_filename(
        filename_prefix=filename_prefix,
        seed=seed
    )
    output_file = FilenameHelper.construct_filename(
        filename=filename,
        desired_extension=sg.JSON_EXTENSION,
        path=tmpdir
    )

    assert Path(output_file).exists()
    assert Path(cruise_speed_file).exists()
    assert Path(climb_time_file).exists()
    assert Path(downtrack_distance_file).exists()
