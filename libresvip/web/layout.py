import atexit
import base64
import contextlib
import os
import shutil
import tempfile

from omegaconf.errors import OmegaConfBaseException
from trame_client.widgets import html, trame
from trame_server.core import Server
from trame_vuetify.ui.vuetify3 import SinglePageLayout
from trame_vuetify.widgets import vuetify3

import libresvip
from libresvip.core.config import DarkMode, Language, save_settings, settings
from libresvip.core.constants import res_dir
from libresvip.web.views import converter


def initialize(server: Server):
    state, ctrl = server.state, server.controller

    state.setdefault("lang", settings.language.value)
    state.setdefault("dark_mode", settings.dark_mode.value)
    state.current_route = "Convert"
    state.menu_items = ["简体中文", "English"]
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
        with contextlib.suppress(OmegaConfBaseException):
            settings.language = Language(state.lang)
            settings.dark_mode = DarkMode(state.dark_mode)
            settings.auto_detect_input_format = state.auto_detect
            settings.reset_tasks_on_input_change = state.auto_reset
            settings.last_input_format = state.input_format
            settings.last_output_format = state.output_format
            save_settings()

    atexit.register(save_settings_to_disk)

    with SinglePageLayout(server) as layout:
        reload_trigger = trame.JSEval(
            events=["reload"],
            exec="window.location.reload()",
        )
        ctrl.call = reload_trigger.exec

        trame.Style(
            """
            .app-copy {
                position: fixed !important;
                z-index: -1 !important;
                pointer-events: none !important;
                contain: size style !important;
                overflow: clip !important;
            }

            .app-transition {
                --clip-size: 0;
                --clip-pos: 0 0;
                clip-path: circle(var(--clip-size) at var(--clip-pos));
                transition: clip-path .35s ease-out;
            }
            """
        )
        change_theme_trigger = trame.JSEval(
            exec="""
            (() => {
                // Adapted from https://github.com/vuetifyjs/vuetify/blob/master/packages/docs/src/App.vue
                function hasScrollbar (el) {
                    if (!el || el.nodeType !== window.Node.ELEMENT_NODE) return false

                    const style = window.getComputedStyle(el)
                    return style.overflowY === 'scroll' || (style.overflowY === 'auto' && el.scrollHeight > el.clientHeight)
                }
                const x = window.performance.now()
                for (let i = 0; i++ < 1e7; i << 9 & 9 % 9 * 9 + 9);
                if (window.performance.now() - x > 10) return

                const el = window.document.querySelector('[data-v-app]')
                if (!el) return

                el.querySelectorAll('*').forEach(el => {
                    if (hasScrollbar(el)) {
                        el.dataset.scrollX = String(el.scrollLeft)
                        el.dataset.scrollY = String(el.scrollTop)
                    }
                })

                const copy = el.cloneNode(true)
                copy.classList.add('app-copy')
                const rect = el.getBoundingClientRect()
                copy.style.top = rect.top + 'px'
                copy.style.left = rect.left + 'px'
                copy.style.width = rect.width + 'px'
                copy.style.height = rect.height + 'px'

                const targetEl = window.document.querySelector('.mdi-invert-colors')
                if (!targetEl) return
                const targetRect = targetEl.getBoundingClientRect()
                window.console.log(targetRect)
                const left = targetRect.left + targetRect.width / 2 + window.scrollX
                const top = targetRect.top + targetRect.height / 2 + window.scrollY
                el.style.setProperty('--clip-pos', `${left}px ${top}px`)
                el.style.removeProperty('--clip-size')

                window.Vue.nextTick(() => {
                    el.classList.add('app-transition')
                    window.requestAnimationFrame(() => {
                        window.requestAnimationFrame(() => {
                            el.style.setProperty('--clip-size', Math.hypot(window.innerWidth, window.innerHeight) + 'px')
                        })
                    })
                })

                window.document.body.append(copy)

                copy.querySelectorAll('[data-scroll-x], [data-scroll-y]').forEach(el => {
                    if (el.dataset.scrollX) el.scrollLeft = +el.dataset.scrollX
                    if (el.dataset.scrollY) el.scrollTop = +el.dataset.scrollY
                })

                function onTransitionend (e) {
                    if (e.target === e.currentTarget) {
                    copy.remove()
                    el.removeEventListener('transitionend', onTransitionend)
                    el.removeEventListener('transitioncancel', onTransitionend)
                    el.classList.remove('app-transition')
                    el.style.removeProperty('--clip-size')
                    el.style.removeProperty('--clip-pos')
                    }
                }
                el.addEventListener('transitionend', onTransitionend)
                el.addEventListener('transitioncancel', onTransitionend)
            })()
            """,
        )

        @state.change("dark_mode")
        def change_theme(dark_mode: str, *args, **kwargs):
            change_theme_trigger.exec()

        layout.icon.v_show = False
        layout.footer.clear()
        layout.title._attr_names += ["v_text"]
        layout.title.v_text = "translations[lang][current_route]"
        layout.toolbar.dense = True
        layout.root.theme = ("""
            ((dark_mode) => {
                switch (dark_mode) {
                    case 'Light':
                        return 'light'
                        break
                    case 'Dark':
                        return 'dark'
                        break
                    case 'System':
                        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
                        break
                }
            })(dark_mode)
        """,)

        with layout.toolbar:
            vuetify3.VSpacer()
            with vuetify3.VMenu(offset_y=True, transition="scale-transition"):
                with vuetify3.Template(v_slot_activator="{ props }"):
                    with vuetify3.VBtn(text=True, v_bind="props"):
                        vuetify3.VIcon("mdi-invert-colors")
                        html.Span(v_text="translations[lang]['Switch Theme']")
                        vuetify3.VIcon("mdi-menu-down", small=True)
                with vuetify3.VList():
                    with vuetify3.VListItem(
                        v_for="(item, i) in ['Light', 'Dark', 'System']",
                        key="i",
                        value=["item"],
                        click="dark_mode = item",
                    ):
                        vuetify3.VListItemTitle(
                            "{{ translations[lang][item] }}",
                        )
            with vuetify3.VMenu(offset_y=True, transition="scale-transition"):
                with vuetify3.Template(v_slot_activator="{ props }"):
                    with vuetify3.VBtn(text=True, v_bind="props"):
                        vuetify3.VIcon("mdi-translate")
                        html.Span(v_text="lang")
                        vuetify3.VIcon("mdi-menu-down", small=True)
                with vuetify3.VList():
                    with vuetify3.VListItem(
                        v_for="(item, i) in menu_items",
                        key="i",
                        value=["item"],
                        click="lang = item",
                    ):
                        vuetify3.VListItemTitle(
                            "{{ item }}",
                        )
            with vuetify3.VTooltip(location="bottom"):
                with vuetify3.Template(v_slot_activator="{ props }"):
                    with vuetify3.VBtn(
                        icon=True, v_bind="props", click="show_about = true"
                    ):
                        vuetify3.VIcon("mdi-information-outline")
                    with vuetify3.VDialog(
                        v_model=("show_about", False), width="auto",
                    ):
                        with vuetify3.VCard(
                            append_icon="$close",
                            title=("translations[lang]['About']", ""),
                        ):
                            with vuetify3.Template(v_slot_append=""):
                                vuetify3.VBtn(
                                    icon="$close",
                                    click="show_about = false",
                                    variant="text",
                                )
                            vuetify3.VDivider()
                            vuetify3.VCardTitle(
                                "LibreSVIP",
                                classes="text-center text-h4",
                            )
                            with vuetify3.VCardText(classes="text-center"):
                                vuetify3.VLabel(
                                    f"{{{{ translations[lang]['Version'] + ': {libresvip.__version__}' }}}}"
                                )
                            with vuetify3.VCardText(classes="text-center"):
                                vuetify3.VLabel(
                                    "{{ translations[lang]['Author: SoulMelody'] }}"
                                )
                            with vuetify3.VCardText(classes="text-center"):
                                with vuetify3.VBtn(
                                    href="https://space.bilibili.com/175862486",
                                    target="_blank",
                                    prepend_icon="mdi-television-classic",
                                    rounded="xl",
                                    variant="tonal",
                                    __properties=["target"]
                                ):
                                    vuetify3.VLabel("{{ translations[lang]['Author\\'s Profile'] }}")
                                with vuetify3.VBtn(
                                    href="https://github.com/SoulMelody/LibreSVIP",
                                    target="_blank",
                                    prepend_icon="mdi-github",
                                    rounded="xl",
                                    variant="tonal",
                                    __properties=["target"]
                                ):
                                    vuetify3.VLabel("{{ translations[lang]['Repo URL'] }}")
                            vuetify3.VCardText(
                                v_text="translations[lang]['LibreSVIP is an open-sourced, liberal and extensionable framework that can convert your singing synthesis projects between different file formats.']",
                                classes="text-center",
                            )
                            vuetify3.VCardText(
                                v_text=r"translations[lang]['All people should have the right and freedom to choose. That\'s why we\'re committed to giving you a second chance to keep your creations free from the constraints of platforms and coterie.']",
                                classes="text-center",
                            )
                            with vuetify3.VCardActions():
                                vuetify3.VSpacer()
                                vuetify3.VBtn(
                                    v_text="translations[lang]['OK']",
                                    click="show_about = false",
                                    color="primary",
                                    variant="elevated"
                                )
                                vuetify3.VSpacer()
                html.Span(v_text="translations[lang]['About']")

        with layout.content:
            with vuetify3.VContainer(fluid=True):
                converter.initialize(server=server)

        with layout.footer:
            vuetify3.VSpacer()
            with vuetify3.VBtn(
                x_small=True,
                icon=True,
                click=ctrl.on_server_reload,
                size="x-small"
            ):
                vuetify3.VIcon("mdi-autorenew", size="x-small")

