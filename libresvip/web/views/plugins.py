import io

from more_itertools import chunked
from trame_client.widgets import html
from trame_server.core import Server
from trame_vuetify.widgets import vuetify

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

    with vuetify.VToolbar(dense=True):
        vuetify.VToolbarTitle("{{ translations[lang]['Plugins List'] }}")
        vuetify.VSpacer()
        with vuetify.VTooltip(bottom=True):
            with vuetify.Template(v_slot_activator="{ on, attrs }"):
                with vuetify.VBtn(
                    icon=True,
                    v_bind="attrs",
                    v_on="on",
                    click="getRef('plugin_file_input').click()",
                ):
                    vuetify.VIcon("mdi-puzzle-plus-outline")
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
    with vuetify.VList():
        with vuetify.VListItem(
            v_for="(item, i) in plugin_cur_page",
            key="i",
            value=["item"],
            three_line=True,
        ):
            with vuetify.VListItemContent():
                with vuetify.VListItemTitle():
                    with vuetify.VListItemAvatar(v_if="item.icon_base64"):
                        vuetify.VImg(
                            src=("'data:image/png;base64,' + item.icon_base64", "")
                        )
                    html.Span(v_text="item.name")
                with vuetify.VListItemSubtitle():
                    html.Span("{{translations[lang]['Author']}}：")
                    vuetify.VBtn(
                        "{{item.author}}",
                        rounded=True,
                        small=True,
                        href=("item.website", "#"),
                        target="_blank",
                    )
                    html.Span("{{translations[lang]['Version']}}： ")
                    vuetify.VChip(v_text="item.version", small=True)
                vuetify.VListItemSubtitle(
                    v_html="item.description",
                )
            with vuetify.VListItemAction():
                with vuetify.VBtn(
                    color="primary",
                    icon=True,
                ):
                    vuetify.VIcon("mdi-update")
            with vuetify.VListItemAction():
                with vuetify.VBtn(
                    color="primary",
                    icon=True,
                ):
                    vuetify.VIcon("mdi-delete-outline")
    with vuetify.Template():
        vuetify.VPagination(
            v_model="plugin_page",
            length=len(all_pages),
        )
