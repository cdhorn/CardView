#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
AddressesGrampsFrameGroup
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
from gramps.gen.db import DbTxn


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_address import AddressGrampsFrame
from frame_list import GrampsFrameList
from frame_utils import get_gramps_object_type

# ------------------------------------------------------------------------
#
# AddressesGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class AddressesGrampsFrameGroup(GrampsFrameList):
    """
    The AddressesGrampsFrameGroup class provides a container for managing
    all of the associations a person has with other people.
    """

    def __init__(self, grstate, obj):
        GrampsFrameList.__init__(self, grstate)
        self.obj = obj
        self.obj_type, skip, skip = get_gramps_object_type(obj)
        if not self.option("layout", "tabbed"):
            self.hideable = self.option("layout.address", "hideable")

        groups = {
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }

        for address in obj.get_address_list():
            frame = AddressGrampsFrame(
                grstate,
                "address",
                obj,
                address,
                groups=groups,
            )
            self.add_frame(frame)
        self.show_all()

