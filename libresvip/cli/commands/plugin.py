import enum
from collections.abc import ValuesView
from typing import get_args, get_type_hints

import typer
from rich.console import Console
from rich.table import Table

from libresvip.core.config import save_settings, settings
from libresvip.extension.manager import plugin_manager
from libresvip.extension.meta_info import FormatProviderPluginInfo
from libresvip.model.base import BaseComplexModel
from libresvip.utils.translation import gettext_lazy as _

app = typer.Typer()


@app.command()
def toggle(identifier: str) -> None:
    if identifier in plugin_manager.plugin_registry:
        try:
            settings.disabled_plugins.append(identifier)
            plugin_manager.import_plugins(reload=True)
            assert identifier not in plugin_manager.plugin_registry
            save_settings()
            typer.secho(_("The plugin is successfully disabled."), fg="green")
        except AssertionError:
            typer.secho(_("Failed to disable the plugin!"), err=True, fg="red")
    elif identifier in settings.disabled_plugins:
        try:
            settings.disabled_plugins.remove(identifier)
            plugin_manager.import_plugins(reload=True)
            assert identifier in plugin_manager.plugin_registry
            save_settings()
            typer.secho(_("The plugin is successfully enabled."), fg="green")
        except AssertionError:
            typer.secho(_("Failed to enable the plugin!"), err=True, fg="red")
    else:
        typer.secho(_("Unable to find the plugin."), fg="yellow")


@app.command("list")
def list_plugins() -> None:
    print_plugin_summary(plugin_manager.plugin_registry.values())


@app.command()
def detail(plugin_name: str) -> None:
    if plugin_name in plugin_manager.plugin_registry:
        print_plugin_details(plugin_manager.plugin_registry[plugin_name])
    else:
        typer.echo(_("Cannot find plugin ") + f"{plugin_name}!", err=True)


def print_plugin_summary(
    plugins: ValuesView[FormatProviderPluginInfo],
) -> None:
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
        format_desc = f"{_(plugin.file_format)} (*.{plugin.suffix})"
        table.add_row(
            f"[{num + 1}] ",
            plugin.name + margin,
            str(plugin.version) + margin,
            plugin.author + margin,
            plugin.suffix + margin,
            format_desc + margin,
        )
    console.print(table)


def print_plugin_details(plugin: FormatProviderPluginInfo) -> None:
    if plugin.plugin_object is None:
        return
    typer.echo()
    typer.echo("--------------------------------------------------\n")
    typer.echo(
        f"{{}}{plugin.name}\t{{}}{plugin.version!s}\t{{}}{plugin.author}".format(
            _("Plugin: "),
            _("Version: "),
            _("Author: "),
        )
    )
    if plugin.website:
        typer.echo("\n" + _("Website: ") + plugin.website)
    format_desc = f"{_(plugin.file_format)} (*.{plugin.suffix})"
    typer.echo("\n" + f'{_("This plugin is applicable to")} {format_desc}.')
    typer.echo(
        _(
            "If you want to use this plugin, please specify '-i {}' (input) or '-o {}' (output) when converting."
        ).format(plugin.suffix.lower(), plugin.suffix.lower())
    )
    if plugin.description:
        typer.echo(f'\n{_("Description: ")}\n{_(plugin.description)}')
    op_arr = [_("input"), _("output")]
    options_arr = [
        get_type_hints(plugin.plugin_object.load).get("options", None),
        get_type_hints(plugin.plugin_object.dump).get("options", None),
    ]
    for op, options in zip(op_arr, options_arr):
        if options is None:
            continue
        typer.echo(_("This plugin supports the following {} conversion options:").format(op))
        for field_info in options.model_fields.values():
            if issubclass(field_info.annotation, (bool, int, float, str, enum.Enum)):
                typer.echo(
                    "\n  "
                    + f"{_(field_info.title)} = {field_info.annotation.__name__}    {_(field_info.description)}"
                )
                if field_info.default is not None:
                    typer.echo(f"\t{{}}{field_info.default}".format(_("Default: ")))
                if issubclass(field_info.annotation, enum.Enum):
                    typer.echo("  " + _("Available values:"))
                    annotations = get_type_hints(field_info.annotation, include_extras=True)
                    for enum_item in field_info.annotation:
                        if enum_item.name in annotations:
                            annotated_args = get_args(annotations[enum_item.name])
                            if len(annotated_args) == 2:
                                enum_type, enum_field = annotated_args
                                typer.echo(f"\t{enum_item.value}\t=>\t{_(enum_field.title)}")
            elif issubclass(field_info.annotation, BaseComplexModel):
                typer.echo(
                    "\n  "
                    + f"{_(field_info.title)} = {field_info.annotation.__name__}    {_(field_info.description)}"
                )
                typer.echo("  " + _("Available fields:"))
                for field in field_info.annotation.model_fields.values():
                    if hasattr(field.annotation, "__name__"):
                        typer.echo(f"    {field.title} = {field.annotation.__name__}")
                    else:
                        typer.echo(f"    {field.title} = {get_args(field.annotation)}")
                typer.echo("\t" + _("Default: ") + field_info.annotation.default_repr())
    typer.echo("\n--------------------------------------------------\n")
