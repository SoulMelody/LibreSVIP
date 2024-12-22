from typing import Annotated

import typer

from libresvip.core.config import save_settings, settings
from libresvip.utils.translation import gettext_lazy as _

app = typer.Typer()


@app.command("list")
def list_configurations() -> None:
    for name, value in settings.model_dump().items():
        typer.echo(f"{name}: {value}")


def conf_key_callback(value: str) -> str:
    if value not in ["language"]:
        raise typer.BadParameter(
            _("Setting {} is not supported in cli mode.").format(value),
        )
    return value


@app.command("set")
def set_configuration(
    name: Annotated[str, typer.Argument(callback=conf_key_callback)],
    value: Annotated[str, typer.Argument()],
) -> None:
    setattr(settings, name, value)
    save_settings()
    typer.echo(_("Set {} to {}").format(name, value))
