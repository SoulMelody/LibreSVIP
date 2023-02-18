import typer

from .commands import plugin_app, proj_app

app = typer.Typer(pretty_exceptions_enable=False)

app.add_typer(plugin_app, name="plugin")
app.add_typer(proj_app, name="proj")
