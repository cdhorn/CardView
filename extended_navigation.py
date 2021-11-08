#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Nick Hall
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
Provide the base classes for GRAMPS' DataView classes
"""

import html
import logging

# ----------------------------------------------------------------
#
# Python modules
#
# ----------------------------------------------------------------
from abc import abstractmethod

# ----------------------------------------------------------------
#
# Gnome/Gtk modules
#
# ----------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ----------------------------------------------------------------
#
# Gramps modules
#
# ----------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.constfunc import mod_key
from gramps.gen.utils.callback import Callback
from gramps.gen.utils.db import navigation_label
from gramps.gui.uimanager import ActionGroup
from gramps.gui.utils import match_primary_mask
from gramps.gui.views.pageview import PageView

_ = glocale.translation.sgettext

_LOG = logging.getLogger(".navigationview")

DISABLED = -1
MRU_SIZE = 10

MRU_TOP = '<section id="CommonHistory">'
MRU_BTM = "</section>"


# ------------------------------------------------------------------------------
#
# ExtendedNavigationView class
#
# ------------------------------------------------------------------------------
class ExtendedNavigationView(PageView):
    """
    The ExtendedNavigationView class is the base class for all views that
    require advanced navigation functionality across multiple object types.
    It requires use of the ExtendedHistory class to keep list views in sync.
    """

    def __init__(self, title, pdata, state, uistate, bm_type, nav_group):
        PageView.__init__(self, title, pdata, state, uistate)
        self.bookmarks = bm_type(self.dbstate, self.uistate, self.bm_change)

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
        self.active_type = None

        self.other_history = {}
        for history_type in (
            "Person",
            "Family",
            "Event",
            "Place",
            "Media",
            "Note",
            "Citation",
            "Source",
            "Repository",
        ):
            self.other_history[history_type] = self.uistate.get_history(
                history_type
            )
            self.other_history[history_type].connect(
                "active-changed", self.sync(history_type)
            )
        self.history = ExtendedHistory(self.dbstate, self.other_history)

    def sync(self, history_type):
        """
        Return a callback to update our view when a corresponding list
        view change is made.
        """

        def sync(handle):
            self.dirty = True
            self.change_active((history_type, handle))

        return sync

    def bm_change(self, handle):
        """
        Handle bookmark change.
        """
        self.change_active(("Person", handle, None, None, None, None))

    def navigation_type(self):
        """
        Indictates the navigation type. Navigation type can be the string
        name of any of the primary Objects. A History object will be
        created for it, see DisplayState.History
        """
        return None

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
        PageView.enable_action_group(self, obj)

        self.uimanager.set_actions_visible(self.fwd_action, True)
        self.uimanager.set_actions_visible(self.back_action, True)
        hobj = self.get_history()
        self.uimanager.set_actions_sensitive(
            self.fwd_action, not hobj.at_end()
        )
        self.uimanager.set_actions_sensitive(
            self.back_action, not hobj.at_front()
        )

    def change_page(self):
        """
        Called when the page changes.
        """
        hobj = self.get_history()
        self.uimanager.set_actions_sensitive(
            self.fwd_action, not hobj.at_end()
        )
        self.uimanager.set_actions_sensitive(
            self.back_action, not hobj.at_front()
        )
        self.uimanager.set_actions_sensitive(
            self.other_action, not self.dbstate.db.readonly
        )
        self.uistate.modify_statusbar(self.dbstate)

    def set_active(self):
        """
        Called when the page becomes active (displayed).
        """
        PageView.set_active(self)
        self.bookmarks.display()

        hobj = self.get_history()
        self.active_signal = hobj.connect("active-changed", self.goto_active)
        self.mru_signal = hobj.connect("mru-changed", self.update_mru_menu)
        self.update_mru_menu(hobj.mru, update_menu=False)

        self.goto_active(None)

    def set_inactive(self):
        """
        Called when the page becomes inactive (not displayed).
        """
        if self.active:
            PageView.set_inactive(self)
            self.bookmarks.undisplay()
            hobj = self.get_history()
            hobj.disconnect(self.active_signal)
            hobj.disconnect(self.mru_signal)
            self.mru_disable()

    def navigation_group(self):
        """
        Return the navigation group.
        """
        return self.nav_group

    def get_history(self):
        """
        Return the history object.
        """
        return self.history

    def goto_active(self, active_handle):
        """
        Callback (and usable function) that selects the active person
        in the display tree.
        """
        hobj = self.get_history()
        active_handle = hobj.present()
        if active_handle:
            self.goto_handle(active_handle)

        self.uimanager.set_actions_sensitive(
            self.fwd_action, not hobj.at_end()
        )
        self.uimanager.set_actions_sensitive(
            self.back_action, not hobj.at_front()
        )

    def get_active(self):
        """
        Return the handle of the active object.
        """
        hobj = self.get_history()
        return hobj.present()

    def change_active(self, obj_tuple):
        """
        Changes the active object.
        """
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
        hobj = self.get_history()
        if full_tuple and not hobj.lock and not full_tuple == hobj.present():
            self.active_type = full_tuple[1]
            hobj.push(full_tuple)

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
    def add_bookmark(self, *_dummy_obj):
        """
        Add a bookmark to the list.
        """
        from gramps.gen.display.name import displayer as name_displayer

        active_handle = self.uistate.get_active("Person")
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        if active_person:
            self.bookmarks.add(active_handle)
            name = name_displayer.display(active_person)
            self.uistate.push_message(
                self.dbstate, _("%s has been bookmarked") % name
            )
        else:
            from gramps.gui.dialog import WarningDialog

            WarningDialog(
                _("Could Not Set a Bookmark"),
                _(
                    "A bookmark could not be set because "
                    "no one was selected."
                ),
                parent=self.uistate.window,
            )

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

        self.other_action = ActionGroup(name=self.title + "/PersonOther")
        self.other_action.add_actions([("SetActive", self.set_default_person)])

        self._add_action_group(self.back_action)
        self._add_action_group(self.fwd_action)
        self._add_action_group(self.other_action)

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
            self.change_active(("Person", defperson.get_handle()))
        else:
            from ..dialog import WarningDialog

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
        hobj = self.get_history()
        hobj.lock = True
        if not hobj.at_end():
            self.dirty = True
            hobj.forward()
            self.uistate.modify_statusbar(self.dbstate)
        self.uimanager.set_actions_sensitive(
            self.fwd_action, not hobj.at_end()
        )
        self.uimanager.set_actions_sensitive(self.back_action, True)
        hobj.lock = False

    def back_clicked(self, *_dummy_obj):
        """
        Move backward one object in the history.
        """
        hobj = self.get_history()
        hobj.lock = True
        if not hobj.at_front():
            self.dirty = True
            hobj.back()
            self.uistate.modify_statusbar(self.dbstate)
        self.uimanager.set_actions_sensitive(
            self.back_action, not hobj.at_front()
        )
        self.uimanager.set_actions_sensitive(self.fwd_action, True)
        hobj.lock = False

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
        hobj = self.get_history()
        menu_len = min(len(items) - 1, MRU_SIZE)

        data = []
        for index in range(menu_len - 1, -1, -1):
            name, dummy_obj = navigation_label(
                self.dbstate.db, items[index][0], items[index][1]
            )
            menus += menuitem % (nav_type, index, html.escape(name))
            data.append(
                (
                    "%s%02d" % (nav_type, index),
                    make_callback(hobj.push, items[index]),
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
        if self.active:
            if event.type == Gdk.EventType.KEY_PRESS:
                if event.keyval == Gdk.KEY_c and match_primary_mask(
                    event.get_state()
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
            return self.copy_to_clipboard(
                primary_obj_type, [primary_obj_handle]
            )


def make_callback(func, handle):
    """
    Generates a callback function based off the passed arguments
    """
    return lambda x, y: func(handle)


# ------------------------------------------------------------------------------
#
# ExtendedHistory class
#
# ------------------------------------------------------------------------------
class ExtendedHistory(Callback):
    """
    The ExtendedHistory manages the pages that have been viewed, with ability to
    go backward or forward. Unlike a list view History class it can track pages
    for embedded secondary objects. It will also attempt to keep the list view
    history in sync.

    In this extended class a history item or page reference is a tuple
    consisting of:

        (
            primary_object_type,
            primary_object_handle,
            reference_object_type,
            reference_object_handle,
            secondary_object_type,
            secondary_object_hash
        )

    The secondary_object_hash is a sha256 hash of the json serialized object
    that is used as a signature for the object so it can be identified. In
    order for this hash to remain valid when secondary objects are updated
    the replace_secondary method should be called to update the hash as part
    of the update process.
    """

    __signals__ = {"active-changed": (tuple,), "mru-changed": (list,)}

    def __init__(self, dbstate, other_history):
        Callback.__init__(self)
        self.dbstate = dbstate
        self.history = []
        self.other_history = other_history
        self.mru = []
        self.index = -1
        self.lock = False

        dbstate.connect("database-changed", self.connect_signals)
        self.signal_map = {}
        self.signal_map["person-delete"] = self.person_removed
        self.signal_map["person-rebuild"] = self.history_changed
        self.signal_map["family-delete"] = self.family_removed
        self.signal_map["family-rebuild"] = self.history_changed
        self.signal_map["event-delete"] = self.event_removed
        self.signal_map["event-rebuild"] = self.history_changed
        self.signal_map["place-delete"] = self.place_removed
        self.signal_map["place-rebuild"] = self.history_changed
        self.signal_map["media-delete"] = self.media_removed
        self.signal_map["media-rebuild"] = self.history_changed
        self.signal_map["note-delete"] = self.note_removed
        self.signal_map["note-rebuild"] = self.history_changed
        self.signal_map["citation-delete"] = self.citation_removed
        self.signal_map["citation-rebuild"] = self.history_changed
        self.signal_map["source-delete"] = self.source_removed
        self.signal_map["source-rebuild"] = self.history_changed
        self.signal_map["repository-delete"] = self.repository_removed
        self.signal_map["repository-rebuild"] = self.history_changed
        self.signal_map["tag-delete"] = self.tag_removed
        self.connect_signals(dbstate.db)

    def connect_signals(self, db):
        """
        Connects database signals when the database has changed.
        """
        for sig in self.signal_map:
            db.connect(sig, self.signal_map[sig])

    def clear(self):
        """
        Clears the history, resetting the values back to their defaults.
        """
        self.history = []
        self.mru = []
        self.index = -1
        self.lock = False

    def sync_other(self, obj_type, obj_handle):
        """
        Updates the history object for the list view if needed.
        """
        if obj_type in self.other_history:
            sync_hist = self.other_history[obj_type]
            if sync_hist.present() != obj_handle:
                sync_hist.push(obj_handle)

    def push(self, item):
        """
        Pushes the page reference on the history stack and object on the
        mru stack.
        """
        print("history.push start: {}".format(item))
        self.prune()
        if len(item) == 2:
            full_item = (item[0], item[1], None, None, None, None)
        else:
            full_item = item
        if len(self.history) == 0 or full_item != self.history[-1]:
            self.history.append(full_item)
            if full_item[0] != "Tag":
                mru_item = (full_item[0], full_item[1])
                if mru_item in self.mru:
                    self.mru.remove(mru_item)
                self.mru.append(mru_item)
                self.emit("mru-changed", (self.mru,))
            self.index += 1
            if self.history:
                self.emit("active-changed", (full_item,))
            self.sync_other(full_item[0], full_item[1])

    def forward(self, step=1):
        """
        Moves forward in the history list.
        """
        self.index += step
        item = self.history[self.index]
        if item[0] != "Tag":
            mru_item = (item[0], item[1])
            if mru_item in self.mru:
                self.mru.remove(mru_item)
            self.mru.append(mru_item)
            self.emit("mru-changed", (self.mru,))
        self.emit("active-changed", (item,))
        self.sync_other(item[0], item[1])
        return item

    def back(self, step=1):
        """
        Moves backward in the history list.
        """
        self.index -= step
        try:
            item = self.history[self.index]
            if item[0] != "Tag":
                mru_item = (item[0], item[1])
                if mru_item in self.mru:
                    self.mru.remove(mru_item)
                self.mru.append(mru_item)
                self.emit("mru-changed", (self.mru,))
            self.emit("active-changed", (item,))
            self.sync_other(item[0], item[1])
            return item
        except IndexError:
            return ""

    def present(self):
        """
        Return the active/current history object.
        """
        try:
            if self.history:
                return self.history[self.index]
            return ""
        except IndexError:
            return ""

    def at_end(self):
        """
        Return True if at the end of the history list.
        """
        return self.index + 1 == len(self.history)

    def at_front(self):
        """
        Return True if at the front of the history list.
        """
        return self.index <= 0

    def prune(self):
        """
        Truncate the history list at the current object.
        """
        if not self.at_end():
            self.history = self.history[0 : self.index + 1]

    def person_removed(self, handle_list):
        """
        Remove a person from the history.
        """
        self.handles_removed("Person", handle_list)

    def family_removed(self, handle_list):
        """
        Remove a family from the history.
        """
        self.handles_removed("Family", handle_list)

    def event_removed(self, handle_list):
        """
        Remove an event from the history.
        """
        self.handles_removed("Event", handle_list)

    def place_removed(self, handle_list):
        """
        Remove a place from the history.
        """
        self.handles_removed("Place", handle_list)

    def media_removed(self, handle_list):
        """
        Remove a media item from the history.
        """
        self.handles_removed("Media", handle_list)

    def note_removed(self, handle_list):
        """
        Remove a note from the history.
        """
        self.handles_removed("Note", handle_list)

    def citation_removed(self, handle_list):
        """
        Remove a citation from the history.
        """
        self.handles_removed("Citation", handle_list)

    def source_removed(self, handle_list):
        """
        Remove a source from the history.
        """
        self.handles_removed("Source", handle_list)

    def repository_removed(self, handle_list):
        """
        Remove a repository from the history.
        """
        self.handles_removed("Repository", handle_list)

    def tag_removed(self, handle_list):
        """
        Remove a tag from the history.
        """
        self.handles_removed("Tag", handle_list, silent=True)

    def handles_removed(self, _dummy_var, handle_list, silent=False):
        """
        Removes pages for a specific object from the history.
        """
        for handle in handle_list:
            for item in self.history:
                if handle in [item[1], item[3]]:
                    self.history.remove(item)
                    self.index -= 1

            for item in self.mru:
                if item[1] == handle:
                    self.mru.remove(item)
        if not silent:
            if self.history:
                self.emit("active-changed", (self.history[self.index],))
            self.emit("mru-changed", (self.mru,))

    def replace_secondary(self, old, new):
        """
        Replace old secondary handle or hash value with new one.
        """
        for item in self.history:
            if item[5] == old:
                new_item = (
                    item[0],
                    item[1],
                    item[2],
                    item[3],
                    item[4],
                    new,
                )
                index = self.history.index(item)
                self.history.remove(item)
                self.history.insert(index, new_item)

    def history_changed(self):
        """
        Called in response to an object-rebuild signal.
        Objects in the history list may have been deleted.
        """
        self.clear()
        self.emit("mru-changed", (self.mru,))
