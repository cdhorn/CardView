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
from subprocess import Popen, PIPE
from threading import Thread, Lock

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import USER_PLUGINS


_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# StatisticsService
#
# -------------------------------------------------------------------------
class StatisticsService:
    """
    A singleton class that collects and manages database statistics.
    """

    __init = False

    def __new__(cls, *args):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(StatisticsService, cls).__new__(cls)
        return cls.instance

    def __init__(self, dbstate):
        """
        Initialize the class if needed.
        """
        if not self.__init:
            self.dbstate = dbstate
            self.data = {}
            self.worker = find_statistics_service_worker()
            self.dbstate.connect("database-changed", self.database_changed)
            self.__init = True

    def gather_data(self):
        s = time.time()
        dbname = self.dbstate.db.get_dbname()
        pipe = Popen(["python", "-u", self.worker, "-t", dbname], stdout=PIPE)
        output, errors = pipe.communicate()
        self.data = pickle.loads(output)
        print("stats collected: %s" % (time.time() - s), file=sys.stderr)

    def database_changed(self, *args):
        """
        Rescan the database.
        """
        if self.dbstate.is_open():
            self.gather_data()
        else:
            self.data.clear()

    def get_data(self):
        if self.data == {}:
            self.gather_data()
        return self.data


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
        "statistics_worker.py",
    )
    if not os.path.isfile(filepath):
        for root, dirs, files in os.walk(USER_PLUGINS):
            if "statistics_worker.py" in files:
                filepath = os.path.join(root, "statistics_worker.py")
                break
    return filepath
