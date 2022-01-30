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
FrameGroupWindow
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
from gramps.gen.utils.db import navigation_label
from gramps.gui.managedwindow import ManagedWindow

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from ..common.common_const import GROUP_LABELS
from ..common.common_utils import make_scrollable
from .group_builder import group_builder

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# FrameGroupWindow Class
#
# ------------------------------------------------------------------------
class FrameGroupWindow(ManagedWindow):
    """
    Window to display a frame group.
    """

    def __init__(self, grstate, obj, group_type, key, callback, title=None):
        """
        Initialize class.
        """
        self.key = key
        self.grstate = grstate
        self.callback = callback
        self.group_base = GrampsObject(obj)
        self.group_type = group_type
        working_title = self.build_title(title)
        if "Ref" in self.group_base.obj_type:
            self.base_title = "".join(
                (
                    working_title,
                    " ",
                    _("Reference"),
                    ": ",
                    GROUP_LABELS[self.group_type],
                )
            )
        else:
            self.base_title = "".join(
                (working_title, ": ", GROUP_LABELS[self.group_type])
            )
        prefix = ".".join(("interface.linked-view.group", self.group_type))
        ManagedWindow.__init__(self, grstate.uistate, [], obj)

        group_args = {"raw": True, "title": self.base_title}
        group = group_builder(grstate, group_type, obj, group_args)
        self.group_box = Gtk.VBox(spacing=3, margin=3)
        self.group_box.pack_start(group, expand=False, fill=True, padding=0)
        scroll = make_scrollable(self.group_box)

        window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        window.set_transient_for(self.uistate.window)
        window.add(scroll)
        self.set_window(window, None, self.base_title)
        self.setup_configs(prefix, 768, 768)
        self.show()

    def build_window_key(self, _dummy_obj):
        """
        Return window key.
        """
        return self.key

    def build_title(self, title):
        """
        Build title if one not provided.
        """
        if title:
            return title
        if self.group_base.has_handle:
            title, dummy_obj = navigation_label(
                self.grstate.dbstate.db,
                self.group_base.obj_type,
                self.group_base.obj.get_handle(),
            )
            return title
        return ""

    def build_menu_names(self, _dummy_obj):
        """
        Build menu names.
        """
        title = self.base_title
        if "]" in title:
            title = title.split("] ")[1].strip()
        menu_label = "".join(
            (
                self.group_base.obj_lang,
                ": ",
                title,
            )
        )
        return (menu_label, None)

    def rebuild(self):
        """
        Rebuild current group contents.
        """
        group_args = {"raw": True, "title": self.base_title}
        group = group_builder(
            self.grstate, self.group_type, self.group_base.obj, group_args
        )
        list(map(self.group_box.remove, self.group_box.get_children()))
        self.group_box.pack_start(group, expand=False, fill=True, padding=0)
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
        if not self.group_base.has_handle:
            return self.close()

        self.group_base.refresh(self.grstate)
        return self.rebuild()

    def close(self, *_dummy_args, defer_delete=False):
        """
        Close the window.
        """
        ManagedWindow.close(self)
        if not defer_delete:
            self.callback(self.key)
