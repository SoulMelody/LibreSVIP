import io

from trame.widgets import html, vuetify
from trame_server.core import Server

from libresvip.extension.manager import plugin_registry


def initialize(server: Server):
    if "svg" not in plugin_registry:
        return

    state = server.state

    state["svg_data"] = ""

    html.Div(v_html="svg_data")
