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
from .frame_classes import GrampsFrameIndicators

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

    def __init__(self, grstate, groptions, primary_obj, secondary_obj):
        GrampsFrame.__init__(
            self, grstate, groptions, primary_obj, secondary_obj
        )

        body = Gtk.HBox(hexpand=False, margin=3)
        if self.get_option("show-age") or self.groptions.age_base:
            self.age = Gtk.VBox(
                margin_right=3,
                margin_left=3,
                margin_top=3,
                margin_bottom=3,
                spacing=2,
            )
            if "age" in self.groptions.size_groups:
                self.groptions.size_groups["age"].add_widget(self.age)
            body.pack_start(self.age, expand=False, fill=False, padding=0)

        fact_block = Gtk.VBox(hexpand=False, vexpand=False)
        body.pack_start(fact_block, expand=True, fill=True, padding=0)
        self.title = Gtk.HBox()
        fact_block.pack_start(self.title, expand=True, fill=True, padding=0)
        fact_block.pack_start(
            self.facts_grid, expand=True, fill=True, padding=0
        )
        if "data" in self.groptions.size_groups:
            self.groptions.size_groups["data"].add_widget(fact_block)

        mode = self.grstate.config.get("options.global.privacy-mode")
        if mode or self.get_option("options.global.enable-child-indicators"):
            attribute_block = Gtk.VBox()
            if mode:
                image = Gtk.Image()
                if self.secondary.obj.private:
                    if mode in [1, 3]:
                        image.set_from_icon_name(
                            "gramps-lock", Gtk.IconSize.BUTTON
                        )
                else:
                    if mode in [2, 3]:
                        image.set_from_icon_name(
                            "gramps-unlock", Gtk.IconSize.BUTTON
                        )
                image_box = Gtk.HBox()
                image_box.pack_end(image, False, False, 0)
                attribute_block.pack_start(image_box, False, False, 0)

            if self.get_option("options.global.enable-child-indicators"):
                self.indicators = GrampsFrameIndicators(grstate, groptions)
                attribute_block.pack_end(
                    self.indicators, expand=False, fill=False, padding=0
                )
                if "active" in self.groptions.option_space:
                    size = 12
                else:
                    size = 2
                self.indicators.load(
                    self.secondary.obj, self.secondary.obj_type, size=size
                )
            if len(attribute_block):
                body.pack_end(
                    attribute_block, expand=False, fill=False, padding=0
                )
                if "attributes" in self.groptions.size_groups:
                    self.groptions.size_groups["attributes"].add_widget(
                        attribute_block
                    )

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

    def add_fact(self, fact, label=None):
        """
        Add a simple fact.
        """
        self.facts_grid.add_fact(fact, label=label)

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
