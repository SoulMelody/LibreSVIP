import pathlib

from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.parsers.xml import XmlParser

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .models.mxml2 import ScorePartwise
from .musicxml_parser import MusicXMLParser
from .options import InputOptions, OutputOptions


class MusicXMLConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        xml_parser = XmlParser(config=ParserConfig(fail_on_unknown_properties=False))
        score = xml_parser.from_bytes(path.read_bytes(), ScorePartwise)
        return MusicXMLParser(options).parse_project(score)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        raise NotImplementedError
