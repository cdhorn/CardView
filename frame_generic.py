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
GenericGrampsFrameGroup
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_event import EventGrampsFrame
from frame_list import GrampsFrameList
from frame_person import PersonGrampsFrame
from frame_couple import CoupleGrampsFrame


# ------------------------------------------------------------------------
#
# GenericGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class GenericGrampsFrameGroup(GrampsFrameList):
    """
    The GenericGrampsFrameGroup class provides a container for managing a
    set of generic frames for a list of primary Gramps objects.
    """

    def __init__(self, grstate, obj_type, obj_handles):
        GrampsFrameList.__init__(self, grstate)
        self.obj_type = obj_type
        self.obj_handles = obj_handles

        groups = {
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }

        if obj_type == "Person":
            for handle in obj_handles:
                person = grstate.dbstate.db.get_person_from_handle(handle)
                frame = PersonGrampsFrame(grstate, "people", person, groups=groups)
                self.add_frame(frame)

        if obj_type == "Family":
            for handle in obj_handles:
                family = grstate.dbstate.db.get_family_from_handle(handle)
                frame = CoupleGrampsFrame(grstate, "family", family)
                self.add_frame(frame)

        if obj_type == "Event":
            for handle in obj_handles:
                event = grstate.dbstate.db.get_event_from_handle(handle)
                frame = EventGrampsFrame(
                    grstate,
                    "events",
                    None,
                    event,
                    None,
                    None,
                    None,
                    None,
                    groups=groups
                )
                self.add_frame(frame)

        self.show_all()
