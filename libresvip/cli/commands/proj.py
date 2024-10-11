# mypy: disable-error-code="attr-defined"
import pathlib
from typing import Annotated, Optional, get_type_hints

import typer
from rich.progress import track
from rich.prompt import Confirm

from libresvip.cli.prompt import prompt_fields
from libresvip.extension.manager import middleware_manager, plugin_manager
from libresvip.utils.translation import gettext_lazy as _

app = typer.Typer()


def option_callback(ctx: typer.Context, value: pathlib.Path) -> Optional[pathlib.Path]:
    if ctx.resilient_parsing:
        return None
    ext = value.suffix.lstrip(".").lower()
    if ext not in plugin_manager.plugin_registry:
        raise typer.BadParameter(
            _("Extension {} is not supported. Supported extensions are: {}").format(
                ext, list(plugin_manager.plugin_registry.keys())
            )
        )
    return value


@app.command()
def convert(
    in_path: pathlib.Path = typer.Argument(
        "", exists=True, dir_okay=False, callback=option_callback
    ),
    out_path: pathlib.Path = typer.Argument(
        "", exists=False, dir_okay=False, callback=option_callback
    ),
) -> None:
    """
    Convert a file from one format to another.
    """
    input_ext = in_path.suffix.lstrip(".").lower()
    input_plugin = plugin_manager.plugin_registry[input_ext]
    output_ext = out_path.suffix.lstrip(".").lower()
    output_plugin = plugin_manager.plugin_registry[output_ext]
    if (
        input_plugin.plugin_object is not None
        and (input_option := get_type_hints(input_plugin.plugin_object.load).get("options"))
        and output_plugin.plugin_object is not None
        and (output_option := get_type_hints(output_plugin.plugin_object.dump).get("options"))
    ):
        option_type, option_class = _("Input Options: "), input_option
        option_kwargs = {}
        if len(option_class.model_fields):
            typer.echo(option_type)
            option_kwargs = prompt_fields(option_class)
        project = input_plugin.plugin_object.load(in_path, option_class(**option_kwargs))
        for middleware in middleware_manager.plugin_registry.values():
            if (
                (
                    Confirm.ask(
                        _("Enable {} middleware?").format(_(middleware.name)),
                        default=False,
                    )
                )
                and (middleware.plugin_object is not None)
                and (
                    middleware_option := get_type_hints(middleware.plugin_object.process).get(
                        "options"
                    )
                )
            ):
                option_type, option_class = (
                    _("Process Options: "),
                    middleware_option,
                )
                option_kwargs = {}
                if len(option_class.model_fields):
                    typer.echo(option_type)
                    option_kwargs = prompt_fields(option_class)
                project = middleware.plugin_object.process(project, option_class(**option_kwargs))
        option_type, option_class = _("Output Options: "), output_option
        option_kwargs = {}
        if len(option_class.model_fields):
            typer.echo(option_type)
            option_kwargs = prompt_fields(option_class)
        output_plugin.plugin_object.dump(out_path, project, option_class(**option_kwargs))
    else:
        typer.secho("Invalid options", err=True, color="red")


