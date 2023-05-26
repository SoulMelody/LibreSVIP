import enum
import pathlib
from gettext import gettext as _
from typing import get_args, get_type_hints

import typer

try:
    from pydantic.fields import ModelField
except ImportError:
    from pydantic.fields import Field as ModelField
from rich.console import Console
from rich.table import Table

from libresvip.extension.manager import plugin_manager, plugin_registry
from libresvip.model.base import BaseComplexModel

app = typer.Typer()


@app.command("list")
def list_plugins():
    print_plugin_summary(plugin_registry.values())


@app.command()
def install(path: pathlib.Path):
    plugin_manager.installFromZIP(path)


@app.command()
def detail(plugin_name: str):
    if plugin_name in plugin_registry:
        print_plugin_details(plugin_registry[plugin_name])
    else:
        typer.echo(_("Cannot find plugin ") + f"{plugin_name}!")


def print_plugin_summary(plugins):
    console = Console(color_system="256")
    if not plugins:
        console.print(_("No plugins are currently installed."))
    margin = " " * 2
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column(_("No."), justify="left", style="cyan")
    table.add_column(_("Name"), justify="left", style="cyan")
    table.add_column(_("Version"), justify="left", style="cyan")
    table.add_column(_("Author"), justify="left", style="cyan")
    table.add_column(_("Identifier"), justify="left", style="cyan")
    table.add_column(_("Applicable file format"), justify="left", style="cyan")
    for num, plugin in enumerate(plugins):
        table.add_row(
            f"[{num + 1}] ",
            plugin.name + margin,
            plugin.version_string + margin,
            plugin.author + margin,
            plugin.suffix + margin,
            f"{plugin.file_format} (*.{plugin.suffix}){margin}",
        )
    console.print(table)


def print_plugin_details(plugin):
    typer.echo()
    typer.echo("--------------------------------------------------\n")
    typer.echo(
        f"{{}}{plugin.name}\t{{}}{plugin.version_string}\t{{}}{plugin.author}".format(
            _("Plugin: "),
            _("Version: "),
            _("Author: "),
        )
    )
    if plugin.website:
        typer.echo("\n" + _("Website: ") + plugin.website)
    typer.echo(
        "\n"
        + "{} {}.".format(
            _("This plugin is applicable to"),
            _(f"{plugin.file_format} (*.{plugin.suffix})"),
        )
    )
    typer.echo(
        _(
            "If you want to use this plugin, please specify '-i {}' (input) or '-o {}' (output) when converting."
        ).format(plugin.suffix.lower(), plugin.suffix.lower())
    )
    if plugin.description:
        typer.echo("\n{}\n{}".format(_("Description: "), _(plugin.description)))
    op_arr = [_("input"), _("output")]
    options_arr = [
        get_type_hints(plugin.plugin_object.load).get("options", None),
        get_type_hints(plugin.plugin_object.dump).get("options", None),
    ]
    for op, options in zip(op_arr, options_arr):
        if options is None:
            continue
        typer.echo(
            _("This plugin supports the following {} conversion options:").format(op)
        )
        option: ModelField
        for option in options.__fields__.values():
            if issubclass(option.type_, (bool, int, float, str, enum.Enum)):
                typer.echo(
                    "\n  "
                    + "{} = {}    {}".format(
                        _(option.name),
                        option.type_.__name__,
                        _(option.field_info.description),
                    )
                )
                if option.default is not None:
                    typer.echo(f"\t{{}}{option.default}".format(_("Default: ")))
                if issubclass(option.type_, enum.Enum):
                    typer.echo("  " + _("Available values:"))
                    annotations = get_type_hints(option.type_, include_extras=True)
                    for enum_item in option.type_:
                        if enum_item.name in annotations:
                            annotated_args = get_args(annotations[enum_item.name])
                            if len(annotated_args) == 2:
                                enum_type, enum_field = annotated_args
                                typer.echo(
                                    "\t{}\t=>\t{}".format(
                                        enum_item.value, _(enum_field.title)
                                    )
                                )
            elif issubclass(option.type_, BaseComplexModel):
                typer.echo(
                    "\n  "
                    + "{} = {}    {}".format(
                        _(option.name),
                        option.type_.__name__,
                        _(option.field_info.description),
                    )
                )
                typer.echo("  " + _("Available fields:"))
                for field in option.type_.__fields__.values():
                    if hasattr(field.type_, "__name__"):
                        typer.echo(f"    {field.name} = {field.type_.__name__}")
                    else:
                        typer.echo(f"    {field.name} = {get_args(field.type_)}")
                typer.echo("\t" + _("Default: ") + option.type_.default_repr())
    typer.echo("\n--------------------------------------------------\n")
