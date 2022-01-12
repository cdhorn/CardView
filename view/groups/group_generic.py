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
GenericFrameGroup
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
from ..common.common_classes import GrampsOptions
from ..frames import (
    CitationFrame,
    FamilyFrame,
    EventFrame,
    MediaFrame,
    NoteFrame,
    PersonFrame,
    PlaceFrame,
    RepositoryFrame,
    SourceFrame,
)
from .group_list import FrameGroupList

FRAME_MAP = {
    "Person": PersonFrame,
    "Family": FamilyFrame,
    "Event": EventFrame,
    "Place": PlaceFrame,
    "Media": MediaFrame,
    "Note": NoteFrame,
    "Source": SourceFrame,
    "Citation": CitationFrame,
    "Repository": RepositoryFrame,
}


# ------------------------------------------------------------------------
#
# GenericFrameGroup class
#
# ------------------------------------------------------------------------
class GenericFrameGroup(FrameGroupList):
    """
    The GenericFrameGroup class provides a container for managing a
    set of generic frames for a list of primary Gramps objects.
    """

    def __init__(self, grstate, groptions, frame_obj_type, frame_obj_handles):
        FrameGroupList.__init__(
            self, grstate, groptions, None, enable_drop=False
        )
        self.obj_type = frame_obj_type
        self.obj_handles = frame_obj_handles

        if frame_obj_type == "Tuples":
            tuple_list = frame_obj_handles
        else:
            tuple_list = [(frame_obj_type, x) for x in frame_obj_handles]

        groups = {
            "ref": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "age": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "attributes": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }

        for obj_type, obj_handle in tuple_list:
            if obj_type not in FRAME_MAP:
                continue
            group_space = "".join(("group.", obj_type.lower()))
            group_groptions = GrampsOptions(group_space, size_groups=groups)
            group_groptions.set_age_base(groptions.age_base)
            obj = self.fetch(obj_type, obj_handle)
            frame = FRAME_MAP[obj_type](grstate, group_groptions, obj)
            self.add_frame(frame)
        self.show_all()
