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
GenericRefObjectView
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from .view_base import GrampsObjectView
from .view_const import FRAME_MAP


class GenericRefObjectView(GrampsObjectView):
    """
    Provides an object view that handles basic reference objects.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        build_frame = FRAME_MAP[self.primary_obj.obj_type]
        option_space = ".".join(
            ("options.active", self.primary_obj.obj_type.lower())
        )
        groptions = GrampsOptions(option_space)
        subject_frame = build_frame(
            self.grstate, groptions, self.primary_obj.obj
        )
        self.view_header.pack_start(subject_frame, False, False, 0)

        build_frame = FRAME_MAP[self.reference_obj.obj_type]
        option_space = ".".join(
            ("options.active", self.reference_obj.obj_type.lower())
        )
        groptions = GrampsOptions(option_space)
        self.view_object = build_frame(
            self.grstate,
            groptions,
            self.primary_obj.obj,
            self.reference_obj.obj,
        )
        self.view_focus = self.wrap_focal_widget(self.view_object)
        self.view_header.pack_start(self.view_focus, False, False, 0)

        self.view_body = self.build_object_groups(self.grcontext.reference_obj)
