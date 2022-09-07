#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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
#

"""
StatisticsService
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import os
import sys
import time
import pickle
from subprocess import Popen, PIPE, TimeoutExpired
from threading import Event, Lock, Thread

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gi.repository import GLib

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import USER_PLUGINS
from gramps.gen.datehandler import format_time
from gramps.gen.utils.callback import Callback
from gramps.gen.utils.db import navigation_label

from .service_statistics_worker import gather_statistics, get_object_list


_ = glocale.translation.sgettext

SERIALIZATION_INDEX = [
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
]


# -------------------------------------------------------------------------
#
# StatisticsService
#
# -------------------------------------------------------------------------
class StatisticsService(Callback):
    """
    A singleton class that collects and manages database statistics.
    """

    __signals__ = {
        "statistics-updated": (dict,),
        "changes-detected": (),
        "changes-updated": (),
    }

    __init = False
    __init_callback = False

    def __new__(cls, *args):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(StatisticsService, cls).__new__(cls)
        return cls.instance

    def __init__(self, grstate=None):
        """
        Initialize the class if needed.
        """
        if not self.__init:
            if not self.__init_callback:
                Callback.__init__(self)
                self.__init_callback = True
            if grstate:
                self.dbstate = grstate.dbstate
                self.threshold = grstate.config.get(
                    "general.concurrent-threshold"
                )
                self.all_events = grstate.config.get(
                    "general.summarize-all-events"
                )
                self.threads = []
                self.lock = Lock()
                self.data = {}
                self.change_history = {}
                self.worker = find_statistics_service_worker()
                self.concurrent = self.determine_collection_method()
                self.signal_map = {}
                for obj_type in SERIALIZATION_INDEX:
                    self.__register_signals(obj_type)
                self.dbstate.connect("database-changed", self.database_changed)
                grstate.uistate.connect(
                    "nameformat-changed", self.rebuild_name_labels
                )
                grstate.uistate.connect(
                    "placeformat-changed", self.rebuild_place_labels
                )
                self.__init = True

    def __init_signals(self):
        """
        Connect to signals from database.
        """
        for sig, callback in self.signal_map.items():
            self.dbstate.db.connect(sig, callback)

    def __register_signals(self, object_type):
        """
        Register signal.
        """
        update_function = lambda x: self.update_change_history(x, object_type)
        delete_function = lambda x: self.delete_change_history(x, object_type)
        lower_type = object_type.lower()
        for sig in ["add", "update", "rebuild"]:
            self.signal_map["{}-{}".format(lower_type, sig)] = update_function
        self.signal_map["{}-delete".format(lower_type)] = delete_function

    def determine_collection_method(self):
        """
        Determine based on size what method to try to use.
        """
        if self.dbstate.is_open():
            total, dummy_obj_list = get_object_list(
                self.dbstate.db.get_dbname()
            )
            if total > self.threshold:
                return True
        return False

    def emit_statistics_updated(self, thread_dbname):
        """
        Emit statistics updated signal.
        """
        for (index, (dbname, dummy_thread, dummy_event)) in enumerate(
            self.threads
        ):
            if dbname == thread_dbname:
                if self.dbstate.db.get_dbname() == thread_dbname:
                    self.emit("statistics-updated", (self.data,))
                    self.rebuild_change_history()
                    self.emit("changes-updated", ())
                del self.threads[index]
        return False

    def clean_stale_thread(self, thread_dbname):
        """
        Cleanup aborted thread entry.
        """
        for (index, (dbname, dummy_thread, dummy_event)) in enumerate(
            self.threads
        ):
            if dbname == thread_dbname:
                del self.threads[index]

    def collect_statistics(self, event, dbname):
        """
        Thread to handle the statistics collection work.
        """
        s = time.time()
        done = False
        if self.concurrent and self.worker:
            args = ["python3", "-u", self.worker, "-t", dbname]
            if self.all_events:
                args.append("-a")
            try:
                process = Popen(args, stdout=PIPE)
                finished = False
                while not finished:
                    try:
                        output, dummy_errors = process.communicate(timeout=0.1)
                        finished = True
                    except TimeoutExpired:
                        if event.is_set():
                            process.terminate()
                            output, dummy_errors = process.communicate()
                            finished = True
                if not event.is_set():
                    with self.lock:
                        self.data = pickle.loads(output)
                print(
                    "stats collected: %s" % (time.time() - s), file=sys.stderr
                )
                done = True
            except EOFError:
                self.worker = None
        if not done:
            args = {
                "all_events": self.all_events,
                "tree_name": dbname,
                "serial": True,
            }
            dummy_total, data = gather_statistics(args, event=event)
            if not event.is_set():
                with self.lock:
                    self.data = data
            print("stats collected: %s" % (time.time() - s), file=sys.stderr)
        if not event.is_set():
            GLib.idle_add(self.emit_statistics_updated, dbname)
        else:
            GLib.idle_add(self.clean_stale_thread, dbname)

    def spawn_collect_statistics(self):
        """
        Spawn statistics collection thread.
        """
        current_dbname = self.dbstate.db.get_dbname()
        if current_dbname:
            need_collect = True
            for (dbname, dummy_thread, event) in self.threads:
                if dbname == current_dbname:
                    need_collect = False
                else:
                    event.set()
            if need_collect:
                self.concurrent = self.determine_collection_method()
                with self.lock:
                    self.data.clear()
                    event = Event()
                    thread = Thread(
                        target=self.collect_statistics,
                        args=(
                            event,
                            current_dbname,
                        ),
                    )
                    self.threads.append((current_dbname, thread, event))
                    thread.start()
        else:
            for (dummy_dbname, dummy_thread, event) in self.threads:
                event.set()
            with self.lock:
                self.data.clear()

    def database_changed(self, *_dummy_args):
        """
        Rescan the database.
        """
        self.__init_signals()
        self.spawn_collect_statistics()

    def request_data(self):
        """
        Return data if available otherwise initiate statistics collection.
        """
        with self.lock:
            if self.data != {}:
                return self.data
        self.spawn_collect_statistics()
        return None

    def recalculate_data(self):
        """
        Force a statistics collection if one not running.
        """
        self.spawn_collect_statistics()

    def rebuild_change_history(self):
        """
        Rebuild change history from collected statistics.
        """
        change_history = {}
        global_history = []
        for obj_type in SERIALIZATION_INDEX:
            handle_list = [
                (obj_type, x, y) for (x, y) in self.data["changed"][obj_type]
            ]
            formatted_history = get_formatted_handle_list(
                self.dbstate.db, handle_list
            )
            change_history[obj_type] = formatted_history
            global_history = global_history + formatted_history
        global_history.sort(key=lambda x: x[3], reverse=True)
        change_history["Global"] = global_history[:20]
        with self.lock:
            self.change_history = change_history

    def get_change_history(self):
        """
        Fetch the history.
        Callers should lock and unlock around this.
        """
        if not self.__init:
            return {}
        if not self.dbstate.is_open():
            return {}
        if (
            "Global" in self.change_history
            and not self.change_history["Global"]
        ):
            return {}
        if self.change_history == {}:
            self.spawn_collect_statistics()
        return self.change_history

    def update_change_history(self, object_handles, object_type):
        """
        Update history and emit object modification signal.
        """
        self.emit("changes-detected", ())
        if object_handles:
            object_handle = object_handles[0]
            self.clean_change_history(object_type, object_handle)
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
            if len(self.change_history[object_type]) > 20:
                self.change_history[object_type].pop()
            self.change_history["Global"].insert(0, changed_tuple)
            if len(self.change_history["Global"]) > 20:
                self.change_history["Global"].pop()
            print("update change hist emitting")
            self.emit("changes-updated", ())

    def rebuild_labels(self, category):
        """
        Rebuild labels for a formatting change and trigger synthetic update.
        """
        for (
            index,
            (object_type, object_handle, object_label, change, change_string),
        ) in enumerate(self.change_history[category]):
            object_label, dummy_object = get_object_label(
                self.dbstate.db, object_type, object_handle
            )
            updated_tuple = (
                object_type,
                object_handle,
                object_label,
                change,
                change_string,
            )
            self.change_history[category][index] = updated_tuple
            self.replace_global_label(object_handle, updated_tuple)
        self.emit("changes-updated", ())

    def replace_global_label(self, object_handle, updated_tuple):
        """
        Replace a label in the Global history.
        """
        for (index, object_data) in enumerate(self.change_history["Global"]):
            if object_data[1] == object_handle:
                self.change_history["Global"][index] = updated_tuple
                break

    def rebuild_name_labels(self):
        """
        Rebuild labels for a name format change.
        """
        self.rebuild_labels("Person")

    def rebuild_place_labels(self):
        """
        Rebuild labels for a place format change and trigger synthetic update.
        """
        self.rebuild_labels("Place")

    def clean_change_history(self, object_type, object_handle):
        """
        Remove the given object from the history if it is present.
        """
        for index in ["Global", object_type]:
            for object_data in self.change_history[index]:
                if object_data[1] == object_handle:
                    self.change_history[index].remove(object_data)

    def delete_change_history(self, object_handles, object_type):
        """
        If deleted from history rebuild history and emit notification.
        """
        self.emit("changes-detected", ())
        if object_handles:
            object_handle = object_handles[0]
            if self.check_removed_object(
                object_type, object_handle
            ) or self.check_removed_object("Global", object_handle):
                self.change_history = {}
                print("update change hist emitting")
                self.emit("changes-updated", ())

    def check_removed_object(self, object_type, object_handle):
        """
        Check if deleted handle in current history.
        """
        for object_data in self.change_history[object_type]:
            if object_data[1] == object_handle:
                return True
        return False


def find_statistics_service_worker():
    """
    Locate the statistics service worker.
    """
    filepath = os.path.join(
        USER_PLUGINS,
        "CardView",
        "src",
        "view",
        "services",
        "service_statistics_worker.py",
    )
    if not os.path.isfile(filepath):
        for root, dummy_dirs, files in os.walk(USER_PLUGINS):
            if "service_statistics_worker.py" in files:
                filepath = os.path.join(root, "service_statistics_worker.py")
                break
    return filepath


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
