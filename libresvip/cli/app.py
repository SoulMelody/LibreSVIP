import typer

from .commands import conf_app, plugin_app, proj_app

app = typer.Typer(pretty_exceptions_enable=False)

app.add_typer(conf_app, name="conf")
app.add_typer(plugin_app, name="plugin")
app.add_typer(proj_app, name="proj")
