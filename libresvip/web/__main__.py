import argparse

from trame.app import dev, get_server
from trame_server.core import Server

from libresvip.web import i18n, layout, views


def init_server(server: Server):
    i18n.initialize(server)
    layout.initialize(server)


def _reload():
    server = get_server()
    dev.clear_change_listeners(server)
    dev.reload(i18n)
    dev.reload(views.converter)
    dev.reload(layout)
    init_server(server)
    server.controller.call("reload")


def main(**kwargs):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--port", type=int, default=8080)
    arg_parser.add_argument("--exec_mode", type=str, default="main")

    args = arg_parser.parse_known_args()[0]
    # Get or create server
    server = get_server()
    server.client_type = "vue3"
    server.controller.on_server_reload.add(_reload)

    init_server(server)

    # Start server
    server.start(**kwargs, port=args.port, exec_mode=args.exec_mode)


if __name__ == "__main__":
    main()
