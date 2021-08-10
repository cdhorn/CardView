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
UrlsGrampsFrameGroup
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import re


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
from ..frames.frame_note_url import NoteUrlGrampsFrame
from ..frames.frame_url import UrlGrampsFrame
from ..frames.frame_utils import get_gramps_object_type
from .group_list import GrampsFrameGroupList


# ------------------------------------------------------------------------
#
# UrlsGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class UrlsGrampsFrameGroup(GrampsFrameGroupList):
    """
    The UrlsGrampsFrameGroup class provides a container for launching all
    of the urls associated with an object. It gathers them from the url
    list but also extracts what it can from the notes as well.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(self, grstate, groptions, enable_drop=False)
        self.obj = obj
        self.obj_type, dummy_var1, dummy_var2 = get_gramps_object_type(obj)
        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        self.parse_urls()
        if self.grstate.config.get("options.global.include-note-urls"):
            self.parse_notes()
        self.show_all()

    def parse_urls(self):
        """
        Parse all urls associated with object.
        """
        if hasattr(self.obj, "urls"):
            for url in self.obj.get_url_list():
                frame = UrlGrampsFrame(
                    self.grstate,
                    self.groptions,
                    self.obj,
                    url
                )
                self.add_frame(frame)

    def parse_notes(self):
        """
        Parse all notes associated with object.
        """
        for handle in self.obj.get_note_list():
            self.parse_note(handle)

        for obj in self.obj.get_note_child_list():
            for handle in obj.get_note_list():
                self.parse_note(handle)

    def parse_note(self, handle):
        """
        Parse a specific note extracting urls.
        """
        note = self.grstate.dbstate.db.get_note_from_handle(handle)
        links = re.findall(r"(?P<url>https?://[^\s]+)", note.get())
        if links:
            for link in links:
                self.add_note_url(note, link)

    def add_note_url(self, note, link):
        """
        Add a note url.
        """
        frame = NoteUrlGrampsFrame(
            self.grstate,
            self.groptions,
            note,
            link
        )
        self.add_frame(frame)

