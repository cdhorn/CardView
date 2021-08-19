#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
SecondaryGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import pickle


# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk, Gdk


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
from .frame_base import GrampsFrame
from .frame_utils import menu_item, submenu_item

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# SecondaryGrampsFrame class
#
# ------------------------------------------------------------------------
class SecondaryGrampsFrame(GrampsFrame):
    """
    The SecondaryGrampsFrame class provides core methods for constructing the
    view and working with the secondary Gramps object it exposes.
    """

    def __init__(
        self, grstate, groptions, primary_obj, secondary_obj
    ):
        GrampsFrame.__init__(self, grstate, groptions, primary_obj, secondary_obj)

        vcontent = Gtk.VBox()
        self.title = Gtk.HBox()
        vcontent.pack_start(self.title, expand=True, fill=True, padding=0)
        vcontent.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
        body = Gtk.HBox(hexpand=True, margin=3)
        body.pack_start(vcontent, expand=True, fill=True, padding=0)
        if self.secondary.obj.private:
            vlock = Gtk.VBox()
            image = Gtk.Image()
            image.set_from_icon_name("gramps-lock", Gtk.IconSize.BUTTON)
            vlock.pack_start(image, False, False, 0)
            body.pack_start(vlock, False, False, 0)
        if "data" in self.groptions.size_groups:
            self.groptions.size_groups["data"].add_widget(body)
        self.frame.set_size_request(160, -1)
        self.frame.add(body)
        self.eventbox.add(self.frame)
        self.add(self.eventbox)

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

    def add_fact(self, fact, label=None, row=None, column=0, stop=1):
        """
        Add a simple fact.
        """
        row_number = row or self.facts_row
        if label:
            self.facts_grid.attach(label, column, row_number, stop, 1)
            self.facts_grid.attach(fact, column + 1, row_number, stop, 1)
        else:
            self.facts_grid.attach(fact, column, row_number, stop + 1, 1)
        if row is None:
            self.facts_row = self.facts_row + 1

    def build_action_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click. First action will always be
        edit, then any custom actions of the derived children, then the global
        actions supported for all objects enabled for them.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.action_menu = Gtk.Menu()
            self.action_menu.append(self._edit_object_option())
            self.add_custom_actions()
            if hasattr(self.secondary.obj, "citation_list"):
                self.action_menu.append(
                    self._citations_option(
                        self.secondary.obj,
                        self.add_new_citation,
                        self.add_existing_citation,
                        self.remove_citation,
                    )
                )
            if hasattr(self.secondary.obj, "note_list"):
                self.action_menu.append(
                    self._notes_option(
                        self.secondary.obj,
                        self.add_new_note,
                        self.add_existing_note,
                        self.remove_note,
                    )
                )
            self.action_menu.append(self._change_privacy_option())
            self.action_menu.show_all()
            if Gtk.get_minor_version() >= 22:
                self.action_menu.popup_at_pointer(event)
            else:
                self.action_menu.popup(
                    None, None, None, None, event.button, event.time
                )

    def add_custom_actions(self):
        """
        For derived objects to inject their own actions into the menu.
        """
