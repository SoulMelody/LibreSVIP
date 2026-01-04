import pathlib
from importlib.resources import files

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.text import to_unicode

from .model import TuneLabProject
from .options import InputOptions, OutputOptions
from .tunelab_generator import TuneLabGenerator
from .tunelab_parser import TuneLabParser


class TuneLabConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "tlp.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "tlp"
    _version_ = "0.5.8"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        tlp_project = TuneLabProject.model_validate_json(to_unicode(path.read_bytes()))
        return TuneLabParser(options_obj).parse_project(tlp_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        tlp_project = TuneLabGenerator(options_obj).generate_project(project)
        path.write_bytes(
            json.dumps(
                tlp_project.model_dump(mode="json", by_alias=True),
                ensure_ascii=False,
            ).encode("utf-8")
        )
