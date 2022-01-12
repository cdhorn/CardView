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
GenericObjectView
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from .view_base import GrampsObjectView
from .view_const import FRAME_MAP


class GenericObjectView(GrampsObjectView):
    """
    Provides an object view that handles most basic objects.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        primary = self.grcontext.primary_obj
        reference = self.grcontext.reference_obj
        secondary = self.grcontext.secondary_obj

        build_frame = FRAME_MAP[primary.obj_type]
        option_space = ".".join(("active", primary.obj_type.lower()))
        groptions = GrampsOptions(option_space)
        primary_frame = build_frame(self.grstate, groptions, primary.obj)

        groups = primary
        if reference:
            groups = reference
            reference_frame = self.build_secondary_frame(primary, reference)
            self.view_object = reference_frame
            self.view_focus = self.wrap_focal_widget(self.view_object)
            self.view_header.pack_start(primary_frame, False, False, 0)
            self.view_header.pack_start(self.view_focus, False, False, 0)
        elif secondary:
            groups = secondary
            self.view_object = self.build_secondary_frame(primary, secondary)
            self.view_focus = self.wrap_focal_widget(self.view_object)
            self.view_header.pack_start(primary_frame, False, False, 0)
            self.view_header.pack_start(self.view_focus, False, False, 0)
        else:
            self.view_object = primary_frame
            self.view_focus = self.wrap_focal_widget(self.view_object)
            self.view_header.pack_start(self.view_focus, False, False, 0)

        self.view_body = self.build_object_groups(groups)

    def build_secondary_frame(self, primary, secondary):
        """
        Build frame for secondary objects.
        """
        build_frame = FRAME_MAP[secondary.obj_type]
        option_space = ".".join(("active", secondary.obj_type.lower()))
        groptions = GrampsOptions(option_space)
        if "Ref" in secondary.obj_type:
            groptions.set_ref_mode(2)
        return build_frame(
            self.grstate,
            groptions,
            primary.obj,
            secondary.obj,
        )
