import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import reset_time_axis
from libresvip.utils.text import to_unicode

from .model import NnWalker, get_nn_grammar
from .niaoniao_generator import NiaoniaoGenerator
from .niaoniao_parser import NiaoNiaoParser
from .options import InputOptions, OutputOptions
from .template import render_nn


class NiaoNiaoConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "nn.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "nn"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        tree = get_nn_grammar().parse(to_unicode(path.read_bytes()))
        nn_project = NnWalker().walk(tree)
        return NiaoNiaoParser(options_obj).parse_project(nn_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        if len(project.song_tempo_list) != 1:
            project = reset_time_axis(project, options_obj.tempo)
        nn_project = NiaoniaoGenerator(options_obj).generate_project(project)
        render_nn(nn_project, path)
