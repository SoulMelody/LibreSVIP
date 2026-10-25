from typing import Annotated

import typer

from libresvip import __version__
from libresvip.utils.translation import gettext_lazy as _

from .commands import conf_app, mcp_app, plugin_app, proj_app, rpc_app

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"LibreSVIP {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=_version_callback,
            is_eager=True,
            help=_("Show the version and exit"),
        ),
    ] = False,
) -> None:
    pass


app.add_typer(conf_app, name="conf")
app.add_typer(mcp_app, name="mcp")
app.add_typer(plugin_app, name="plugin")
app.add_typer(proj_app, name="proj")
app.add_typer(rpc_app, name="rpc")
