__lazy_modules__ = ["libresvip.cli.mcp.server"]

import typer

from libresvip.cli.mcp.server import mcp

app = typer.Typer()


@app.command()
def serve() -> None:
    """Expose project load, middleware, and save as an MCP server on stdio."""
    mcp.stdio()
