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
ExtendedHistory
"""

# ----------------------------------------------------------------
#
# Gramps Modules
#
# ----------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.callback import Callback

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------------
#
# ExtendedHistory Class
#
# ------------------------------------------------------------------------------
class ExtendedHistory(Callback):
    """
    The ExtendedHistory manages the pages that have been viewed, with ability to
    go backward or forward. Unlike a list view History class it can track pages
    for embedded secondary objects. It will also attempt to keep the list view
    histories in sync.

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

    __slots__ = ("uistate", "history", "mru", "index", "lock", "signal_map")

    _init = False

    def __new__(cls, *args):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(ExtendedHistory, cls).__new__(cls)
        return cls.instance

    def __init__(self, dbstate, uistate):
        """
        Initialize the class if needed.
        """
        if not self._init:
            Callback.__init__(self)
            self.uistate = uistate
            self.history = []
            self.mru = []
            self.index = -1
            self.lock = False
            self.signal_map = {}
            for nav_type in [
                "Person",
                "Family",
                "Event",
                "Place",
                "Source",
                "Citation",
                "Repository",
                "Media",
                "Note",
                "Tag",
            ]:
                self.uistate.register(dbstate, nav_type, 0)
                self.signal_map[
                    "{}-delete".format(nav_type.lower())
                ] = self.handles_removed
                self.signal_map[
                    "{}-rebuild".format(nav_type.lower())
                ] = self.history_changed
            self.signal_map["tag-delete"] = self.handles_removed
            self.connect_signals(dbstate.db)
            dbstate.connect("database-changed", self.connect_signals)
            self._init = True

    def connect_signals(self, db):
        """
        Connects database signals when the database has changed.
        """
        for sig, callback in self.signal_map.items():
            db.connect(sig, callback)

    def clear(self):
        """
        Clears the history, resetting the values back to their defaults.
        """
        self.history = []
        self.mru = []
        self.index = -1
        self.lock = False

    def sync_object_history(self, obj_type, obj_handle):
        """
        Updates the history object for the list view if needed.
        """
        object_history = self.uistate.get_history(obj_type)
        if object_history and object_history.present() != obj_handle:
            object_history.push(obj_handle)

    def push(self, item, quiet=False, initial=False):
        """
        Pushes the page reference on the history stack and object on the
        mru stack.
        """
        self.prune()
        if len(item) == 2:
            full_item = (item[0], item[1], None, None, None, None)
        else:
            full_item = item
        if len(self.history) == 0 or full_item != self.history[-1]:
            self.history.append(full_item)
            self.index += 1
            if not quiet:
                if full_item[0] != "Tag":
                    mru_item = (full_item[0], full_item[1])
                    if mru_item in self.mru:
                        self.mru.remove(mru_item)
                    self.mru.append(mru_item)
                    self.emit("mru-changed", (self.mru,))
                self.emit("active-changed", (full_item,))
                self.sync_object_history(full_item[0], full_item[1])
            elif initial and full_item[0] != "Tag":
                mru_item = (full_item[0], full_item[1])
                self.mru.append(mru_item)

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
        self.sync_object_history(item[0], item[1])
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
            self.sync_object_history(item[0], item[1])
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

    def handles_removed(self, handle_list):
        """
        Removes pages for a specific object from the history.
        """
        silent = False
        for handle in handle_list:
            for item in self.history:
                if handle in [item[1], item[3]]:
                    self.history.remove(item)
                    self.index -= 1
                    if item[0] == "Tag":
                        silent = True

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
        replaced_item = False
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
                replaced_item = True
        return replaced_item

    def history_changed(self):
        """
        Called in response to an object-rebuild signal.
        Objects in the history list may have been deleted.
        """
        self.clear()
        self.emit("mru-changed", (self.mru,))
