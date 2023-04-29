import atexit
import os
import shutil
import tempfile

from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import html, router, trame, vuetify
from trame_server.core import Server

from libresvip.core.config import settings


def initialize(server: Server):
    state, ctrl = server.state, server.controller
    state.setdefault("lang", settings.language.value)
    state.setdefault("dark_mode", settings.dark_mode == "Dark")
    state.current_route = "Convert"
    state.menu_items = ["简体中文", "English"]
    state.trame__title = state.translations[state.lang]["LibreSVIP"]
    state.temp_dir = tempfile.mkdtemp(prefix="libresvip")
    os.makedirs(state.temp_dir, exist_ok=True)
    # state.trame__favicon

    def clean_temp_dir():
        shutil.rmtree(state.temp_dir, ignore_errors=True)

    atexit.register(clean_temp_dir)

    with SinglePageWithDrawerLayout(server) as layout:
        client_triggers = trame.ClientTriggers(
            ref="reload_trigger",
            reload="window.location.reload()",
            mounted="$vuetify.theme.dark = dark_mode",
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
            with vuetify.VTooltip(bottom=True):
                with vuetify.Template(v_slot_activator="{ on, attrs }"):
                    with vuetify.VBtn(
                        icon=True,
                        v_bind="attrs",
                        v_on="on",
                        click="$vuetify.theme.dark = !$vuetify.theme.dark",
                    ):
                        vuetify.VIcon("mdi-invert-colors")
                html.Span(v_text="translations[lang]['Switch Theme']")
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
                                v_text="translations[lang]['About Text 1']"
                            )
                            vuetify.VCardText(
                                v_text="translations[lang]['About Text 2']"
                            )
                            vuetify.VBtn(
                                v_text="translations[lang]['OK']",
                                click="show_about = false",
                                color="primary",
                            )
                html.Span(v_text="translations[lang]['About']")
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
                            "{{ translations[lang][item] }}",
                        )

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
