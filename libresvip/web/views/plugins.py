import io

from pkg_resources.extern.more_itertools import chunked
from trame_client.widgets import html
from trame_server.core import Server
from trame_vuetify.widgets import vuetify3

from libresvip.extension.manager import plugin_manager


def initialize(server: Server):
    state = server.state

    all_pages = list(chunked(state.plugin_details.values(), 5))

    @state.change("plugin_page")
    def plugin_paging(plugin_page, **kwargs):
        state.plugin_cur_page = all_pages[plugin_page - 1]

    @state.change("plugin_file")
    def handle(plugin_file, **kwargs):
        if plugin_file:
            plugin_manager.installFromZIP(io.BytesIO(plugin_file["content"]))

    state.setdefault("plugin_file", "")
    state.setdefault("plugin_page", 1)
    state.setdefault("plugin_cur_page", all_pages[state.plugin_page - 1])

    with vuetify3.VToolbar(dense=True):
        vuetify3.VToolbarTitle("{{ translations[lang]['Plugins List'] }}")
        vuetify3.VSpacer()
        with vuetify3.VTooltip(location="bottom"):
            with vuetify3.Template(v_slot_activator="{ props }"):
                with vuetify3.VBtn(
                    icon=True,
                    v_bind="props",
                    click="trame.refs['plugin_file_input'].click()",
                ):
                    vuetify3.VIcon("mdi-puzzle-plus-outline")
                html.Input(
                    change="""
                    for (i = 0; i < $event.target.files.length; i++) {
                        plugin_file = event.target.files.item(i);
                    };
                    flushState('plugin_file');""",
                    type="file",
                    ref="plugin_file_input",
                    accept=".zip",
                    v_show="false",
                    __events=["change"],
                )
            html.Span("{{ translations[lang]['Install a Plugin'] }}")
    with vuetify3.VList():
        with vuetify3.VListItem(
            v_for="(item, i) in plugin_cur_page",
            key="i",
            value=["item"],
            lines="three",
        ):
            with vuetify3.VListItem():
                with vuetify3.VListItemTitle():
                    with vuetify3.VListItem(v_if="item.icon_base64"):
                        vuetify3.VImg(
                            src=("'data:image/png;base64,' + item.icon_base64", "")
                        )
                    html.Span(v_text="item.name")
                with vuetify3.VListItemSubtitle():
                    html.Span("{{translations[lang]['Author']}}：")
                    vuetify3.VBtn(
                        "{{item.author}}",
                        rounded=True,
                        small=True,
                        href=("item.website", "#"),
                        target="_blank",
                    )
                    html.Span("{{translations[lang]['Version']}}： ")
                    vuetify3.VChip(v_text="item.version", small=True)
                vuetify3.VListItemSubtitle(
                    v_html="translations[lang][item.description]",
                )
            with vuetify3.VListItemAction():
                with vuetify3.VBtn(
                    color="primary",
                    icon=True,
                ):
                    vuetify3.VIcon("mdi-update")
            with vuetify3.VListItemAction():
                with vuetify3.VBtn(
                    color="primary",
                    icon=True,
                ):
                    vuetify3.VIcon("mdi-delete-outline")
    with vuetify3.Template():
        vuetify3.VPagination(
            v_model="plugin_page",
            length=len(all_pages),
        )
