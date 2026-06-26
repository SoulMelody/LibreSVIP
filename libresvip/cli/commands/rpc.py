import asyncio

import typer

from libresvip.cli.rpc.server import run_grpc_server

app = typer.Typer()


@app.command()
def server(
    host: str = "127.0.0.1",
    port: int = 15150,
) -> None:
    run_kwargs = {}
    asyncio.run(run_grpc_server(host=host, port=port), **run_kwargs)
