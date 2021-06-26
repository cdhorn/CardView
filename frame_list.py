#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
GrampsFrameList.
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
from gi.repository import Gtk, Gdk, GdkPixbuf


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gui.ddtargets import DdTargets


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsConfig, GrampsFrame
from frame_utils import get_gramps_object_type


# ------------------------------------------------------------------------
#
# GrampsFrameList class
#
# ------------------------------------------------------------------------
class GrampsFrameList(Gtk.ListBox, GrampsConfig):
    """
    The GrampsFrameList class provides the core methods for managing a
    list of GrampsFrame objects. It primarily supports drag and drop 
    actions related to the list.
    """

    def __init__(self, dbstate, uistate, space, config):
        Gtk.ListBox.__init__(self)
        GrampsConfig.__init__(self, dbstate, uistate, space, config)
        self.obj_type = None
        self.dnd_type = None
        self.dnd_icon = None
        self.row_frames = []
        self.row_previous = 0
        self.row_current = 0
        self.row_previous_provider = None
        self.row_current_provider = None
        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("drag-motion", self.on_drag_motion)
        self.connect("drag-leave", self.on_drag_leave)

    def add_frame(self, gramps_frame):
        """
        Add a GrampsFrame object.
        """
        if not isinstance(gramps_frame, GrampsFrame):
            return None
        if self.obj_type is None and self.dnd_type is None:
            self.obj_type = gramps_frame.obj_type
            self.dnd_type = gramps_frame.dnd_type
            self.drag_dest_set(
                Gtk.DestDefaults.MOTION|Gtk.DestDefaults.DROP,
                [self.dnd_type.target()],
                Gdk.DragAction.COPY
            )
        self.row_frames.append(gramps_frame)
        row = Gtk.ListBoxRow(selectable=False)
        row.add(self.row_frames[-1])
        self.add(row)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        """
        Extract the data and handle any required actions.
        """
        self.reset_dnd_css()
        if data and data.get_data():
            dnd_type, obj_id, obj_handle, skip = pickle.loads(data.get_data())
            index = 0
            for frame in self.row_frames:
                if frame.obj.get_handle() == obj_handle:
                    if self.row_current != index:
                        row_moving = self.get_row_at_index(index)
                        frame_moving = self.row_frames[index]
                        self.remove(row_moving)
                        self.row_frames.remove(frame_moving)
                        self.insert(row_moving, self.row_current)
                        self.row_frames.insert(self.row_current, frame_moving)
                        self.save_reordered_list()
                    break
                index = index + 1
            if index >= len(self.row_frames):
                self.save_new_object(obj_handle)
        self.row_previous = 0
        self.row_current = 0

    def save_reordered_list(self):
        """
        Stub for derived objects to save the reordered list.
        """
        
    def save_new_object(self, handle):
        """
        Stub for derived objects to add an external object to the list.
        """
        
    def on_drag_motion(self, widget, context, x, y, time):
        """
        Update the view while a user drag and drop is underway.
        """
        self.reset_dnd_css()
        current_row = self.get_row_at_y(y)
        allocation = current_row.get_allocation()
        if (y < allocation.y + allocation.height/2):
            self.row_current = current_row.get_index()
            self.row_previous = self.row_current - 1
            if self.row_previous < 0:
                self.row_previous = 0
        else:
            self.row_previous = current_row.get_index()
            self.row_current = self.row_previous + 1
            if self.row_current >= len(self) - 1:
                self.row_current = len(self) - 1

        if self.row_current == 0 and self.row_previous == 0:
            self.row_current_provider = self.set_dnd_css(self.row_frames[self.row_current], top=True)
        elif self.row_current == self.row_previous:
            self.row_current_provider = self.set_dnd_css(self.row_frames[self.row_current], top=False)
        elif self.row_current > self.row_previous:
            self.row_previous_provider = self.set_dnd_css(self.row_frames[self.row_previous], top=False)
            self.row_current_provider = self.set_dnd_css(self.row_frames[self.row_current], top=True)
        else:
            self.row_previous_provider = self.set_dnd_css(self.row_frames[self.row_previous], top=True)
            self.row_current_provider = self.set_dnd_css(self.row_frames[self.row_current], top=False)

    def on_drag_leave(self, *obj):
        """
        Reset custom CSS if drag no longer in focus.
        """
        self.reset_dnd_css()

    def reset_dnd_css(self):
        """
        Reset custom CSS for the drag and drop view.
        """
        if self.row_previous_provider:
            context = self.row_frames[self.row_previous].get_style_context()
            context.remove_provider(self.row_previous_provider)
            self.row_previous_provider = None
        self.row_frames[self.row_previous].set_css_style()
        if self.row_current_provider:
            context = self.row_frames[self.row_current].get_style_context()
            context.remove_provider(self.row_current_provider)
            self.row_current_provider = None
        self.row_frames[self.row_current].set_css_style()
        
    def set_dnd_css(self, row, top):
        """
        Set custom CSS for the drag and drop view.
        """
        if top:
            css = ".frame { border-top-width: 3px; border-top-color: #4e9a06; }".encode("utf-8")
        else:
            css = ".frame { border-bottom-width: 3px; border-bottom-color: #4e9a06; }".encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = row.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")
        return provider
