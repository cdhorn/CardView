#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021       Christopher Horn
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Configuration menu and helpers
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_const import GROUP_LABELS_SINGLE
from ..common.common_utils import menu_item
from ..config.config_builder import config_factory
from ..config.config_const import PAGE_NAMES
from ..config.config_layout import build_layout_grid
from ..config.config_panel import build_global_panel

_ = glocale.translation.sgettext

TOGGLE_OPTIONS = [
    (
        "options.global.media-bar.enabled",
        _("Disable media bar"),
        _("Enable media bar"),
    ),
    (
        "options.global.indicator.tags",
        _("Disable tags"),
        _("Enable tags"),
    ),
    (
        "options.global.indicator.child-objects",
        _("Disable child object indicators"),
        _("Enable child object indicators"),
    ),
    (
        "options.global.indicator.child-objects-counts",
        _("Disable display of child object indicator counts"),
        _("Enable display of child object indicator counts"),
    ),
    (
        "options.global.status.todo",
        _("Disable display of to do indicator"),
        _("Enable display of to do indicator"),
    ),
    (
        "options.global.status.confidence-ranking",
        _("Disable display of confidence ranking indicator"),
        _("Enable display of confidence ranking indicator"),
    ),
    (
        "options.global.status.citation-alert",
        _("Disable display of citation alert indicator"),
        _("Enable display of citation alert indicator"),
    ),
    (
        "options.global.status.missing-alert",
        _("Disable display of missing events indicator"),
        _("Enable display of missing events indicator"),
    ),
]


def run_global_config(_dummy_obj, grstate):
    """
    Global config page.
    """
    grstate.launch_config(_("Global"), build_global_panel, None, None)


def run_object_config(_dummy_obj, grstate, groptions, primary_type):
    """
    Configure object type based on current frame calling context.
    """
    space, context, dummy_menu_title, window_title = get_object_config_title(
        groptions, primary_type
    )
    builder = config_factory(space, context)
    grstate.launch_config(window_title, builder, space, context)


def get_object_config_title(groptions, primary_type):
    """
    Build object config description.
    """
    space = ".".join((tuple(groptions.option_space.split(".")[:2])))
    try:
        context = groptions.option_space.split(".")[2]
    except IndexError:
        return space, "unknown", "unknown", "unknown"
    if context in GROUP_LABELS_SINGLE:
        obj_type = GROUP_LABELS_SINGLE[context]
    else:
        obj_type = "Unknown"
    if context in ["parent", "spouse"] and primary_type == "Family":
        context = "family"
        obj_type = _("Family")
    if "active" in space:
        space_label = " ".join((_("Active"), obj_type))
    elif "group" in space:
        space_label = " ".join((obj_type, _("Group")))
    elif "timeline" in space:
        if "person" in groptions.option_space:
            context = "person"
            space_label = " ".join((_("Person"), _("Timeline")))
        elif "family" in groptions.option_space:
            context = "family"
            space_label = " ".join((_("Family"), _("Timeline")))
        elif "place" in groptions.option_space:
            context = "place"
            space_label = " ".join((_("Place"), _("Timeline")))
    menu_title = " ".join((_("Configure"), space_label.lower()))
    window_title = " ".join((_("Configuration"), _("for"), space_label))
    return space, context, menu_title, window_title


def add_page_layout_option(menu, grstate):
    """
    Build page layout menu option.
    """
    grcontext = grstate.fetch_page_context()
    menu_title = " ".join(
        (
            _("Configure"),
            PAGE_NAMES[grcontext.page_type],
            _("Page"),
            _("Layout"),
        )
    )
    window_title = " ".join(
        (
            _("Configuration"),
            _("for"),
            PAGE_NAMES[grcontext.page_type],
            _("Page"),
        )
    )
    menu.append(
        menu_item(
            "preferences-system",
            menu_title.lower().capitalize(),
            run_layout_config,
            grstate,
            (grcontext.page_type, window_title),
        )
    )


def run_layout_config(_dummy_obj, grstate, page_tuple):
    """
    Configure current page layout.
    """
    (page_type, window_title) = page_tuple
    grstate.launch_config(window_title, build_layout_grid, page_type, None)


def build_config_menu(widget, grstate, groptions, primary_type, event):
    """
    Build the configuration option menu.
    """
    config = grstate.config
    menu = Gtk.Menu()
    menu.append(
        menu_item(
            "preferences-system",
            _("Global options"),
            run_global_config,
            grstate,
        )
    )
    (
        dummy_space,
        context,
        menu_title,
        dummy_window_title,
    ) = get_object_config_title(groptions, primary_type)
    if context not in ["attribute", "url"] and "unknown" not in menu_title:
        menu.append(
            menu_item(
                "preferences-system",
                menu_title,
                run_object_config,
                grstate,
                groptions,
                primary_type,
            )
        )
    add_page_layout_option(menu, grstate)
    for option_data in TOGGLE_OPTIONS:
        menu.append(toggle_option(config, option_data))
    menu.attach_to_widget(widget, None)
    menu.show_all()
    if Gtk.get_minor_version() >= 22:
        menu.popup_at_pointer(event)
    else:
        menu.popup(None, None, None, None, event.button, event.time)
    return True


def toggle_option(config, option_data):
    """
    Prepare a toggle option.
    """
    (option, disable_text, enable_text) = option_data
    if config.get(option):
        return menu_item(
            "list-remove",
            disable_text,
            toggle,
            config,
            option,
        )
    return menu_item(
        "list-add",
        enable_text,
        toggle,
        config,
        option,
    )


def toggle(_dummy_arg, config, option):
    """
    Toggle an option setting.
    """
    value = config.get(option)
    config.set(option, not value)
    config.save()
