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
SourcesGrampsFrameGroup
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


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames.frame_source import SourceGrampsFrame
from ..frames.frame_utils import get_gramps_object_type
from .group_list import GrampsFrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# SourcesGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class SourcesGrampsFrameGroup(GrampsFrameGroupList):
    """
    The SourcesGrampsFrameGroup class provides a container for viewing and
    managing all of the sources associated with a primary Gramps object.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(self, grstate, groptions)
        self.obj = obj
        self.obj_type, dummy_var1, dummy_var2 = get_gramps_object_type(obj)
        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        sources_list = []
        if self.obj_type == "Repository":
            for (
                obj_type,
                obj_handle,
            ) in grstate.dbstate.db.find_backlink_handles(
                self.obj.get_handle()
            ):
                if obj_type == "Source":
                    source = self.grstate.dbstate.db.get_source_from_handle(
                        obj_handle
                    )
                    sources_list.append(source)

        if sources_list:
            for source in sources_list:
                frame = SourceGrampsFrame(
                    grstate,
                    groptions,
                    source,
                )
                self.add_frame(frame)
        self.show_all()

    # Todo
    def save_new_object(self, handle, insert_row):
        """
        Add new source to the repository.
        """