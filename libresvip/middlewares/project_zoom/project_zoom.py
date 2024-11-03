import fractions

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import zoom_project

from .options import ProcessOptions


class ProjectZoomMiddleware(plugin_base.MiddlewareBase):
    def process(self, project: Project, options: ProcessOptions) -> Project:
        if (zoom_factor := float(fractions.Fraction(options.factor.value))) != 1.0:
            return zoom_project(project, zoom_factor)
        return project
