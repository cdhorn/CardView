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
    Provides an object view that handles basic primary and secondary objects.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """

        def build_frame(gramps_obj):
            """
            Build frame for an object.
            """
            frame = FRAME_MAP[gramps_obj.obj_type]
            option = ".".join(("options.active", gramps_obj.obj_type.lower()))
            groptions = GrampsOptions(option)
            return frame(self.grstate, groptions, gramps_obj.obj)

        self.view_object = build_frame(self.grcontext.primary_obj)

        if self.grcontext.secondary_obj:
            self.view_focus = self.wrap_focal_widget(
                build_frame(self.grcontext.secondary_obj)
            )
            self.view_header.pack_start(self.view_object, False, False, 0)
            self.view_body = self.build_object_groups(
                self.grcontext.secondary_obj
            )
        else:
            self.view_focus = self.wrap_focal_widget(self.view_object)
            if hasattr(self.grcontext.primary_obj.obj, "get_date_object"):
                age_base = self.grcontext.primary_obj.obj.get_date_object()
            else:
                age_base = None
            self.view_body = self.build_object_groups(
                self.grcontext.primary_obj, age_base=age_base
            )

        self.view_header.pack_start(self.view_focus, False, False, 0)
