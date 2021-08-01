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
from ..frames.frame_citation import CitationGrampsFrame
from ..frames.frame_couple import CoupleGrampsFrame
from ..frames.frame_event import EventGrampsFrame
from ..frames.frame_image import ImageGrampsFrame
from ..frames.frame_note import NoteGrampsFrame
from ..frames.frame_person import PersonGrampsFrame
from ..frames.frame_place import PlaceGrampsFrame
from ..frames.frame_source import SourceGrampsFrame
from ..frames.frame_repository import RepositoryGrampsFrame
from .group_list import GrampsFrameGroupList


# ------------------------------------------------------------------------
#
# GenericGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class GenericGrampsFrameGroup(GrampsFrameGroupList):
    """
    The GenericGrampsFrameGroup class provides a container for managing a
    set of generic frames for a list of primary Gramps objects.
    """

    def __init__(self, grstate, frame_obj_type, frame_obj_handles):
        GrampsFrameGroupList.__init__(self, grstate)
        self.obj_type = frame_obj_type
        self.obj_handles = frame_obj_handles

        if frame_obj_type == "Tuples":
            tuple_list = frame_obj_handles
        else:
            tuple_list = [(frame_obj_type, x) for x in frame_obj_handles]

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
                    groups=groups,
                )
            elif obj_type == "Place":
                obj = grstate.dbstate.db.get_place_from_handle(obj_handle)
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
            elif obj_type == "Citation":
                obj = grstate.dbstate.db.get_citation_from_handle(obj_handle)
                frame = CitationGrampsFrame(grstate, "citation", obj)
            elif obj_type == "Repository":
                obj = grstate.dbstate.db.get_repository_from_handle(obj_handle)
                frame = RepositoryGrampsFrame(grstate, "repository", obj)
            else:
                continue
            self.add_frame(frame)
        self.show_all()
