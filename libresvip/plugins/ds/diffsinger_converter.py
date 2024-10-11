import pathlib

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import reset_time_axis

from .diffsinger_generator import DiffSingerGenerator
from .diffsinger_parser import DiffSingerParser
from .model import DsProject
from .options import InputOptions, OutputOptions
from .utils.project_util import split_into_segments


class DiffSingerConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        ds_project = DsProject.model_validate_json(path.read_bytes().decode("utf-8"))
        return DiffSingerParser(options).parse_project(ds_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        if options.split_threshold >= 0:
            segments = split_into_segments(
                project,
                options.min_interval,
                int(options.split_threshold * 1000),
            )
            series = []
            for segment in segments:
                ds_params = DiffSingerGenerator(
                    options=options, trailing_space=segment[2]
                ).generate(segment[1])
                ds_params.offset = segment[0]
                if options.seed >= 0:
                    ds_params.seed = options.seed
                series.append(ds_params)
            ds_project = DsProject(root=series)
        else:
            project = reset_time_axis(project)
            diff_singer_params = DiffSingerGenerator(options=options, trailing_space=0.5).generate(
                project
            )
            if options.seed >= 0:
                diff_singer_params.seed = options.seed
            ds_project = DsProject(root=[diff_singer_params])
        path.write_bytes(
            json.dumps(
                ds_project.model_dump(mode="json"),
                indent=options.indent,
                ensure_ascii=False,
            ).encode("utf-8")
        )
