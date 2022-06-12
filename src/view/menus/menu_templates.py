#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022       Christopher Horn
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
Templates menu
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
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .menu_utils import add_double_separator, menu_item, show_menu
from ..services.service_templates import TemplatesService

_ = glocale.translation.sgettext


def build_templates_menu(widget, grstate, event):
    """
    Build the templates menu.
    """
    menu = Gtk.Menu()
    templates_service = TemplatesService(grstate.dbstate)
    user_templates = templates_service.get_templates()
    for template in user_templates:
        menu.append(
            menu_item(
                "preferences-system",
                template["lang_string"],
                switch_active_template,
                grstate,
                template["xml_string"],
            )
        )
    add_double_separator(menu)
    label = Gtk.MenuItem(label=_("Templates"))
    label.set_sensitive(False)
    menu.append(label)
    return show_menu(menu, widget, event)


def switch_active_template(_dummy_obj, grstate, new_template):
    """
    Change the active template.
    """
    grstate.templates.set("templates.active", new_template)
    grstate.templates.save()
    grstate.reload_config(refresh_only=False, defer_refresh=False)
