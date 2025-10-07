import pathlib
from importlib.resources import files

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VoiceVoxProject
from .options import InputOptions, OutputOptions
from .voicevox_generator import VOICEVOXGenerator
from .voicevox_parser import VOICEVOXParser


class VOICEVOXConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "vvproj.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "vvproj"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        voicevox_project = VoiceVoxProject.model_validate_json(path.read_bytes())
        return VOICEVOXParser(options_obj).parse_project(voicevox_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        voicevox_project = VOICEVOXGenerator(options_obj).generate_project(project)
        path.write_bytes(
            json.dumps(voicevox_project.model_dump(mode="json", by_alias=True)).encode("utf-8")
        )
