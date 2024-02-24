import pathlib
from typing import Optional, get_type_hints

import typer
from loguru import logger

from libresvip.cli.prompt import prompt_fields
from libresvip.extension.manager import plugin_manager
from libresvip.model.base import InstrumentalTrack
from libresvip.utils import gettext_lazy as _

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
        options = []
        for option_type, option_class in {
            _("Input Options: "): input_option,
            _("Output Options: "): output_option,
        }.items():
            option_kwargs = {}
            if len(option_class.model_fields):
                typer.echo(option_type)
                option_kwargs = prompt_fields(option_class)
            options.append(option_class(**option_kwargs))
        project = input_plugin.plugin_object.load(in_path, options[0])
        output_plugin.plugin_object.dump(out_path, project, options[1])
    else:
        logger.error("Invalid options")


@app.command("accomp")
def add_accompaniment(
    in_path: pathlib.Path = typer.Argument(
        "", exists=True, dir_okay=False, callback=option_callback
    ),
    audio_path: pathlib.Path = typer.Argument("", exists=True, dir_okay=False),
    offset: int = typer.Option(0, help=_("Offset in milliseconds")),
    mute: bool = typer.Option(False, help=_("Mute other tracks")),
) -> None:
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
    else:
        logger.error("Invalid options")
        return

    if mute:
        for track in project.track_list:
            track.mute = True
    project.track_list.append(
        InstrumentalTrack(
            audio_file_path=str(audio_path),
            offset=offset,
        )
    )

    if input_plugin.plugin_object is not None and (
        output_option := get_type_hints(input_plugin.plugin_object.dump).get("options")
    ):
        option_type, option_class = _("Output Options: "), output_option
        option_kwargs = {}
        if len(option_class.model_fields):
            typer.echo(option_type)
            option_kwargs = prompt_fields(option_class)
        input_plugin.plugin_object.dump(in_path, project, option_class(**option_kwargs))
    else:
        logger.error("Invalid options")
