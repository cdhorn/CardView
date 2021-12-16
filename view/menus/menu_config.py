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
from ..common.common_utils import (
    menu_item,
    submenu_item,
)
from ..config.config_builder import config_factory
from ..config.config_const import PAGE_NAMES, PAGES
from ..config.config_panel import build_global_panel
from ..config.config_layout import build_layout_grid

_ = glocale.translation.sgettext


def run_global_config(_dummy_obj, grstate):
    """
    Global config page.
    """
    grstate.launch_config(_("Global"), build_global_panel, None, None)


def run_object_config(_dummy_obj, grstate, groptions):
    """
    Configure object type based on current frame calling context.
    """
    space, context, dummy_menu_title, window_title = get_object_config_title(
        groptions
    )
    builder = config_factory(space, context)
    grstate.launch_config(window_title, builder, space, context)


def get_object_config_title(groptions):
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


def build_config_menu(widget, grstate, groptions, event):
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
    ) = get_object_config_title(groptions)
    if context not in ["attribute", "url"] and "unknown" not in menu_title:
        menu.append(
            menu_item(
                "preferences-system",
                menu_title,
                run_object_config,
                grstate,
                groptions,
            )
        )
    add_page_layout_option(menu, grstate)
    menu.append(media_bar_option(config))
    menu.append(tags_option(config))
    menu.append(indicators_option(config))
    menu.append(indicator_counts_option(config))
    menu.attach_to_widget(widget, None)
    menu.show_all()
    if Gtk.get_minor_version() >= 22:
        menu.popup_at_pointer(event)
    else:
        menu.popup(None, None, None, None, event.button, event.time)
    return True


def media_bar_option(config):
    """
    Prepare media bar option.
    """
    if config.get("options.global.media-bar.enabled"):
        return menu_item(
            "list-remove",
            _("Disable media bar"),
            toggle,
            config,
            "options.global.media-bar.enabled",
        )
    return menu_item(
        "list-add",
        _("Enable media bar"),
        toggle,
        config,
        "options.global.media-bar.enabled",
    )


def tags_option(config):
    """
    Prepare tags option.
    """
    if config.get("options.global.indicator.tags"):
        return menu_item(
            "list-remove",
            _("Disable tag icons"),
            toggle,
            config,
            "options.global.indicator.tags",
        )
    return menu_item(
        "list-add",
        _("Enable tag icons"),
        toggle,
        config,
        "options.global.indicator.tags",
    )


def indicators_option(config):
    """
    Prepare indicators option.
    """
    if config.get("options.global.indicator.child-objects"):
        return menu_item(
            "list-remove",
            _("Disable child object indicators icons"),
            toggle,
            config,
            "options.global.indicator.child-objects",
        )
    return menu_item(
        "list-add",
        _("Enable child object indicator icons"),
        toggle,
        config,
        "options.global.indicator.child-objects",
    )


def indicator_counts_option(config):
    """
    Prepare indicators option.
    """
    if config.get("options.global.indicator.child-objects-counts"):
        return menu_item(
            "list-remove",
            _("Disable display of child object counts with indicator icons"),
            toggle,
            config,
            "options.global.indicator.child-objects-counts",
        )
    return menu_item(
        "list-add",
        _("Enable display of child object counts with indicator icons"),
        toggle,
        config,
        "options.global.indicator.child-objects-counts",
    )


def toggle(_dummy_arg, config, option):
    """
    Toggle an option setting.
    """
    value = config.get(option)
    config.set(option, not value)
    config.save()
