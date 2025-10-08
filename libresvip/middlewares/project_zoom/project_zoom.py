import fractions
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import zoom_project

from .options import ProcessOptions


class ProjectZoomMiddleware(plugin_base.Middleware):
    process_option_cls = ProcessOptions
    info = plugin_base.MiddlewarePluginInfo.load_from_string(
        (files(__package__) / "project_zoom.yapsy-plugin").read_text(encoding="utf-8")
    )
    _alias_ = "project_zoom"
    _version_ = "1.0.0"

    @classmethod
    def process(cls, project: Project, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.process_option_cls.model_validate(options)
        if (zoom_factor := float(fractions.Fraction(options_obj.factor.value))) != 1.0:
            return zoom_project(project, zoom_factor)
        return project
