import gettext
from gettext import gettext as _

from trame_server.core import Server

from libresvip.core.config import Language
from libresvip.core.constants import PACKAGE_NAME, res_dir
from libresvip.extension.messages import messages_iterator

messages = [
    _("SVS Projects Converter"),
    _("Convert"),
    _("Plugins"),
    _("Settings"),
    _("About"),
    _("Help"),
    _("Export"),
    _("Switch Theme"),
    _("Light"),
    _("Dark"),
    _("System"),
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
    _("Invalid integer"),
    _("Invalid float"),
]


def flattern_messages(msg_dict: dict):
    msgs = []
    for msg in msg_dict.values():
        if isinstance(msg, dict):
            msgs.extend(flattern_messages(msg))
        elif isinstance(msg, list):
            msgs.extend(
                sum(
                    (flattern_messages(elem) for elem in msg if isinstance(elem, dict)),
                    [],
                )
            )
        else:
            msgs.append(msg)
    return msgs


plugin_msgs = []

for plugin_suffix, plugin_metadata, info_path in messages_iterator():
    plugin_msgs.extend(flattern_messages(plugin_metadata))

messages.extend(set(plugin_msgs))


def initialize(server: Server):
    state = server.state

    @state.change("lang")
    def change_lang(lang, **kwargs):
        state.trame__title = (
            "LibreSVIP - " + state.translations[state.lang]["SVS Projects Converter"]
        )
        try:
            translation = gettext.translation(PACKAGE_NAME, res_dir / "locales", [Language(lang).to_locale()], fallback=True)
            gettext.textdomain(PACKAGE_NAME)
        except OSError:
            translation = gettext.NullTranslations()
            gettext.textdomain("messages")
        translation.install(
            names=["gettext", "ngettext"]
        )

    gettext.bindtextdomain(PACKAGE_NAME, res_dir / "locales")
    chinese_translation = gettext.translation(
        "libresvip", localedir=res_dir / "locales", languages=["zh_CN"]
    )
    all_messages = {
        "简体中文": {
            msg: chinese_translation.gettext(msg).replace("\n", "<br>")
            for msg in messages
        },
        "English": {msg: msg.replace("\n", "<br>") for msg in messages},
    }
    state.setdefault("translations", all_messages)
