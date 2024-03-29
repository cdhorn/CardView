#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021-2022  Christopher Horn
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
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_const import GROUP_LABELS_SINGLE
from ..config.config_builder import config_factory
from ..config.config_const import PAGE_NAMES
from ..config.config_layout import build_layout_grid
from ..config.config_panel import build_global_panel
from .menu_utils import add_double_separator, menu_item, new_menu, show_menu

_ = glocale.translation.sgettext

TOGGLE_OPTIONS = [
    (
        "general.link-people-to-relationships-view",
        _("Disable linking people to relationship category view"),
        _("Enable linking people to relationship category view"),
    ),
    (
        "media-bar.enabled",
        _("Disable media bar"),
        _("Enable media bar"),
    ),
    (
        "indicator.tags",
        _("Disable tags"),
        _("Enable tags"),
    ),
    (
        "indicator.child-objects",
        _("Disable child object indicators"),
        _("Enable child object indicators"),
    ),
    (
        "indicator.child-objects-counts",
        _("Disable display of child object indicator counts"),
        _("Enable display of child object indicator counts"),
    ),
    (
        "status.todo",
        _("Disable display of to do indicator"),
        _("Enable display of to do indicator"),
    ),
    (
        "status.confidence-ranking",
        _("Disable display of confidence ranking indicator"),
        _("Enable display of confidence ranking indicator"),
    ),
    (
        "status.citation-alert",
        _("Disable display of citation alert indicator"),
        _("Enable display of citation alert indicator"),
    ),
    (
        "status.missing-alert",
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
    Configure object type based on current card calling context.
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
    space = ".".join((tuple(groptions.option_space.split(".")[:1])))
    try:
        context = groptions.option_space.split(".")[1]
    except IndexError:
        return space, "unknown", "unknown", "unknown"
    obj_type = GROUP_LABELS_SINGLE.get(context) or "Unknown"
    if context in ["parent", "spouse"] and primary_type == "Family":
        context = "family"
        obj_type = _("Family")
    if "active" in space:
        space_label = "%s %s" % (_("Active"), obj_type)
    elif "group" in space:
        space_label = "%s %s" % (obj_type, _("Group"))
    elif "timeline" in space:
        if "person" in groptions.option_space:
            context = "person"
            space_label = "%s %s" % (_("Person"), _("Timeline"))
        elif "family" in groptions.option_space:
            context = "family"
            space_label = "%s %s" % (_("Family"), _("Timeline"))
        elif "place" in groptions.option_space:
            context = "place"
            space_label = "%s %s" % (_("Place"), _("Timeline"))
    menu_title = "%s %s" % (_("Configure"), space_label.lower())
    window_title = "%s %s %s" % (_("Configuration"), _("for"), space_label)
    return space, context, menu_title, window_title


def add_page_layout_option(menu, grstate):
    """
    Build page layout menu option.
    """
    grcontext = grstate.fetch_page_context()
    menu_title = "%s %s %s %s" % (
        _("Configure"),
        PAGE_NAMES[grcontext.page_type],
        _("Page"),
        _("Layout"),
    )
    window_title = "%s %s %s %s" % (
        _("Configuration"),
        _("for"),
        PAGE_NAMES[grcontext.page_type],
        _("Page"),
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
    menu = new_menu(
        "preferences-system", _("Global options"), run_global_config, grstate
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
    add_double_separator(menu)
    menu.append(toggle_option(
        global_config,
        (
            "interface.cardview.enable-statistics-dashboard",
            _("Disable statistics dashboard (requires restart)"),
            _("Enable statistics dashboard (requires restart)"),
        )
    ))
    add_double_separator(menu)
    label = Gtk.MenuItem(label=_("Configuration"))
    label.set_sensitive(False)
    menu.append(label)
    return show_menu(menu, widget, event)


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
