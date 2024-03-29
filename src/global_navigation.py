#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Nick Hall
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
GlobalNavigation class
"""

# ----------------------------------------------------------------
#
# Python Modules
#
# ----------------------------------------------------------------
import html
import logging
from abc import abstractmethod
from functools import partial

# ----------------------------------------------------------------
#
# GTK Modules
#
# ----------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ----------------------------------------------------------------
#
# Gramps Modules
#
# ----------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.constfunc import mod_key
from gramps.gen.db.dummydb import DummyDb
from gramps.gen.utils.db import navigation_label
from gramps.gui.dialog import WarningDialog
from gramps.gui.uimanager import ActionGroup
from gramps.gui.utils import match_primary_mask
from gramps.gui.views.bookmarks import (
    PersonBookmarks,
    FamilyBookmarks,
    EventBookmarks,
    PlaceBookmarks,
    CitationBookmarks,
    SourceBookmarks,
    RepoBookmarks,
    MediaBookmarks,
    NoteBookmarks,
)
from gramps.gui.views.pageview import PageView

# ----------------------------------------------------------------
#
# Plugin Modules
#
# ----------------------------------------------------------------
from global_history import GlobalHistory
from view.config.config_const import CATEGORIES

_ = glocale.translation.sgettext

_LOG = logging.getLogger(".navigationview")

DISABLED = -1
MRU_SIZE = 10

MRU_TOP = '<section id="CommonHistory">'
MRU_BTM = "</section>"

BOOKMARKS = {
    "Person": PersonBookmarks,
    "Family": FamilyBookmarks,
    "Event": EventBookmarks,
    "Place": PlaceBookmarks,
    "Media": MediaBookmarks,
    "Note": NoteBookmarks,
    "Citation": CitationBookmarks,
    "Source": SourceBookmarks,
    "Repository": RepoBookmarks,
}


# -----------------------------------------------------------------------------
#
# GlobalNavigationView Class
#
# -----------------------------------------------------------------------------
class GlobalNavigationView(PageView):
    """
    The GlobalNavigationView class is the base class for all views that
    require advanced navigation functionality across multiple object types.
    It requires use of the GlobalHistory class to keep list views in sync.
    """

    def __init__(self, title, pdata, state, uistate, nav_group):
        PageView.__init__(self, title, pdata, state, uistate)
        self.bookmarks_list = self._init_bookmarks()
        self.bookmarks = self.bookmarks_list["Person"]
        self.fwd_action = None
        self.back_action = None
        self.book_action = None
        self.other_action = None
        self.active_signal = None
        self.mru_signal = None
        self.nav_group = nav_group
        self.mru_active = DISABLED
        self.uimanager = uistate.uimanager

        self.mru_action = None
        self.mru_ui = None
        self.dirty = False
        self.lock = False

        self.history = GlobalHistory(self.dbstate, uistate)
        if ("Global", nav_group) not in uistate.history_lookup:
            uistate.history_lookup[("Global", nav_group)] = self.history

        object_history = self.uistate.get_history(self.navigation_type())
        if object_history:
            object_history.connect(
                "active-changed", self.sync(self.navigation_type())
            )
        self.dirty_redraw_trigger = False

    def sync(self, history_type):
        """
        Return a callback to update our view when a corresponding list
        view change is made.
        """

        def sync(handle):
            self.dirty = True
            self.change_active((history_type, handle), quiet=True)

        return sync

    @abstractmethod
    def navigation_type(self):
        """
        Must be set in derived classes. Indictates the navigation
        type, a string representing any of the primary Gramps objects.
        """

    def navigation_group(self):
        """
        Return the navigation group.
        """
        return self.nav_group

    @abstractmethod
    def navigation_group_key(self):
        """
        Return the navigation group key. Should be common value in the id field
        of the view plugins used to find the view when switching categories.
        """

    def get_history(self):
        """
        Return the history object.
        """
        return self.history

    def define_actions(self):
        """
        Define menu actions.
        """
        PageView.define_actions(self)
        self.bookmark_actions()
        self.navigation_actions()

    def disable_action_group(self):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        PageView.disable_action_group(self)
        self.uimanager.set_actions_visible(self.fwd_action, False)
        self.uimanager.set_actions_visible(self.back_action, False)

    def enable_action_group(self, obj):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        if not isinstance(obj, DummyDb):
            PageView.enable_action_group(self, obj)
            self.uimanager.set_actions_visible(self.fwd_action, True)
            self.uimanager.set_actions_visible(self.back_action, True)
            self.uimanager.set_actions_sensitive(
                self.fwd_action, not self.history.at_end()
            )
            self.uimanager.set_actions_sensitive(
                self.back_action, not self.history.at_front()
            )

    def change_category(self, category):
        """
        Switch to different category view.
        """
        if category in CATEGORIES:
            category_name = CATEGORIES[category]
            if category_name != self.get_category():
                viewmanager = self.uistate.viewmanager
                category_index = viewmanager.get_category(category_name)
                if category_index is not None:
                    category_views = viewmanager.get_views()[category_index]
                    if category_views:
                        for (
                            view_index,
                            (view_plugin, _view_class),
                        ) in enumerate(category_views):
                            if self.navigation_group_key() in view_plugin.id:
                                return viewmanager.goto_page(
                                    category_index, view_index
                                )
                        return viewmanager.goto_page(category_index, None)

    def change_person_category(self):
        """
        Check preferred person view and switch category if needed
        """
        if self._config_view.get("general.link-people-to-relationships-view"):
            if self.get_category() != "Relationships":
                self.change_category("Relationship")
        else:
            if self.get_category() != "People":
                self.change_category("Person")

    def change_page(self):
        """
        Called when the page changes.
        """
        self.uimanager.set_actions_sensitive(
            self.fwd_action, not self.history.at_end()
        )
        self.uimanager.set_actions_sensitive(
            self.back_action, not self.history.at_front()
        )
        self.uistate.modify_statusbar(self.dbstate)

    def set_active(self):
        """
        Called when the page becomes active (displayed).
        """
        PageView.set_active(self)
        self.bookmarks.display()
        self.active_signal = self.history.connect(
            "active-changed", self.goto_active
        )
        self.mru_signal = self.history.connect(
            "mru-changed", self.update_mru_menu
        )
        self.update_mru_menu(self.history.mru, update_menu=False)
        self.goto_active(None)

    def set_inactive(self):
        """
        Called when the page becomes inactive (not displayed).
        """
        if self.active:
            PageView.set_inactive(self)
            self.bookmarks.undisplay()
            self.history.disconnect(self.active_signal)
            self.history.disconnect(self.mru_signal)
            self.mru_disable()

    def get_active(self):
        """
        Return the handle of the active object.
        """
        return self.history.present()

    def goto_active(self, _dummy_handle):
        """
        Callback (and usable function) that selects the active person
        in the display tree.
        """
        current_handle = self.history.present()
        if current_handle:
            if current_handle[0] == self.navigation_type():
                if current_handle[0] == "Person":
                    self.change_person_category()
                if not self.history.lock:
                    self.goto_handle(current_handle)
                self.uimanager.set_actions_sensitive(
                    self.fwd_action, not self.history.at_end()
                )
                self.uimanager.set_actions_sensitive(
                    self.back_action, not self.history.at_front()
                )
            else:
                target = current_handle[0]
                if target == "Person" and self._config_view.get(
                    "general.link-people-to-relationships-view"
                ):
                    target = "Relationship"
                return self.change_category(target)

    def change_active(self, obj_tuple, quiet=False):
        """
        Changes the active object.
        """
        if not self.lock:
            self.lock = True
            if len(obj_tuple) == 2:
                full_tuple = (
                    obj_tuple[0],
                    obj_tuple[1],
                    None,
                    None,
                    None,
                    None,
                )
            else:
                full_tuple = obj_tuple
            if full_tuple and not self.history.lock:
                present = self.history.present()
                if full_tuple != present:
                    self.dirty_redraw_trigger = False
                    self.history.push(full_tuple, quiet=quiet)
                elif full_tuple == present and self.dirty_redraw_trigger:
                    self.dirty = True
                    self.goto_active(None)
                    self.dirty_redraw_trigger = False
            self.lock = False

    @abstractmethod
    def goto_handle(self, handle):
        """
        Needs to be implemented by classes derived from this.
        Used to move to the given handle.
        """

    def selected_handles(self):
        """
        Return the active person's handle in a list. Used for
        compatibility with those list views that can return multiply
        selected items.
        """
        active_handle = self.uistate.get_active(
            self.navigation_type(), self.navigation_group()
        )
        return [active_handle] if active_handle else []

    ####################################################################
    # Bookmark related methods
    ####################################################################
    def _init_bookmarks(self):
        """
        Initialize bookmarks list.
        """
        bookmarks = {}
        for (bookmark_type, bookmark_class) in BOOKMARKS.items():
            change_active = partial(self.goto_bookmark, bookmark_type)
            bookmark_handler = bookmark_class(
                self.dbstate, self.uistate, change_active
            )
            bookmarks.update({bookmark_type: bookmark_handler})
        return bookmarks

    def set_bookmarks(self, obj_type):
        """
        Set current bookmarks object.
        """
        self.bookmarks.undisplay()
        if obj_type != "Tag":
            self.bookmarks = self.bookmarks_list[obj_type]

    def goto_bookmark(self, obj_type, obj_handle):
        """
        Goto a bookmarked object
        """
        self.dirty = True
        self.change_active((obj_type, obj_handle, None, None, None, None))

    def add_bookmark(self, *_dummy_obj):
        """
        Add a bookmark to the list.
        """
        active_object = self.get_active()
        self.bookmarks.add(active_object[1])
        self.bookmarks.redraw()

    def edit_bookmarks(self, *_dummy_obj):
        """
        Call the bookmark editor.
        """
        self.bookmarks.edit()

    def bookmark_actions(self):
        """
        Define the bookmark menu actions.
        """
        self.book_action = ActionGroup(name=self.title + "/Bookmark")
        self.book_action.add_actions(
            [
                ("AddBook", self.add_bookmark, "<PRIMARY>d"),
                ("EditBook", self.edit_bookmarks, "<shift><PRIMARY>D"),
            ]
        )
        self._add_action_group(self.book_action)

    ####################################################################
    # Navigation related methods
    ####################################################################
    def navigation_actions(self):
        """
        Define the navigation menu actions.
        """
        # add the Forward action group to handle the Forward button
        self.fwd_action = ActionGroup(name=self.title + "/Forward")
        self.fwd_action.add_actions(
            [("Forward", self.fwd_clicked, "%sRight" % mod_key())]
        )

        # add the Backward action group to handle the Forward button
        self.back_action = ActionGroup(name=self.title + "/Backward")
        self.back_action.add_actions(
            [("Back", self.back_clicked, "%sLeft" % mod_key())]
        )

        self._add_action("HomePerson", self.home, "%sHome" % mod_key())
        self._add_action_group(self.back_action)
        self._add_action_group(self.fwd_action)

    def set_default_person(self, *_dummy_obj):
        """
        Set the default person.
        """
        active = self.uistate.get_active("Person")
        if active:
            self.dbstate.db.set_default_person_handle(active)

    def home(self, *_dummy_obj):
        """
        Move to the default person.
        """
        defperson = self.dbstate.db.get_default_person()
        if defperson:
            self.change_active(("Person", defperson.handle))
        else:
            WarningDialog(
                _("No Home Person"),
                _(
                    "You need to set a 'default person' to go to. "
                    "Select the People View, select the person you want as "
                    "'Home Person', then confirm your choice "
                    "via the menu Edit -> Set Home Person."
                ),
                parent=self.uistate.window,
            )

    def jump(self, *_dummy_obj):
        """
        A dialog to move to a Gramps ID entered by the user.
        """
        dialog = Gtk.Dialog(_("Jump to by Gramps ID"), self.uistate.window)
        dialog.set_border_width(12)
        label = Gtk.Label(
            label='<span weight="bold" size="larger">%s</span>'
            % _("Jump to by Gramps ID")
        )
        label.set_use_markup(True)
        dialog.vbox.add(label)
        dialog.vbox.set_spacing(10)
        dialog.vbox.set_border_width(12)
        hbox = Gtk.Box()
        hbox.pack_start(Gtk.Label(label=_("%s: ") % _("ID")), True, True, 0)
        text = Gtk.Entry()
        text.set_activates_default(True)
        hbox.pack_start(text, False, True, 0)
        dialog.vbox.pack_start(hbox, False, True, 0)
        dialog.add_buttons(
            _("_Cancel"),
            Gtk.ResponseType.CANCEL,
            _("_Jump to"),
            Gtk.ResponseType.OK,
        )
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.vbox.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            gid = text.get_text()
            handle = self.get_handle_from_gramps_id(gid)
            if handle is not None:
                self.change_active(handle)
            else:
                self.uistate.push_message(
                    self.dbstate, _("Error: %s is not a valid Gramps ID") % gid
                )
        dialog.destroy()

    def get_handle_from_gramps_id(self, gid):
        """
        Get an object handle from its Gramps ID.
        Needs to be implemented by the inheriting class.
        """

    def fwd_clicked(self, *_dummy_obj):
        """
        Move forward one object in the history.
        """
        if not self.history.at_end():
            self.dirty = True
            self.history.forward()
            self.uistate.modify_statusbar(self.dbstate)
        self.uimanager.set_actions_sensitive(
            self.fwd_action, not self.history.at_end()
        )
        self.uimanager.set_actions_sensitive(self.back_action, True)

    def back_clicked(self, *_dummy_obj):
        """
        Move backward one object in the history.
        """
        if not self.history.at_front():
            self.dirty = True
            self.history.back()
            self.uistate.modify_statusbar(self.dbstate)
        self.uimanager.set_actions_sensitive(
            self.back_action, not self.history.at_front()
        )
        self.uimanager.set_actions_sensitive(self.fwd_action, True)

    ####################################################################
    # MRU related methods
    ####################################################################
    def mru_disable(self):
        """
        Remove the UI and action groups for the MRU list.
        """
        if self.mru_active != DISABLED:
            self.uimanager.remove_ui(self.mru_active)
            self.uimanager.remove_action_group(self.mru_action)
            self.mru_active = DISABLED

    def mru_enable(self, update_menu=False):
        """
        Enables the UI and action groups for the MRU list.
        """
        if self.mru_active == DISABLED:
            self.uimanager.insert_action_group(self.mru_action)
            self.mru_active = self.uimanager.add_ui_from_string(self.mru_ui)
            if update_menu:
                self.uimanager.update_menu()

    def update_mru_menu(self, items, update_menu=True):
        """
        Builds the UI and action group for the MRU list.
        """
        menuitem = """        <item>
              <attribute name="action">win.%s%02d</attribute>
              <attribute name="label">%s</attribute>
            </item>
            """
        menus = ""
        self.mru_disable()
        nav_type = self.navigation_type()
        menu_len = min(len(items) - 1, MRU_SIZE)

        data = []
        for index in range(menu_len - 1, -1, -1):
            name, dummy_obj = navigation_label(
                self.dbstate.db, items[index][0], items[index][1]
            )
            if name:
                menus += menuitem % (nav_type, index, html.escape(name))
                data.append(
                    (
                        "%s%02d" % (nav_type, index),
                        make_callback(self.history.push, items[index]),
                        "%s%d" % (mod_key(), menu_len - 1 - index),
                    )
                )
        self.mru_ui = [MRU_TOP + menus + MRU_BTM]

        self.mru_action = ActionGroup(name=self.title + "/MRU")
        self.mru_action.add_actions(data)
        self.mru_enable(update_menu)

    @abstractmethod
    def build_tree(self):
        """
        Rebuilds the current display. This must be overridden by the derived
        class.
        """

    @abstractmethod
    def build_widget(self):
        """
        Builds the container widget for the interface. Must be overridden by
        the base class. Returns a gtk container widget.
        """

    def key_press_handler(self, widget, event):
        """
        Handle the control+c (copy) and control+v (paste), or pass it on.
        """
        if (
            self.active
            and event.type == Gdk.EventType.KEY_PRESS
            and event.keyval == Gdk.KEY_c
            and match_primary_mask(event.state)
        ):
            self.call_copy()
            return True
        return super().key_press_handler(widget, event)

    def call_copy(self):
        """
        Navigation specific copy (control+c) hander. If the copy can be handled
        it returns True, otherwise False.

        The code brings up the Clipboard (if already exists) or creates it. The
        copy is handled through the drag and drop system.
        """
        handles = self.selected_handles()
        if handles:
            (
                primary_obj_type,
                primary_obj_handle,
                dummy_reference_obj_type,
                dummy_reference_obj_handle,
                dummy_secondary_obj_type,
                dummy_secondary_obj_hash,
            ) = handles[0]
            self.copy_to_clipboard(primary_obj_type, [primary_obj_handle])


def make_callback(func, handle):
    """
    Generates a callback function based off the passed arguments
    """
    return lambda x, y: func(handle)
