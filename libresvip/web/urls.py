from trame.widgets import vuetify
from trame_router.ui.router import RouterViewLayout
from trame_server.core import Server

from libresvip.web.views import converter, plugins


def initialize(server: Server):
    state = server.state

    state.router_items = [
        {
            "title": "Convert",
            "icon": "mdi-sync",
            "route": "/",
        },
        {
            "title": "Plugins",
            "icon": "mdi-puzzle-outline",
            "route": "/plugin",
        },
        {
            "title": "Settings",
            "icon": "mdi-cog-outline",
            "route": "/settings",
        },
    ]

    with RouterViewLayout(server, "/"):
        converter.initialize(server)

    with RouterViewLayout(server, "/plugin"):
        plugins.initialize(server)

    with RouterViewLayout(server, "/settings"):
        with vuetify.VCard():
            vuetify.VCardTitle("This is settings")
