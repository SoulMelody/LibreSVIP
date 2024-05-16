import pathlib
import plistlib

# Use like this: dmgbuild -s settings.py "Test Volume" test.dmg

# You can actually use this file for your own application (not just TextEdit)
# by doing e.g.
#
#   dmgbuild -s settings.py -D app=/path/to/My.app "My Application" MyApp.dmg

# .. Useful stuff ..............................................................

application = defines.get("app", "dist/LibreSVIP.app")  # type: ignore[name-defined] # noqa: F821
appname = pathlib.Path(application).name


def icon_from_app(app_path: str) -> str:
    plist_path = pathlib.Path(app_path) / "Contents" / "Info.plist"
    with plist_path.open("rb") as f:
        plist = plistlib.load(f)
    return str(pathlib.Path(app_path) / "Contents" / "Resources" / plist["CFBundleIconFile"])


# .. Basics ....................................................................


# Volume format (see hdiutil create -help)
format = defines.get("format", "UDBZ")  # type: ignore[name-defined] # noqa: A001,F821

# Volume size (must be large enough for your files)
size = defines.get("size", "150M")  # type: ignore[name-defined] # noqa: F821

# Files to include
files = [application]

# Symlinks to create
symlinks = {"Applications": "/Applications"}

# Volume icon
#
# You can either define icon, in which case that icon file will be copied to the
# image, *or* you can define badge_icon, in which case the icon file you specify
# will be used to badge the system's Removable Disk icon
#
# icon = icon_from_app(application)
badge_icon = icon_from_app(application)

# Where to put the icons
icon_locations = {appname: (140, 120), "Applications": (500, 120)}

# .. Window configuration ......................................................

background = "builtin-arrow"

show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180

# Window position in ((x, y), (w, h)) format
window_rect = ((100, 100), (640, 280))

# Select the default view; must be one of
#
#    'icon-view'
#    'list-view'
#    'column-view'
#    'coverflow'
#
default_view = "icon-view"

# General view configuration
show_icon_preview = False

# Set these to True to force inclusion of icon/list view settings (otherwise
# we only include settings for the default view)
include_icon_view_settings = "auto"
include_list_view_settings = "auto"

# .. Icon view configuration ...................................................

arrange_by = None
grid_offset = (0, 0)
grid_spacing = 120
scroll_position = (0, 0)
label_pos = "bottom"  # or 'right'
text_size = 16
icon_size = 128

# .. List view configuration ...................................................

list_icon_size = 16
list_text_size = 12
list_scroll_position = (0, 0)
list_sort_by = "name"
list_use_relative_dates = True
list_calculate_all_sizes = (False,)
list_columns = ("name", "date-modified", "size", "kind", "date-added")
list_column_widths = {
    "name": 300,
    "date-modified": 181,
    "date-created": 181,
    "date-added": 181,
    "date-last-opened": 181,
    "size": 97,
    "kind": 115,
    "label": 100,
    "version": 75,
    "comments": 300,
}
list_column_sort_directions = {
    "name": "ascending",
    "date-modified": "descending",
    "date-created": "descending",
    "date-added": "descending",
    "date-last-opened": "descending",
    "size": "descending",
    "kind": "ascending",
    "label": "ascending",
    "version": "ascending",
    "comments": "ascending",
}
