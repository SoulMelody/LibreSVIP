__package__ = "libresvip.plugins.ds"

import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .diffsinger_generator import DiffSingerGenerator
from .diffsinger_parser import DiffSingerParser
from .model import DsProject
from .options import InputOptions, OutputOptions
from .utils.project_util import reset_time_axis, split_into_segments


class DiffSingerConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        ds_project = DsProject.model_validate_json(path.read_text("utf-8"))
        return DiffSingerParser(options).parse_project(ds_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        if options.split_threshold >= 0:
            segments = split_into_segments(project, options.min_interval, int(options.split_threshold * 1000))
            series = []
            for segment in segments:
                ds_params = DiffSingerGenerator(
                    options=options,
                    trailing_space=segment[2]
                ).generate(segment[1])
                ds_params.offset = segment[0]
                if options.seed >= 0:
                    ds_params.seed = options.seed
                series.append(ds_params)
            ds_project = DsProject(
                __root__=series
            )
        else:
            reset_time_axis(project)
            diff_singer_params = DiffSingerGenerator(
                options=options,
                trailing_space=0.5
            ).generate(project)
            if options.seed >= 0:
                diff_singer_params.seed = options.seed
            ds_project = DsProject(
                __root__=[diff_singer_params]
            )
        path.write_text(
            ds_project.json(
                ensure_ascii=False,
                indent=options.indent
            ),
            encoding="utf-8"
        )
