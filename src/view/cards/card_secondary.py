#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
SecondaryCard
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
import pickle

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
from gramps.gen.utils.alive import probably_alive

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from ..common.common_utils import get_person_color_css
from ..menus.menu_utils import (
    add_citations_menu,
    add_delete_menu_option,
    add_double_separator,
    add_edit_menu_option,
    add_notes_menu,
    add_privacy_menu_option,
    show_menu,
)
from .card_object import ObjectCard
from .card_utils import load_metadata

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# SecondaryCard Class
#
# ------------------------------------------------------------------------
class SecondaryCard(ObjectCard):
    """
    The SecondaryCard class provides core methods for constructing the
    view and working with the secondary Gramps object it exposes.
    """

    def __init__(self, grstate, groptions, primary_obj, secondary_obj):
        groptions.is_secondary = True
        ObjectCard.__init__(
            self,
            grstate,
            groptions,
            primary_obj,
        )
        self.secondary = GrampsObject(secondary_obj)
        self.focus = self.secondary
        self.build_layout()
        self.frame.set_size_request(160, -1)
        load_metadata(
            self.widgets["id"], self.grstate, self.groptions, self.secondary
        )
        self.widgets["icons"].load(self.secondary, title=self.get_title())

    def drag_data_get(
        self, _dummy_widget, _dummy_context, data, info, _dummy_time
    ):
        """
        Return requested data.
        """
        if info == self.secondary.dnd_type.app_id:
            returned_data = (
                self.secondary.dnd_type.drag_type,
                id(self),
                self.secondary.obj,
                0,
            )
            data.set(
                self.secondary.dnd_type.atom_drag_type,
                8,
                pickle.dumps(returned_data),
            )

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        return self._base_drop_handler(dnd_type, obj_or_handle, data)

    def add_fact(self, fact, label=None):
        """
        Add a simple fact.
        """
        self.widgets["facts"].add_fact(fact, label=label)

    def build_context_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click. First action will always be
        edit, then any custom actions of the derived children, then the global
        actions supported for all objects enabled for them.
        """
        context_menu = Gtk.Menu()
        add_edit_menu_option(
            self.grstate, context_menu, self.primary, self.secondary
        )
        if self.grstate.config.get(
            "menu.delete"
        ) and not self.grstate.config.get("menu.delete-bottom"):
            add_delete_menu_option(
                self.grstate, context_menu, self.primary, self.secondary
            )
        self.add_custom_actions(context_menu)
        add_citations_menu(
            self.grstate,
            context_menu,
            self.primary,
            self.secondary,
        )
        add_notes_menu(
            self.grstate, context_menu, self.primary, self.secondary
        )
        add_privacy_menu_option(
            self.grstate, context_menu, self.primary, self.secondary
        )
        if self.grstate.config.get("menu.delete") and self.grstate.config.get(
            "menu.delete-bottom"
        ):
            add_double_separator(context_menu)
            add_delete_menu_option(
                self.grstate, context_menu, self.primary, self.secondary
            )
        return show_menu(context_menu, self, event)

    def add_custom_actions(self, context_menu):
        """
        For derived objects to inject their own actions into the menu.
        """

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if (
            self.grstate.config.get("display.use-color-scheme")
            and self.primary.obj_type == "Person"
        ):
            living = probably_alive(self.primary.obj, self.grstate.dbstate.db)
            return get_person_color_css(
                self.primary.obj,
                living=living,
            )
        return ""
