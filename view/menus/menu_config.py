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
from ..common.common_utils import (
    menu_item,
    submenu_item,
)

_ = glocale.translation.sgettext


def build_config_menu(grstate, groptions, event):
    """
    Build the configuration option menu.
    """
    config = grstate.config
    menu = Gtk.Menu()
    menu.append(tags_option(config))
    menu.append(indicators_option(config))

    menu.show_all()
    if Gtk.get_minor_version() >= 22:
        menu.popup_at_pointer(event)
    else:
        menu.popup(None, None, None, None, event.button, event.time)


def tags_option(config):
    """
    Prepare tags option.
    """
    if config.get("options.global.icons-enable-tags"):
        return menu_item(
            "list-remove",
            _("Disable tag icons"),
            toggle,
            config,
            "options.global.icons-enable-tags",
        )
    return menu_item(
        "list-add",
        _("Enable tag icons"),
        toggle,
        config,
        "options.global.icons-enable-tags",
    )


def indicators_option(config):
    """
    Prepare indicators option.
    """
    if config.get("options.global.icons-enable-indicators"):
        return menu_item(
            "list-remove",
            _("Disable child object indicators icons"),
            toggle,
            config,
            "options.global.icons-enable-indicators",
        )
    return menu_item(
        "list-add",
        _("Enable child object indicator icons"),
        toggle,
        config,
        "options.global.icons-enable-indicators",
    )


def toggle(_dummy_arg, config, option):
    """
    Toggle an option setting.
    """
    value = config.get(option)
    config.set(option, not value)
    config.save()
