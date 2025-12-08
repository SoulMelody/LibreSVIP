# mypy: disable-error-code="attr-defined"
import pathlib
from typing import Annotated

import typer
from rich.progress import track
from rich.prompt import Confirm

from libresvip.cli.prompt import prompt_fields
from libresvip.extension.base import ReadOnlyConverterMixin, WriteOnlyConverterMixin
from libresvip.extension.manager import middleware_manager, plugin_manager
from libresvip.model.base import Project
from libresvip.utils.translation import gettext_lazy as _

app = typer.Typer()


def option_callback(ctx: typer.Context, value: pathlib.Path) -> pathlib.Path | None:
    if ctx.resilient_parsing:
        return None
    ext = value.suffix.lstrip(".").lower()
    if ext not in plugin_manager.plugins.get("svs", {}):
        raise typer.BadParameter(
            _("Extension {} is not supported. Supported extensions are: {}").format(
                ext, list(plugin_manager.plugins.get("svs", {}).keys())
            )
        )
    return value


@app.command()
def convert(
    in_path: Annotated[
        pathlib.Path, typer.Argument(exists=True, dir_okay=False, callback=option_callback)
    ],
    out_path: Annotated[
        pathlib.Path, typer.Argument(exists=False, dir_okay=False, callback=option_callback)
    ],
) -> None:
    """
    Convert a file from one format to another.
    """
    input_ext = in_path.suffix.lstrip(".").lower()
    input_plugin = plugin_manager.plugins.get("svs", {})[input_ext]
    assert not issubclass(input_plugin, WriteOnlyConverterMixin)
    output_ext = out_path.suffix.lstrip(".").lower()
    output_plugin = plugin_manager.plugins.get("svs", {})[output_ext]
    assert not issubclass(output_plugin, ReadOnlyConverterMixin)
    input_option = input_plugin.input_option_cls
    output_option = output_plugin.output_option_cls
    option_type, option_class = _("Input Options: "), input_option
    option_kwargs = {}
    if len(option_class.model_fields):
        typer.echo(option_type)
        option_kwargs = prompt_fields(option_class)
    project = input_plugin.load(in_path, option_kwargs)
    for middleware in middleware_manager.plugins.get("middleware", {}).values():
        if Confirm.ask(
            _("Enable {} middleware?").format(_(middleware.info.name)),
            default=False,
        ):
            option_type, option_class = (
                _("Process Options: "),
                middleware.process_option_cls,
            )
            option_kwargs = {}
            if len(option_class.model_fields):
                typer.echo(option_type)
                option_kwargs = prompt_fields(option_class)
            project = middleware.process(project, option_kwargs)
    option_type, option_class = _("Output Options: "), output_option
    option_kwargs = {}
    if len(option_class.model_fields):
        typer.echo(option_type)
        option_kwargs = prompt_fields(option_class)
    output_plugin.dump(out_path, project, option_kwargs)


@app.command("split")
def split_project(
    in_path: Annotated[
        pathlib.Path, typer.Argument(exists=True, dir_okay=False, callback=option_callback)
    ],
    out_dir: Annotated[pathlib.Path, typer.Argument(exists=True, dir_okay=True)],
    output_ext: Annotated[str, typer.Option(help=_("Output format"))] = "ust",
    max_track_count: Annotated[int, typer.Option(help=_("Maximum track count per file"))] = 1,
) -> None:
    input_ext = in_path.suffix.lstrip(".").lower()
    input_plugin = plugin_manager.plugins.get("svs", {})[input_ext]
    output_plugin = plugin_manager.plugins.get("svs", {})[output_ext]
    input_option = input_plugin.input_option_cls
    output_option = output_plugin.output_option_cls
    option_type, option_class = _("Input Options: "), input_option
    option_kwargs = {}
    if len(option_class.model_fields):
        typer.echo(option_type)
        option_kwargs = prompt_fields(option_class)
    root_project = input_plugin.load(in_path, option_kwargs)
    sub_projects = root_project.split_tracks(max_track_count)
    middleware_with_options = []
    for middleware in middleware_manager.plugins.get("middleware", {}).values():
        if Confirm.ask(
            _("Enable {} middleware?").format(_(middleware.info.name)),
            default=False,
        ):
            option_type, option_class = (
                _("Process Options: "),
                middleware.process_option_cls,
            )
            option_kwargs = {}
            if len(option_class.model_fields):
                typer.echo(option_type)
                option_kwargs = prompt_fields(option_class)
            middleware_with_options.append(
                (
                    middleware.process,
                    option_kwargs,
                )
            )
    option_type, option_class = _("Output Options: "), output_option
    option_kwargs = {}
    if len(option_class.model_fields):
        typer.echo(option_type)
        option_kwargs = prompt_fields(option_class)
    for i, project in track(
        enumerate(sub_projects, start=1),
        description=_("Converting ..."),
        total=len(sub_projects),
    ):
        for (
            middleware_func,
            option_kwargs,
        ) in middleware_with_options:
            project = middleware_func(project, option_kwargs)
        output_plugin.dump(
            out_dir / f"{in_path.stem}_{i:02d}.{output_ext}",
            project,
            option_kwargs,
        )


@app.command("merge")
def merge_projects(
    in_paths: Annotated[list[pathlib.Path], typer.Argument()],
    out_path: Annotated[
        pathlib.Path, typer.Option("", exists=False, dir_okay=False, callback=option_callback)
    ],
) -> None:
    projects = []
    middleware_with_options = []
    for middleware in middleware_manager.plugins.get("middleware", {}).values():
        if Confirm.ask(
            _("Enable {} middleware?").format(_(middleware.info.name)),
            default=False,
        ):
            option_type, option_class = (
                _("Process Options: "),
                middleware.process_option_cls,
            )
            option_kwargs = {}
            if len(option_class.model_fields):
                typer.echo(option_type)
                option_kwargs = prompt_fields(option_class)
            middleware_with_options.append((middleware.process, option_kwargs))
    for in_path in in_paths:
        typer.echo(in_path)
        input_ext = in_path.suffix.lstrip(".").lower()
        input_plugin = plugin_manager.plugins.get("svs", {})[input_ext]
        input_option = input_plugin.input_option_cls
        option_type, option_class = _("Input Options: "), input_option
        option_kwargs = {}
        if len(option_class.model_fields):
            typer.echo(option_type)
            option_kwargs = prompt_fields(option_class)
        project = input_plugin.load(in_path, option_kwargs)
        for (
            middleware_func,
            option_kwargs,
        ) in middleware_with_options:
            project = middleware_func(project, option_kwargs)
        projects.append(project)
    output_ext = out_path.suffix.lstrip(".").lower()
    if projects:
        output_plugin = plugin_manager.plugins.get("svs", {})[output_ext]
        output_option = output_plugin.output_option_cls
        project = Project.merge_projects(projects)
        option_type, option_class = _("Output Options: "), output_option
        option_kwargs = {}
        if len(option_class.model_fields):
            typer.echo(option_type)
            option_kwargs = prompt_fields(option_class)
        output_plugin.dump(out_path, project, option_kwargs)
    else:
        typer.secho("Invalid options", err=True, color=True, fg="red")
