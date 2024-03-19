import codecs
import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.text import to_unicode

from .model import UstVisitor, ust_grammar
from .options import InputOptions, OutputOptions
from .template import render_ust
from .ust_generator import USTGenerator
from .ust_parser import USTParser


class USTConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        ust_content = path.read_bytes()
        try:
            codecs.lookup(options.encoding)
            ust_text = ust_content.decode(options.encoding, errors="replace")
        except LookupError:
            ust_text = to_unicode(ust_content)
        tree = ust_grammar.parse(ust_text)
        ust_project = UstVisitor().visit(tree)
        return USTParser(options).parse_project(ust_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        ust_project = USTGenerator(options).generate_project(project)
        render_ust(ust_project, path, options.encoding)
