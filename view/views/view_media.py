# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021       Christopher Horn
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
MediaObjectView
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from .view_base import GrampsObjectView
from .view_const import FRAME_MAP


class MediaObjectView(GrampsObjectView):
    """
    Provides the media object view.
    """

    def __init__(self, grstate, grcontext):
        GrampsObjectView.__init__(self, grstate, grcontext)
        self.colors = None

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        media = self.grcontext.primary_obj

        age_base = None
        if media.obj.get_date_object():
            age_base = media.obj.get_date_object()

        groptions = GrampsOptions("active.media")
        self.view_object = FRAME_MAP["Media"](
            self.grstate, groptions, media.obj
        )
        self.view_focus = self.wrap_focal_widget(self.view_object)
        self.view_header.pack_start(self.view_focus, False, False, 0)

        self.view_body = self.build_object_groups(media, age_base=age_base)
