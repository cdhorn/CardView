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
from gramps.gen.utils.db import navigation_label
from gramps.gui.managedwindow import ManagedWindow

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from ..common.common_const import GROUP_LABELS
from ..common.common_utils import make_scrollable
from .group_utils import build_group


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
        self.group_base = GrampsObject(obj)
        self.group_type = group_type

        group_args = {"raw": True}
        group = build_group(grstate, group_type, obj, group_args)
        self.group_box = Gtk.VBox(spacing=3, margin=3)
        self.group_box.pack_start(group, expand=False, fill=True, padding=0)
        scroll = make_scrollable(self.group_box)

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
        if hasattr(self.group_base.obj, "handle"):
            name, dummy_obj = navigation_label(
                self.grstate.dbstate.db,
                self.group_base.obj_type,
                self.group_base.obj.get_handle(),
            )
            return "".join((name, " - ", GROUP_LABELS[self.group_type]))
        return GROUP_LABELS[self.group_type]

    def rebuild(self):
        """
        Rebuild current group contents.
        """
        group_args = {"raw": True}
        group = build_group(
            self.grstate, self.group_type, self.group_base.obj, group_args
        )
        list(map(self.group_box.remove, self.group_box.get_children()))
        self.group_box.pack_start(group, expand=False, fill=True, padding=0)
        self.set_window(self.root, None, self.get_menu_title())
        self.show()

    def reload(self, obj, group_type=None):
        """
        Load new group, replacing the current one.
        """
        self.group_base = GrampsObject(obj)
        if group_type:
            self.group_type = group_type
        self.rebuild()

    def refresh(self):
        """
        Refresh current group, if not possible close window.
        """
        if not hasattr(self.group_base.obj, "handle"):
            return self.close()

        self.group_base.refresh(self.grstate)
        return self.rebuild()

    def close(self, *_dummy_args, defer_delete=False):
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
