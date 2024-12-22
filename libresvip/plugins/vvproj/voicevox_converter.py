import pathlib

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VoiceVoxProject
from .options import InputOptions, OutputOptions
from .voicevox_generator import VOICEVOXGenerator
from .voicevox_parser import VOICEVOXParser


class VOICEVOXConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        voicevox_project = VoiceVoxProject.model_validate_json(path.read_bytes())
        return VOICEVOXParser(options).parse_project(voicevox_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        voicevox_project = VOICEVOXGenerator(options).generate_project(project)
        path.write_bytes(
            json.dumps(voicevox_project.model_dump(mode="json", by_alias=True)).encode("utf-8")
        )
