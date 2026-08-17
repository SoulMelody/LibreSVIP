from libresvip.plugins.ufdata.model import UFData, UFProject
from libresvip.plugins.ufdata.options import InputOptions
from libresvip.plugins.ufdata.ufdata_parser import UFDataParser


def test_parse_project_without_time_signatures() -> None:
    # A ufdata project may carry no time signatures. parse_project used to read
    # time_signatures[0] unconditionally and raise IndexError on such a file.
    project = UFData(project=UFProject(measure_prefix=0, tracks=[], tempos=[], time_signatures=[]))
    result = UFDataParser(InputOptions()).parse_project(project)

    assert len(result.time_signature_list) == 1
    default = result.time_signature_list[0]
    assert (default.bar_index, default.numerator, default.denominator) == (0, 4, 4)
