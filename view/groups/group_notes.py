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
NotesGrampsFrameGroup
"""

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames.frame_note import NoteGrampsFrame
from .group_list import GrampsFrameGroupList


# ------------------------------------------------------------------------
#
# NotesGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class NotesGrampsFrameGroup(GrampsFrameGroupList):
    """
    The NotesGrampsFrameGroup class provides a container for managing all
    of the notes associated with an object.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(
            self, grstate, groptions, obj, enable_drop=False
        )
        if not hasattr(obj, "note_list"):
            return

        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        for handle in obj.get_note_list():
            note = self.fetch("Note", handle)
            frame = NoteGrampsFrame(
                grstate,
                groptions,
                note,
            )
            frame.set_size_request(220, -1)
            self.add_frame(frame)
        self.show_all()

    # Todo: Add drag and drop to reorder or add to note list
    def save_new_object(self, handle, insert_row):
        """
        Add new note to the list.
        """
        return
