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
WindowService
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import uuid

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib.tableobj import TableObject
from gramps.gui.dialog import WarningDialog
from gramps.gen.utils.db import navigation_label
from gramps.gui.managedwindow import ManagedWindow

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from view.groups.group_window import CardGroupWindow
from view.views.view_builder import view_builder

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PinnedViewWindow Class
#
# ------------------------------------------------------------------------
class PinnedViewWindow(ManagedWindow):
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
                grcontext.primary_obj.obj.handle,
            )

        else:
            self.base_title = "%s: %s" % (
                _("Tag"),
                grcontext.primary_obj.obj.get_name(),
            )
        ManagedWindow.__init__(self, grstate.uistate, [], grcontext)

        self.page_view = Gtk.VBox()
        view = view_builder(grstate, grcontext)
        self.page_view.pack_start(view, True, True, 0)

        window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        window.set_transient_for(self.uistate.window)
        window.add(self.page_view)
        self.set_window(window, None, self.base_title)
        prefix = (
            "interface.cardview.page-%s-window"
            % grcontext.primary_obj.obj_type.lower()
        )
        self.setup_configs(prefix, 768, 768)
        self.show()

    def build_window_key(self, _dummy_obj):
        """
        Return window key.
        """
        return "%s-page" % self.key

    def build_menu_names(self, _dummy_obj):
        """
        Build menu names.
        """
        title = self.base_title
        if "]" in title:
            title = title.split("] ")[1].strip()
        menu_label = "%s: %s" % (self.grcontext.primary_obj.obj_lang, title)
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


# -------------------------------------------------------------------------
#
# WindowService Class
#
# -------------------------------------------------------------------------
class WindowService:
    """
    A singleton class for handling spawned group and view windows.
    """

    def __new__(cls):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(WindowService, cls).__new__(cls)
            cls.instance.__init_singleton__()
        return cls.instance

    def __init_singleton__(self):
        """
        Prepare the window service for use.
        """
        self.group_windows = {}
        self.page_windows = {}

    def launch_view_window(self, grstate, grcontext):
        """
        Launch a page view in a separate window.
        """
        max_windows = grstate.config.get("display.max-page-windows")
        key = grcontext.obj_key
        if reload_single_window(self.page_windows, max_windows, grcontext):
            return
        if launch_new_window(
            grstate, key, self.page_windows, max_windows, _("page")
        ):
            callback = lambda x: clear_window(x, self.page_windows)
            try:
                self.page_windows[key] = PinnedViewWindow(
                    grstate, grcontext, key, callback
                )
            except WindowActiveError:
                pass

    def launch_group_window(self, grstate, obj, group_type, title):
        """
        Launch a group view in a separate window.
        """
        max_windows = grstate.config.get("display.max-group-windows")
        if isinstance(obj, TableObject):
            key = "%s-%s" % (obj.handle, group_type)
        else:
            key = uuid.uuid4().hex
        if reload_single_window(
            self.page_windows, max_windows, obj, group_type
        ):
            return
        if launch_new_window(
            grstate, key, self.group_windows, max_windows, _("group")
        ):
            callback = lambda x: clear_window(x, self.group_windows)
            try:
                self.group_windows[key] = CardGroupWindow(
                    grstate,
                    obj,
                    group_type,
                    key,
                    callback,
                    title=title,
                )
            except WindowActiveError:
                pass

    def close_page_windows(self):
        """
        Close the page view windows.
        """
        close_windows(self.page_windows)

    def close_group_windows(self):
        """
        Close the group view windows.
        """
        close_windows(self.group_windows)

    def close_all_windows(self):
        """
        Close all the windows.
        """
        self.close_page_windows()
        self.close_group_windows()

    def refresh_page_windows(self):
        """
        Refresh the page view windows.
        """
        refresh_windows(self.page_windows)

    def refresh_group_windows(self):
        """
        Refresh the group view windows.
        """
        refresh_windows(self.group_windows)

    def refresh_all_windows(self):
        """
        Refresh all the windows.
        """
        self.refresh_page_windows()
        self.refresh_group_windows()


def reload_single_window(windows, max_windows, *args):
    """
    If only one spawned window enabled reload it.
    """
    if max_windows == 1 and windows:
        window = list(windows.values())[0]
        window.reload(*args)
        return True
    return False


def launch_new_window(grstate, key, windows, max_windows, window_type):
    """
    Validate if okay to launch a new window.
    """
    if len(windows) >= max_windows and key not in windows:
        WarningDialog(
            _("Could Not Spawn New Window"),
            _(
                "Too many %s view windows are open. Close one "
                "before launching another or increase the default "
                "in the preferences."
            )
            % window_type,
            parent=grstate.uistate.window,
        )
        return False
    return True


def clear_window(key, windows):
    """
    Clear a window.
    """
    if key in windows:
        del windows[key]


def close_windows(windows):
    """
    Close the windows.
    """
    for window in [y for x, y in windows.items()]:
        window.close()
    windows.clear()


def refresh_windows(windows):
    """
    Refresh the windows.
    """
    for window in [y for x, y in windows.items()]:
        window.refresh()