@app.command("split")
def split_project(
    in_path: pathlib.Path = typer.Argument(
        "", exists=True, dir_okay=False, callback=option_callback
    ),
    out_dir: pathlib.Path = typer.Argument("", exists=True, dir_okay=True),
    output_ext: str = typer.Option("ust", help=_("Output format")),
    max_track_count: int = typer.Option(1, help=_("Maximum track count per file")),
) -> None:
    input_ext = in_path.suffix.lstrip(".").lower()
    input_plugin = plugin_manager.plugin_registry[input_ext]
    output_plugin = plugin_manager.plugin_registry[output_ext]
    if (
        input_plugin.plugin_object is not None
        and (input_option := get_type_hints(input_plugin.plugin_object.load).get("options"))
        and output_plugin.plugin_object is not None
        and (output_option := get_type_hints(output_plugin.plugin_object.dump).get("options"))
    ):
        option_type, option_class = _("Input Options: "), input_option
        option_kwargs = {}
        if len(option_class.model_fields):
            typer.echo(option_type)
            option_kwargs = prompt_fields(option_class)
        root_project = input_plugin.plugin_object.load(in_path, option_class(**option_kwargs))
        sub_projects = root_project.split_tracks(max_track_count)
        middleware_with_options = []
        for middleware in middleware_manager.plugin_registry.values():
            if (
                (
                    Confirm.ask(
                        _("Enable {} middleware?").format(_(middleware.name)),
                        default=False,
                    )
                )
                and (middleware.plugin_object is not None)
                and (
                    middleware_option := get_type_hints(middleware.plugin_object.process).get(
                        "options"
                    )
                )
            ):
                option_type, option_class = (
                    _("Process Options: "),
                    middleware_option,
                )
                option_kwargs = {}
                if len(option_class.model_fields):
                    typer.echo(option_type)
                    option_kwargs = prompt_fields(option_class)
                middleware_with_options.append(
                    (
                        middleware.plugin_object.process,
                        option_class,
                        option_kwargs,
                    )
                )
        option_type, option_class = _("Output Options: "), output_option
        option_kwargs = {}
        if len(option_class.model_fields):
            typer.echo(option_type)
            option_kwargs = prompt_fields(option_class)
        for i, project in track(
            enumerate(sub_projects),
            description=_("Converting ..."),
            total=len(sub_projects),
        ):
            for (
                middleware_func,
                option_class,
                option_kwargs,
            ) in middleware_with_options:
                project = middleware_func(project, option_class(**option_kwargs))
            output_plugin.plugin_object.dump(
                out_dir / f"{in_path.stem}_{i + 1:02d}.{output_ext}",
                project,
                option_class(**option_kwargs),
            )
    else:
        typer.secho("Invalid options", err=True, color="red")


@app.command("merge")
def merge_projects(
    in_paths: Annotated[list[pathlib.Path], typer.Argument()],
    out_path: pathlib.Path = typer.Option(
        "", exists=False, dir_okay=False, callback=option_callback
    ),
) -> None:
    projects = []
    middleware_with_options = []
    for middleware in middleware_manager.plugin_registry.values():
        if (
            (
                Confirm.ask(
                    _("Enable {} middleware?").format(_(middleware.name)),
                    default=False,
                )
            )
            and (middleware.plugin_object is not None)
            and (
                middleware_option := get_type_hints(middleware.plugin_object.process).get("options")
            )
        ):
            option_type, option_class = (
                _("Process Options: "),
                middleware_option,
            )
            option_kwargs = {}
            if len(option_class.model_fields):
                typer.echo(option_type)
                option_kwargs = prompt_fields(option_class)
            middleware_with_options.append(
                (middleware.plugin_object.process, option_class, option_kwargs)
            )
    for in_path in in_paths:
        typer.echo(in_path)
        input_ext = in_path.suffix.lstrip(".").lower()
        input_plugin = plugin_manager.plugin_registry[input_ext]
        if input_plugin.plugin_object is not None and (
            input_option := get_type_hints(input_plugin.plugin_object.load).get("options")
        ):
            option_type, option_class = _("Input Options: "), input_option
            option_kwargs = {}
            if len(option_class.model_fields):
                typer.echo(option_type)
                option_kwargs = prompt_fields(option_class)
            project = input_plugin.plugin_object.load(in_path, option_class(**option_kwargs))
            for (
                middleware_func,
                option_class,
                option_kwargs,
            ) in middleware_with_options:
                project = middleware_func(project, option_class(**option_kwargs))
            projects.append(project)
        else:
            typer.secho("Invalid options", err=True, color="red")
            break
    output_ext = out_path.suffix.lstrip(".").lower()
    output_plugin = plugin_manager.plugin_registry[output_ext]
    if (
        projects
        and output_plugin.plugin_object is not None
        and (output_option := get_type_hints(output_plugin.plugin_object.dump).get("options"))
    ):
        project = project.merge_projects(projects)
        option_type, option_class = _("Output Options: "), output_option
        option_kwargs = {}
        if len(option_class.model_fields):
            typer.echo(option_type)
            option_kwargs = prompt_fields(option_class)
        output_plugin.plugin_object.dump(out_path, project, option_class(**option_kwargs))
    else:
        typer.secho("Invalid options", err=True, color="red")
