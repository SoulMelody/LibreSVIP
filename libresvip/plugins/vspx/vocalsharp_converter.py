import pathlib
import re
from typing import Any

from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata_pydantic.bindings import XmlParser, XmlSerializer

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.xmlutils import DefaultXmlWriter

from .model import VocalSharpProject
from .options import InputOptions, OutputOptions
from .vspx_generator import VocalSharpGenerator
from .vspx_parser import VocalSharpParser


class VocalSharpXMLWriter(DefaultXmlWriter):
    def set_data(self, data: Any) -> None:
        if (
            isinstance(data, str)
            and self.pending_tag
            and len(self.pending_tag) > 1
            and self.pending_tag[1]
            in (
                "name",
                "Name",
                "Singer",
                "lyric",
                "LSD",
                "symbol",
                "sample",
                "path",
            )
        ):
            super().set_cdata(data)
        else:
            super().set_data(data)

    def start_document(self) -> None:
        if self.config.xml_declaration:
            self.output.write(
                f'<?xml version="{self.config.xml_version}" encoding="{self.config.encoding}" standalone="no"?>\n'
            )


def strip_whitespace(matcher: re.Match[str]) -> str:
    first_tag = matcher[1]
    second_tag = matcher[2]
    if first_tag != second_tag:
        return f"</{first_tag}><{second_tag}>"
    else:
        return matcher.group()


def replace_self_closed(matcher: re.Match[str]) -> str:
    indent = matcher[1]
    tag = matcher[2]
    return f"{indent}<{tag}>{indent}</{tag}>"


class VocalSharpConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        vspx_project = XmlParser().from_bytes(path.read_bytes(), VocalSharpProject)
        return VocalSharpParser(options).parse_project(vspx_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        vspx_project = VocalSharpGenerator(options).generate_project(project)
        serializer = XmlSerializer(
            config=SerializerConfig(pretty_print=True, pretty_print_indent="\t"),
            writer=VocalSharpXMLWriter,
        )
        xml_text = serializer.render(vspx_project)
        xml_text = re.sub(r"(<[a-zA-Z]>)\s+", r"\1", xml_text)
        xml_text = re.sub(r"\s+(</[a-zA-Z]>)", r"\1", xml_text)
        xml_text = re.sub(r"</([a-z])>\s+<([a-z])>", strip_whitespace, xml_text)
        xml_text = re.sub(r"(\n\s*)<([a-zA-Z]+)/>", replace_self_closed, xml_text)
        path.write_bytes(xml_text.encode("utf-8"))
