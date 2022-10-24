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
# Gtk Modules
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
from gramps.gen.utils.callback import Callback

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from .service_statistics_worker import gather_statistics, get_object_list

CATEGORIES = [
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

_ = glocale.translation.sgettext


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
                    "dashboard.concurrent-threshold"
                )
                self.all_events = grstate.config.get(
                    "dashboard.summarize-all-events"
                )
                self.threads = []
                self.lock = Lock()
                self.data = {}
                self.worker = find_statistics_service_worker()
                self.concurrent = self.determine_collection_method()
                self.signal_map = {}
                for obj_type in CATEGORIES:
                    self.__register_signals(obj_type)
                self.dbstate.connect("database-changed", self.database_changed)
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
        lower_type = object_type.lower()
        for sig in ["add", "update", "delete", "rebuild"]:
            self.signal_map[
                "{}-{}".format(lower_type, sig)
            ] = self.change_detected

    def change_detected(self, *_dummy_args):
        """
        Emit change detected signal.
        """
        self.emit("changes-detected", ())

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
            except FileNotFoundError:
                self.worker = None
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
