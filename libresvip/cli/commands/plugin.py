import enum
import gettext
import pathlib
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
        typer.echo(f"未找到插件 {plugin_name}。")


def print_plugin_summary(plugins):
    console = Console(color_system="256")
    if not plugins:
        console.print(gettext.gettext("No plugins are currently installed.\n"))
    margin = " " * 2
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", justify="left", style="cyan")
    table.add_column("名称", justify="left", style="cyan")
    table.add_column("版本", justify="left", style="cyan")
    table.add_column("作者", justify="left", style="cyan")
    table.add_column("标识符", justify="left", style="cyan")
    table.add_column("适用格式", justify="left", style="cyan")
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
    typer.echo(f"插件：{plugin.name}\t版本：{plugin.version_string}\t作者：{plugin.author}")
    if plugin.website:
        typer.echo(f"\n主页：{plugin.website}")
    typer.echo(f"\n此插件适用于 {plugin.file_format} (*.{plugin.suffix})。")
    typer.echo(
        f'若要使用此插件，请在转换时指定 "-i {plugin.file_format}"（输入）或 "-o {plugin.file_format}"（输出）。'
    )
    if plugin.description:
        typer.echo(f"\n描述：\n{plugin.description}")
    op_arr = ["输入", "输出"]
    options_arr = [
        get_type_hints(plugin.plugin_object.load).get("options", None),
        get_type_hints(plugin.plugin_object.dump).get("options", None),
    ]
    for i in range(2):
        if options_arr[i] is None:
            continue
        typer.echo(f"\n本插件可指定以下{op_arr[i]}转换选项：")
        option: ModelField
        for option in options_arr[i].__fields__.values():
            if issubclass(option.type_, (bool, int, float, str, enum.Enum)):
                typer.echo(
                    f"\n  {option.name} = {option.type_.__name__}    {option.field_info.description}"
                )
                if option.default is not None:
                    typer.echo(f"\t默认值：{option.default}")
                if issubclass(option.type_, enum.Enum):
                    typer.echo("  可用值如下：")
                    annotations = get_type_hints(option.type_, include_extras=True)
                    for enum_item in option.type_:
                        if enum_item.name in annotations:
                            annotated_args = get_args(annotations[enum_item.name])
                            if len(annotated_args) == 2:
                                _, enum_field = annotated_args
                                typer.echo(
                                    f"    {enum_item.value}\t=>\t{enum_field.title}"
                                )
            elif issubclass(option.type_, BaseComplexModel):
                typer.echo(
                    f"\n  {option.name} = {option.type_.__name__}    {option.field_info.description}"
                )
                typer.echo("  可用值如下：")
                for field in option.type_.__fields__.values():
                    if hasattr(field.type_, "__name__"):
                        typer.echo(f"    {field.name} = {field.type_.__name__}")
                    else:
                        typer.echo(f"    {field.name} = {get_args(field.type_)}")
                typer.echo(f"\t默认值：{option.type_.default_repr()}")
    typer.echo("\n--------------------------------------------------\n")
