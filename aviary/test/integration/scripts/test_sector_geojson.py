
from pathlib import Path

import aviary.constants as C
from aviary.scripts.sector_geojson import main
from aviary.utils.filename_helper import FilenameHelper
import aviary.sector.sector_element as se

def test_sector_geojson_script(tmpdir):

    sector_type = "I"
    sector_name = "MORTAL"
    origin = "-0.1275,51.5"
    lower_limit = 140
    upper_limit = 400

    filename_prefix = "test_sector_geojson"

    assert not main((
        f'--sector_type={sector_type}',
        f'--sector_name={sector_name}',
        f'--origin={origin}',
        f'--lower_limit={lower_limit}',
        f'--upper_limit={upper_limit}',
        f'--filename_prefix={filename_prefix}',
        f'--output_path={tmpdir}',
    ))

    filename = FilenameHelper.sector_output_filename(
        filename_prefix=filename_prefix,
        sector_name=sector_name,
        sector_type=sector_type,
        lower_limit=lower_limit,
        upper_limit=upper_limit
    )

    output_file = FilenameHelper.construct_filename(
        filename = filename,
        desired_extension=C.GEOJSON_EXTENSION,
        path = tmpdir
    )

    assert Path(tmpdir).exists()

