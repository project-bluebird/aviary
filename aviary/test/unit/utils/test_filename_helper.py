
import pytest
from io import StringIO
import geojson

import aviary.constants as C
from aviary.utils.filename_helper import FilenameHelper
import aviary.sector.sector_element as se


def test_construct_filename_extension_parsing():
    test_path = "/path/to/a/test-sector"
    assert (
        FilenameHelper.construct_filename(test_path, C.GEOJSON_EXTENSION)
        == test_path + ".geojson"
    )
    assert (
        FilenameHelper.construct_filename(test_path + ".geojson", C.GEOJSON_EXTENSION)
        == test_path + ".geojson"
    )

