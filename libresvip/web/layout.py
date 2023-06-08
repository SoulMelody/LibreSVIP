import atexit
import base64
import os
import shutil
import tempfile

from trame.widgets import router, trame
from trame_client.widgets import html
from trame_server.core import Server
from trame_vuetify.ui.vuetify import SinglePageWithDrawerLayout
from trame_vuetify.widgets import vuetify

from libresvip.core.config import DarkMode, Language, save_settings, settings
from libresvip.core.constants import res_dir


def initialize(server: Server):
    state, ctrl = server.state, server.controller
    state.setdefault("lang", settings.language.value)
    state.setdefault("dark_mode", settings.dark_mode.value)
    state.current_route = "Convert"
    state.menu_items = ["简体中文", "English"]
    state.trame__title = (
        "LibreSVIP - " + state.translations[state.lang]["SVS Projects Converter"]
    )
    state.temp_dir = tempfile.mkdtemp(prefix="libresvip")
    os.makedirs(state.temp_dir, exist_ok=True)
    state.trame__favicon = (
        "data:image/x-icon;base64,"
        + base64.b64encode((res_dir / "libresvip.ico").read_bytes()).decode()
    )

    def clean_temp_dir():
        shutil.rmtree(state.temp_dir, ignore_errors=True)

    atexit.register(clean_temp_dir)

    def save_settings_to_disk():
        settings.language = Language(state.lang)
        settings.dark_mode = DarkMode(state.dark_mode)
        settings.auto_detect_input_format = state.auto_detect
        settings.reset_tasks_on_input_change = state.auto_reset
        settings.last_input_format = state.input_format
        settings.last_output_format = state.output_format
        save_settings()

    atexit.register(save_settings_to_disk)

    with SinglePageWithDrawerLayout(server) as layout:
        client_triggers = trame.ClientTriggers(
            ref="reload_trigger",
            reload="window.location.reload()",
            mounted="""
            switch (dark_mode) {
                case 'Light':
                    $vuetify.theme.dark = false
                    break
                case 'Dark':
                    $vuetify.theme.dark = true
                    break
                case 'System':
                    $vuetify.theme.dark = window.matchMedia('(prefers-color-scheme: dark)').matches
                    break
            }
            """,
        )
        ctrl.call = client_triggers.call
        layout.drawer._attr_names += [("mini_variant_sync", "v-bind:mini-variant.sync")]
        layout.drawer.mini_variant_sync = ("mini", False)
        layout.icon.click = "mini = !mini"
        layout.drawer.width = 200
        layout.footer.clear()
        layout.title._attr_names += ["v_text"]
        layout.title.v_text = "translations[lang][current_route]"
        layout.toolbar.dense = True

        with layout.toolbar:
            vuetify.VSpacer()
            with vuetify.VMenu(offset_y=True, transition="scale-transition"):
                with vuetify.Template(v_slot_activator="{ on }"):
                    with vuetify.VBtn(text=True, v_on="on"):
                        vuetify.VIcon("mdi-invert-colors")
                        html.Span(v_text="translations[lang]['Switch Theme']")
                        vuetify.VIcon("mdi-menu-down", small=True)
                with vuetify.VList():
                    with vuetify.VListItem(
                        v_for="(item, i) in ['Light', 'Dark']",
                        key="i",
                        value=["item"],
                        click="$vuetify.theme.dark = item === 'Dark'; dark_mode = item",
                    ):
                        vuetify.VListItemTitle(
                            "{{ translations[lang][item] }}",
                        )
                    with vuetify.VListItem(
                        click="$vuetify.theme.dark = window.matchMedia('(prefers-color-scheme: dark)').matches; dark_mode = 'System'",
                    ):
                        vuetify.VListItemTitle(
                            '{{ translations[lang]["System"] }}',
                        )
            with vuetify.VMenu(offset_y=True, transition="scale-transition"):
                with vuetify.Template(v_slot_activator="{ on }"):
                    with vuetify.VBtn(text=True, v_on="on"):
                        vuetify.VIcon("mdi-translate")
                        html.Span(v_text="lang")
                        vuetify.VIcon("mdi-menu-down", small=True)
                with vuetify.VList():
                    with vuetify.VListItem(
                        v_for="(item, i) in menu_items",
                        key="i",
                        value=["item"],
                        click="lang = item",
                    ):
                        vuetify.VListItemTitle(
                            "{{ item }}",
                        )
            with vuetify.VTooltip(bottom=True):
                with vuetify.Template(v_slot_activator="{ on, attrs }"):
                    with vuetify.VBtn(
                        icon=True, v_bind="attrs", v_on="on", click="show_about = true"
                    ):
                        vuetify.VIcon("mdi-information-outline")
                    with vuetify.VDialog(
                        v_model=("show_about", False), max_width="600px"
                    ):
                        with vuetify.VCard(classes="text-center"):
                            vuetify.VCardTitle(v_text="translations[lang]['LibreSVIP']")
                            with vuetify.VBtn(
                                href="https://github.com/SoulMelody/LibreSVIP",
                                target="_blank",
                                icon=True,
                            ):
                                vuetify.VIcon("mdi-github", size="50", color="grey")
                            vuetify.VCardText(
                                v_text="translations[lang]['LibreSVIP is an open-sourced, liberal and extensionable framework that can convert your singing synthesis projects between different file formats.']"
                            )
                            vuetify.VCardText(
                                v_text=r"translations[lang]['All people should have the right and freedom to choose. That\'s why we\'re committed to giving you a second chance to keep your creations free from the constraints of platforms and coterie.']"
                            )
                            vuetify.VBtn(
                                v_text="translations[lang]['OK']",
                                click="show_about = false",
                                color="primary",
                            )
                html.Span(v_text="translations[lang]['About']")

        with layout.content:
            with vuetify.VContainer(fluid=True):
                router.RouterView()

        with layout.footer:
            vuetify.VSpacer()
            with vuetify.VBtn(
                x_small=True,
                icon=True,
                click=ctrl.on_server_reload,
                classes="mx-2",
            ):
                vuetify.VIcon("mdi-autorenew", x_small=True)

        with layout.drawer:
            with vuetify.VList(shaped=True, v_model=("selected_route", 0)):
                with vuetify.VListItem(
                    v_for="(item, i) in router_items",
                    key="i",
                    value=["item"],
                    to=("item['route']", "/"),
                    click="current_route = item['title']",
                ):
                    with vuetify.VListItemIcon():
                        vuetify.VIcon("{{ item['icon'] }}")
                    with vuetify.VListItemContent():
                        vuetify.VListItemTitle(
                            "{{ translations[lang][item['title']] }}",
                        )
