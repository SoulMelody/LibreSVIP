from gettext import gettext as _
from gettext import translation

from trame_server.core import Server

from libresvip.core.constants import res_dir

messages = [
    _("SVS Projects Converter"),
    _("Convert"),
    _("Visualize"),
    _("Plugins"),
    _("Settings"),
    _("About"),
    _("Help"),
    _("Links"),
    _("Export"),
    _("Switch Theme"),
    _("Switch Language"),
    _("OK"),
    _("Close"),
    _("Author"),
    _("Version"),
    _("Introduction"),
    _("Auto detect import format"),
    _("Reset list when import format changed"),
    _("Import from"),
    _("Import format"),
    _("Export to"),
    _("Export format"),
    _("Choose file format"),
    _("Next"),
    _("Back"),
    _("File operations"),
    _("Import project"),
    _("Import Options"),
    _("Export Options"),
    _("Advanced Options"),
    _("Conversion Successful"),
    _("Conversion Failed"),
    _("Drag and drop files here or click to upload"),
    _(
        "LibreSVIP is an open-sourced, liberal and extensionable framework that can convert your singing synthesis projects between different file formats."
    ),
    _(
        "All people should have the right and freedom to choose. That's why we're committed to giving you a second chance to keep your creations free from the constraints of platforms and coterie."
    ),
    _("Plugin List"),
    _("Install a Plugin"),
]


def initialize(server: Server):
    state = server.state
    chinese_translation = translation(
        "libresvip", localedir=res_dir / "locales", languages=["zh_CN"]
    )
    state.translations = {
        "简体中文": {msg: chinese_translation.gettext(msg) for msg in messages},
        "English": {msg: msg for msg in messages},
    }
