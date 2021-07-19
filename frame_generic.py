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
from frame_couple import CoupleGrampsFrame
from frame_event import EventGrampsFrame
from frame_image import ImageGrampsFrame
from frame_list import GrampsFrameList
from frame_note import NoteGrampsFrame
from frame_person import PersonGrampsFrame
from frame_place import PlaceGrampsFrame
from frame_source import SourceGrampsFrame
from frame_repository import RepositoryGrampsFrame


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

        if obj_type == 'Tuples':
            tuple_list = obj_handles
        else:
            tuple_list = [(obj_type, x) for x in obj_handles]

        groups = {
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }

        for obj_type, obj_handle in tuple_list:
            if obj_type == "Person":
                obj = grstate.dbstate.db.get_person_from_handle(obj_handle)
                frame = PersonGrampsFrame(grstate, "people", obj, groups=groups)
            elif obj_type == "Family":
                obj = grstate.dbstate.db.get_family_from_handle(obj_handle)
                frame = CoupleGrampsFrame(grstate, "family", obj)
            elif obj_type == "Event":
                obj = grstate.dbstate.db.get_event_from_handle(obj_handle)
                frame = EventGrampsFrame(
                    grstate,
                    "events",
                    None,
                    obj,
                    None,
                    None,
                    None,
                    None,
                    groups=groups
                )
            elif obj_type == "Place":
                obj = grstate.dbstate.db.get_family_from_handle(obj_handle)
                frame = PlaceGrampsFrame(grstate, "place", obj)
            elif obj_type == "Media":
                obj = grstate.dbstate.db.get_media_from_handle(obj_handle)
                frame = ImageGrampsFrame(grstate, "media", obj)
            elif obj_type == "Note":
                obj = grstate.dbstate.db.get_note_from_handle(obj_handle)
                frame = NoteGrampsFrame(grstate, "note", obj)
            elif obj_type == "Source":
                obj = grstate.dbstate.db.get_source_from_handle(obj_handle)
                frame = SourceGrampsFrame(grstate, "source", obj)
            elif obj_type == "Repository":
                obj = grstate.dbstate.db.get_repository_from_handle(obj_handle)
                frame = RepositoryGrampsFrame(grstate, "repository", obj)
            else:
                continue
            self.add_frame(frame)
        self.show_all()
