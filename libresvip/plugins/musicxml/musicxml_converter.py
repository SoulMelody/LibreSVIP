import io
import pathlib
import zipfile
from importlib.resources import files

from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata_pydantic.bindings import XmlParser, XmlSerializer

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.xmlutils import DefaultXmlWriter

from .models.container import Container
from .models.mxml4 import ScorePartwise
from .musicxml_generator import MusicXMLGenerator
from .musicxml_parser import MusicXMLParser
from .options import InputOptions, OutputOptions
from .preprocessor import preprocess_for_v4


class MusicXMLWriter(DefaultXmlWriter):
    def start_document(self) -> None:
        super().start_document()
        if self.config.xml_declaration:
            self.output.write(
                '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n'
            )


class MusicXMLConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "musicxml.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "musicxml"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        content = path.read_bytes()
        xml_parser = XmlParser(config=ParserConfig(fail_on_unknown_properties=False))
        if content[:2] == b"PK":
            zip_path = zipfile.Path(io.BytesIO(content))
            container_content = (zip_path / "META-INF/container.xml").read_bytes()
            container = xml_parser.from_bytes(container_content, Container)
            xml_bytes = (zip_path / container.rootfiles.rootfile[0].full_path).read_bytes()
        else:
            xml_bytes = content

        head = xml_bytes[:4096].lstrip()
        if b"<score-partwise" not in head and b"<score-timewise" not in head:
            msg = f"{path}: not a MusicXML score (root must be score-partwise or score-timewise)"
            raise ValueError(msg)

        xml_bytes = preprocess_for_v4(xml_bytes)
        score = xml_parser.from_bytes(xml_bytes, ScorePartwise)
        return MusicXMLParser(options_obj, xml_bytes=xml_bytes).parse_project(score)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        score = MusicXMLGenerator(options_obj).generate_project(project)
        xml_serializer = XmlSerializer(
            config=SerializerConfig(pretty_print=True), writer=MusicXMLWriter
        )
        path.write_bytes(xml_serializer.render(score).encode("utf-8"))
