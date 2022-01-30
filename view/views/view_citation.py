#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021-2022  Christopher Horn
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
CitationObjectView
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from .view_base import GrampsObjectView
from .view_const import FRAME_MAP


# -------------------------------------------------------------------------
#
# CitationObjectView Class
#
# -------------------------------------------------------------------------
class CitationObjectView(GrampsObjectView):
    """
    Provides the citation object view.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        citation = self.grcontext.primary_obj

        age_base = None
        if citation.obj.get_date_object():
            age_base = citation.obj.get_date_object()

        if citation.obj.source_handle:
            source = self.grstate.dbstate.db.get_source_from_handle(
                citation.obj.source_handle
            )
            groptions = GrampsOptions("active.source")
            source_frame = FRAME_MAP["Source"](self.grstate, groptions, source)
            self.view_header.pack_start(source_frame, False, False, 0)

        groptions = GrampsOptions("active.citation")
        self.view_object = FRAME_MAP["Citation"](
            self.grstate, groptions, citation.obj
        )
        self.view_focus = self.wrap_focal_widget(self.view_object)
        self.view_header.pack_start(self.view_focus, False, False, 0)

        self.view_body = self.build_object_groups(citation, age_base=age_base)
