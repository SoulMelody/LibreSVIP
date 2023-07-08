import pathlib

from xsdata.formats.dataclass.parsers.xml import XmlParser

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .models.mxml4 import ScoreTimewise
from .options import InputOptions, OutputOptions


class MusicXMLConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        raise NotImplementedError
        xml_parser = XmlParser()
        score = xml_parser.from_path(path, ScoreTimewise)
        return score

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        raise NotImplementedError
