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
PageViewWindow
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
from gramps.gen.utils.db import navigation_label
from gramps.gui.managedwindow import ManagedWindow

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..views.view_builder import view_builder

_ = glocale.translation.sgettext


class PageViewWindow(ManagedWindow):
    """
    Window to display an object page view.
    """

    def __init__(self, grstate, grcontext, key, callback):
        """
        Initialize class.
        """
        self.key = key
        self.grstate = grstate
        self.grcontext = grcontext
        self.callback = callback
        if grcontext.primary_obj.obj_type != "Tag":
            self.base_title, dummy_obj = navigation_label(
                grstate.dbstate.db,
                grcontext.primary_obj.obj_type,
                grcontext.primary_obj.obj.get_handle(),
            )
        else:
            self.base_title = "".join(
                (_("Tag"), ": ", grcontext.primary_obj.obj.get_name())
            )
        ManagedWindow.__init__(
            self, grstate.uistate, [], grcontext.primary_obj.obj
        )

        self.page_view = Gtk.VBox()
        view = view_builder(grstate, grcontext)
        self.page_view.pack_start(view, True, True, 0)

        window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        window.set_transient_for(self.uistate.window)
        window.add(self.page_view)
        self.set_window(window, None, self.base_title)
        prefix = ".".join(
            (
                "interface.linked-view.page",
                grcontext.primary_obj.obj_type.lower(),
            )
        )
        self.setup_configs(prefix, 768, 768)
        self.show()

    def build_window_key(self, obj):
        """
        Return window key.
        """
        return self.key

    def build_menu_names(self, obj):
        """
        Build menu names.
        """
        title = self.base_title
        if "]" in title:
            title = title.split("] ")[1].strip()
        menu_label = "".join(
            (
                self.grcontext.primary_obj.obj_lang,
                ": ",
                title,
            )
        )
        return (menu_label, None)

    def rebuild(self):
        """
        Rebuild current page view.
        """
        view = view_builder(self.grstate, self.grcontext)
        list(map(self.page_view.remove, self.page_view.get_children()))
        self.page_view.pack_start(view, True, True, 0)
        self.show()

    def reload(self, grcontext):
        """
        Load new navigation context, replacing the current one, and rebuild.
        """
        self.grcontext = grcontext
        self.rebuild()

    def refresh(self):
        """
        Refresh navigation context and rebuild.
        """
        self.grcontext.refresh(self.grstate)
        return self.rebuild()

    def close(self, *_dummy_args, defer_delete=False):
        """
        Close the window.
        """
        ManagedWindow.close(self)
        if not defer_delete:
            self.callback(self.key)
