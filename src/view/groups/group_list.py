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
CardGroupList
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
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsConfig, GrampsObject
from ..common.common_utils import set_dnd_css
from ..cards.card_object import ObjectCard


# ------------------------------------------------------------------------
#
# CardGroupList Class
#
# ------------------------------------------------------------------------
class CardGroupList(Gtk.ListBox, GrampsConfig):
    """
    The CardGroupList class provides the core methods for managing
    a list of Card objects. It primarily supports drag and drop
    actions related to the list.
    """

    def __init__(self, grstate, groptions, obj, enable_drop=True):
        Gtk.ListBox.__init__(self)
        GrampsConfig.__init__(self, grstate, groptions)
        self.group_base = GrampsObject(obj)
        self.managed_obj_type = None
        self.row_cards = []
        self.row_previous = 0
        self.row_current = 0
        self.row_previous_provider = None
        self.row_current_provider = None
        if enable_drop:
            self.connect("drag-data-received", self.on_drag_data_received)
            self.connect("drag-motion", self.on_drag_motion)
            self.connect("drag-leave", self.on_drag_leave)

    def add_card(self, gramps_card):
        """
        Add a Card object.
        """
        if isinstance(gramps_card, ObjectCard):
            if not self.managed_obj_type:
                self.managed_obj_type = gramps_card.focus.obj_type
                if gramps_card.focus.dnd_type:
                    self.drag_dest_set(
                        Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP,
                        [gramps_card.focus.dnd_type.target()],
                        Gdk.DragAction.COPY | Gdk.DragAction.MOVE,
                    )
        self.row_cards.append(gramps_card)
        row = Gtk.ListBoxRow(selectable=False)
        row.add(self.row_cards[-1])
        self.add(row)

    def on_drag_data_received(
        self,
        _dummy_widget,
        _dummy_drag_context,
        _dummy_x,
        _dummy_y,
        data,
        _dummy_info,
        _dummy_time,
    ):
        """
        Extract the data and handle any required actions.
        """
        self.reset_dnd_css()
        if data and data.get_data():
            (
                dummy_dnd_type,
                dummy_obj_id,
                obj_handle,
                dummy_var1,
            ) = pickle.loads(data.get_data())
            self.insert_dropped_object(obj_handle)
        self.row_previous = 0
        self.row_current = 0

    def insert_dropped_object(self, obj_handle):
        """
        Insert dropped object.
        """
        source_index = 0
        for card in self.row_cards:
            if card.primary.obj.handle == obj_handle:
                if self.row_current == source_index:
                    break
                row_moving = self.get_row_at_index(source_index)
                card_moving = self.row_cards[source_index]
                self.remove(row_moving)
                self.row_cards.remove(card_moving)
                if self.row_current < source_index:
                    self.insert(row_moving, self.row_current)
                    self.row_cards.insert(self.row_current, card_moving)
                elif self.row_current == self.row_previous:
                    self.add(row_moving)
                    self.row_cards.append(card_moving)
                elif self.row_current > source_index:
                    self.insert(row_moving, self.row_current - 1)
                    self.row_cards.insert(self.row_current - 1, card_moving)
                self.save_reordered_list()
                break
            source_index = source_index + 1
        if source_index >= len(self.row_cards):
            self.save_new_object(obj_handle, self.row_current)

    def save_reordered_list(self):
        """
        Stub for derived objects to save the reordered list.
        """

    def save_new_object(self, handle, insert_row):
        """
        Stub for derived objects to add an external object to the list.
        """

    def on_drag_motion(
        self, _dummy_widget, _dummy_context, _dummy_x, y_location, _dummy_time
    ):
        """
        Update the view while a user drag and drop is underway.
        """
        self.reset_dnd_css()
        current_row = self.get_row_at_y(y_location)
        if current_row:
            allocation = current_row.get_allocation()
            if allocation:
                self.update_rows_for_drag_motion(
                    y_location, current_row, allocation
                )

    def update_rows_for_drag_motion(self, y_location, current_row, allocation):
        """ """
        if y_location < allocation.y + allocation.height / 2:
            self.row_current = current_row.get_index()
            self.row_previous = self.row_current - 1
            self.row_previous = max(self.row_previous, 0)
        else:
            self.row_previous = current_row.get_index()
            self.row_current = self.row_previous + 1
            if self.row_current >= len(self) - 1:
                self.row_current = len(self) - 1

        if self.row_current == 0 and self.row_previous == 0:
            self.row_current_provider = set_dnd_css(
                self.row_cards[self.row_current], top=True
            )
        elif self.row_current == self.row_previous:
            self.row_current_provider = set_dnd_css(
                self.row_cards[self.row_current], top=False
            )
        elif self.row_current > self.row_previous:
            self.row_previous_provider = set_dnd_css(
                self.row_cards[self.row_previous], top=False
            )
            self.row_current_provider = set_dnd_css(
                self.row_cards[self.row_current], top=True
            )
        else:
            self.row_previous_provider = set_dnd_css(
                self.row_cards[self.row_previous], top=True
            )
            self.row_current_provider = set_dnd_css(
                self.row_cards[self.row_current], top=False
            )

    def on_drag_leave(self, *_dummy_obj):
        """
        Reset custom CSS if drag no longer in focus.
        """
        self.reset_dnd_css()

    def reset_dnd_css(self):
        """
        Reset custom CSS for the drag and drop view.
        """
        if self.row_previous_provider:
            context = self.row_cards[self.row_previous].get_style_context()
            context.remove_provider(self.row_previous_provider)
            self.row_previous_provider = None
        self.row_cards[self.row_previous].set_css_style()
        if self.row_current_provider:
            context = self.row_cards[self.row_current].get_style_context()
            context.remove_provider(self.row_current_provider)
            self.row_current_provider = None
        self.row_cards[self.row_current].set_css_style()
