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
Group widgets
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
from gramps.gen.config import config
from gramps.gen.utils.db import navigation_label
from gramps.gui.managedwindow import ManagedWindow

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_const import GROUP_LABELS
from ..common.common_utils import get_gramps_object_type
from .group_const import OBJECT_GROUPS


class FrameGroupWindow(ManagedWindow):
    """
    Window to display a frame group.
    """

    def __init__(self, grstate, obj, group_type, key, callback):
        """
        Initialize class.
        """
        self.key = key
        ManagedWindow.__init__(self, grstate.uistate, [], obj)
        self.grstate = grstate
        self.callback = callback
        self.obj = obj
        self.obj_type = get_gramps_object_type(obj)
        self.group_type = group_type

        group = OBJECT_GROUPS[group_type](grstate, obj, raw=True)
        self.group_box = Gtk.VBox(spacing=3, margin=3)
        self.group_box.pack_start(group, expand=False, fill=True, padding=0)

        scroll = Gtk.ScrolledWindow(hexpand=False, vexpand=True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        viewport = Gtk.Viewport()
        viewport.add(self.group_box)
        scroll.add(viewport)

        self.root = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.root.set_transient_for(self.uistate.window)
        self.root.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.root.add(scroll)
        self.set_window(self.root, None, self.get_menu_title())
        self.show()

        width = grstate.config.get("interface.width")
        height = grstate.config.get("interface.height")
        self.window.resize(width, height)

    def build_window_key(self, obj):
        """
        Return window key.
        """
        return self.key

    def get_menu_title(self):
        """
        Get the menu title.
        """
        if hasattr(self.obj, "handle"):
            name, dummy_obj = navigation_label(
                self.grstate.dbstate.db,
                self.obj_type,
                self.obj.get_handle(),
            )
            return "{} - {}".format(name, GROUP_LABELS[self.group_type])
        return GROUP_LABELS[self.group_type]

    def reload(self, obj, group_type):
        """
        Load new group, replacing the current one.
        """
        self.obj = obj
        self.obj_type = get_gramps_object_type(obj)
        self.group_type = group_type
        group = OBJECT_GROUPS[group_type](self.grstate, obj, raw=True)
        list(map(self.group_box.remove, self.group_box.get_children()))
        self.group_box.pack_start(group, expand=False, fill=True, padding=0)
        self.set_window(self.root, None, self.get_menu_title())
        self.show()

    def refresh(self):
        """
        Refresh current group, if not possible close window.
        """
        print("refresh window")
        if not hasattr(self.obj, "handle"):
            return self.close()

        self.obj = self.grstate.fetch(self.obj_type, self.obj.get_handle())
        if not self.obj:
            return self.close()

        group = OBJECT_GROUPS[self.group_type](
            self.grstate, self.obj, raw=True
        )
        list(map(self.group_box.remove, self.group_box.get_children()))
        self.group_box.pack_start(group, expand=False, fill=True, padding=0)
        self.show()

    def close(self, *args, defer_delete=False):
        """
        Close the window.
        """
        (width, height) = self.window.get_size()
        self.grstate.config.set("interface.width", width)
        self.grstate.config.set("interface.height", height)
        self.grstate.config.save()
        ManagedWindow.close(self)
        if not defer_delete:
            self.callback(self.key)
