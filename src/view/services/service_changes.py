# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2022       Christopher Horn
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

"""
ChangedObjectService
"""

# This was derived from the LastChange Gramplet

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from bisect import bisect
from copy import copy

# ------------------------------------------------------------------------
#
# GRAMPS modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.datehandler import format_time
from gramps.gen.utils.callback import Callback
from gramps.gen.utils.db import navigation_label

_ = glocale.translation.sgettext

# This is dependent on the serialization format of the objects. Unfortunately
# they do not all have POS_ variables for reference. So this is dependent on
# Gramps version, and will break when objects change in the master branch
# during development.

# Index for Gramps 5.1 objects
SERIALIZATION_INDEX = {
    "Person": 17,
    "Family": 12,
    "Event": 10,
    "Place": 15,
    "Source": 8,
    "Citation": 9,
    "Repository": 7,
    "Media": 9,
    "Note": 5,
    "Tag": 4,
}


def get_object_label(db, object_type, object_handle):
    """
    Generate meaningful label for the object.
    """
    if object_type != "Tag":
        name, obj = navigation_label(db, object_type, object_handle)
    else:
        obj = db.get_tag_from_handle(object_handle)
        name = "".join(("[", _("Tag"), "] ", obj.get_name()))
    return name, obj


def get_formatted_handle_list(db, handle_list):
    """
    Prepare a label and formatted time for all the objects.
    """
    full_list = []
    for (object_type, object_handle, change) in handle_list:
        change = -change
        label, dummy_obj = get_object_label(db, object_type, object_handle)
        full_list.append(
            (object_type, object_handle, label, change, format_time(change))
        )
    return full_list


def get_latest_handles(db, object_type, list_method, depth=10):
    """
    Get the most recently changed object handles for a given object type.
    """
    handle_list = []
    raw_method = db.method("get_raw_%s_data", object_type.lower())
    change_index = SERIALIZATION_INDEX[object_type]
    for object_handle in list_method():
        change = -raw_method(object_handle)[change_index]
        bsindex = bisect(KeyWrapper(handle_list, key=lambda c: c[2]), change)
        handle_list.insert(bsindex, (object_type, object_handle, change))
        if len(handle_list) > depth:
            handle_list.pop(depth)
    return get_formatted_handle_list(db, handle_list)


def get_all_object_handles(db, depth=10):
    """
    Gather and return all recently changed handles and a coalesced global list.
    """
    change_history = {}
    global_history = []
    for object_type in SERIALIZATION_INDEX:
        if object_type == "Citation":
            list_method = db.get_citation_handles
        else:
            list_method = db.method("iter_%s_handles", object_type.lower())
        handle_list = get_latest_handles(db, object_type, list_method, depth)
        change_history[object_type] = handle_list
        global_history = global_history + handle_list
    global_history.sort(key=lambda x: x[3], reverse=True)
    change_history["Global"] = global_history[:depth]
    return change_history


# The general idea here is that if different views or gramplets are going to
# make use of this data we should only collect and update it a single time
# in one place and let them reference it there as needed.


class ChangedObjectService(Callback):
    """
    A singleton for centrally tracking changed objects in the database.
    """

    __signals__ = {"change-notification": (str, str)}

    __slots__ = ("dbstate", "depth", "change_history", "signal_map")

    __init = False

    def __new__(cls, *args, **kwargs):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(ChangedObjectService, cls).__new__(cls)
        return cls.instance

    def __init__(self, dbstate, depth=10):
        """
        Initialize the class if needed.
        """
        if not self.__init:
            Callback.__init__(self)
            self.dbstate = dbstate
            self.depth = depth
            self.change_history = {}
            self.signal_map = {}

            self.register_signal("Person")
            self.register_signal("Family")
            self.register_signal("Event")
            self.register_signal("Place")
            self.register_signal("Source")
            self.register_signal("Citation")
            self.register_signal("Repository")
            self.register_signal("Media")
            self.register_signal("Note")
            self.register_signal("Tag")
            self.initialize_change_history()
            dbstate.connect("database-changed", self.initialize_change_history)
            self.__init = True

    def register_signal(self, object_type):
        """
        Register signal.
        """
        update_function = lambda x: self.update_change_history(x, object_type)
        delete_function = lambda x: self.delete_change_history(x, object_type)
        lower_type = object_type.lower()
        for sig in ["add", "update", "rebuild"]:
            self.signal_map["{}-{}".format(lower_type, sig)] = update_function
        self.signal_map["{}-delete".format(lower_type)] = delete_function

    def change_depth(self, depth):
        """
        Change depth, rebuild list and issue synthetic change notification.
        """
        self.depth = depth
        self.load_change_history()
        if self.change_history["Global"]:
            last_object = self.change_history["Global"][0]
            self.emit("change-notification", (last_object[0], last_object[1]))

    def load_change_history(self):
        """
        Load the change history.
        """
        self.change_history = get_all_object_handles(
            self.dbstate.db, self.depth
        )

    def initialize_change_history(self, *args):
        """
        Rebuild history and connect database signals for change notifications.
        """
        self.load_change_history()
        for sig, callback in self.signal_map.items():
            self.dbstate.db.connect(sig, callback)

    def update_change_history(self, object_handles, object_type):
        """
        Update history and emit object modification signal.
        """
        if object_handles:
            object_handle = object_handles[0]
            object_label, changed_object = get_object_label(
                self.dbstate.db, object_type, object_handle
            )
            changed_tuple = (
                object_type,
                object_handle,
                object_label,
                changed_object.change,
                format_time(changed_object.change),
            )
            self.change_history[object_type].insert(0, changed_tuple)
            if len(self.change_history[object_type]) > self.depth:
                self.change_history[object_type].pop()
            self.change_history["Global"].insert(0, changed_tuple)
            if len(self.change_history["Global"]) > self.depth:
                self.change_history["Global"].pop()
            self.emit("change-notification", (object_type, object_handle))

    def delete_change_history(self, object_handles, object_type):
        """
        If deleted from history rebuild history and emit notification.
        """
        if object_handles:
            object_handle = object_handles[0]
            if self.check_removed_object(
                object_type, object_handle
            ) or self.check_removed_object("Global", object_handle):
                self.load_change_history()
                self.emit("change-notification", (object_type, object_handle))

    def check_removed_object(self, object_type, object_handle):
        """
        Check if deleted handle in current history.
        """
        for object_data in self.change_history[object_type]:
            if object_data[1] == object_handle:
                return True
        return False

    def get_change_history(self, obj_type=None):
        """
        Return change history.
        """
        if obj_type in self.change_history:
            return self.change_history[obj_type]
        return self.change_history


class KeyWrapper:
    """
    For bisect to operate on an element of a tuple in the list.
    """

    def __init__(self, iterable, key):
        self.iter = iterable
        self.key = key

    def __getitem__(self, i):
        return self.key(self.iter[i])

    def __len__(self):
        return len(self.iter)
