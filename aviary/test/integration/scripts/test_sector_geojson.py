
import os

from aviary.utils.filename_helper import FilenameHelper
import aviary.sector.sector_element as se

def test_sector_geojson_script():

    script = "aviary/scripts/sector_geojson.py"

    sector_type = "I"
    sector_name = "MORTAL"
    origin = "-0.1275,51.5"
    lower_limit = 140
    upper_limit = 400

    filename_prefix = "test_sector_geojson"
    output_path = "aviary/test/integration/scripts"

    suppress_stdout = ">/dev/null 2>&1"

    cmd = f'python {script} --sector_type={sector_type} --sector_name={sector_name} ' \
          f'--origin={origin} --lower_limit={lower_limit} --upper_limit={upper_limit} ' \
          f'--filename_prefix={filename_prefix} --output_path={output_path} ' \
          f'{suppress_stdout}'

    returned_value = os.system(cmd)

    # Expect no error.
    assert returned_value == 0

    filename = FilenameHelper.sector_output_filename(filename_prefix=filename_prefix,
                                                     sector_name=sector_name,
                                                     sector_type=sector_type,
                                                     lower_limit=lower_limit,
                                                     upper_limit=upper_limit)

    output_file = FilenameHelper.construct_filename(filename = filename, desired_extension=se.GEOJSON_EXTENSION,
                                                    path = output_path)

    assert os.path.exists(output_file)

    # Clean up.
    os.remove(output_file)

