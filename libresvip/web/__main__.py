import argparse

from trame.app import dev, get_server

from . import i18n, layout, views


def init_server(server):
    i18n.initialize(server)
    layout.initialize(server)


def _reload():
    server = get_server()
    dev.clear_change_listeners(server)
    dev.reload(i18n)
    dev.reload(layout)
    dev.reload(views.converter)
    init_server(server)
    server.controller.call("reload")


def main(**kwargs):
    # Get or create server
    server = get_server()
    server.client_type = "vue3"
    server.controller.on_server_reload.add(_reload)

    init_server(server)

    # Start server
    server.start(**kwargs)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--port", type=int, default=8080)
    arg_parser.add_argument("--exec_mode", type=str, default="main")

    args = arg_parser.parse_known_args()[0]

    main(exec_mode=args.exec_mode)
