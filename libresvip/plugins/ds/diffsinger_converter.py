import pathlib
from importlib.resources import files

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import reset_time_axis

from .diffsinger_generator import DiffSingerGenerator
from .diffsinger_parser import DiffSingerParser
from .options import InputOptions, OutputOptions
from .utils.models.ds_file import DsProject
from .utils.project_util import split_into_segments


class DiffSingerConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        (files(__package__) / "ds.yapsy-plugin").read_text(encoding="utf-8")
    )
    _alias_ = "ds"
    _version_ = "0.0.1"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls.model_validate(options)
        ds_project = DsProject.model_validate_json(path.read_bytes().decode("utf-8"))
        return DiffSingerParser(options_obj).parse_project(ds_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls.model_validate(options)
        if options_obj.split_threshold >= 0:
            segments = split_into_segments(
                project,
                options_obj.min_interval,
                int(options_obj.split_threshold * 1000),
                options_obj.track_index,
            )
            series = []
            for segment in segments:
                ds_params = DiffSingerGenerator(
                    options=options_obj, trailing_space=segment[2]
                ).generate(segment[1])
                ds_params.offset = segment[0]
                if options_obj.seed >= 0:
                    ds_params.seed = options_obj.seed
                series.append(ds_params)
            ds_project = DsProject(root=series)
        else:
            project = reset_time_axis(project)
            diff_singer_params = DiffSingerGenerator(
                options=options_obj, trailing_space=0.5
            ).generate(project)
            if options_obj.seed >= 0:
                diff_singer_params.seed = options_obj.seed
            ds_project = DsProject(root=[diff_singer_params])
        path.write_bytes(
            json.dumps(
                ds_project.model_dump(mode="json"),
                indent=options_obj.indent,
                ensure_ascii=False,
            ).encode("utf-8")
        )
