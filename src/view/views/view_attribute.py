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
AttributeObjectView
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
# AttributeObjectView Class
#
# -------------------------------------------------------------------------
class AttributeObjectView(GrampsObjectView):
    """
    Provides the attribute object view.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        base = self.grcontext.primary_obj
        attribute = self.grcontext.secondary_obj
        if self.grcontext.reference_obj:
            base = self.grcontext.reference_obj

        build_frame = FRAME_MAP[base.obj_type]
        option_space = ".".join(("active", base.obj_type.lower()))
        groptions = GrampsOptions(option_space)
        self.view_object = build_frame(self.grstate, groptions, base.obj)

        groptions = GrampsOptions("active.attribute")
        self.view_focus = self.wrap_focal_widget(
            FRAME_MAP["Attribute"](
                self.grstate, groptions, base.obj, attribute.obj
            )
        )

        self.view_header.pack_start(self.view_object, False, False, 0)
        self.view_header.pack_start(self.view_focus, False, False, 0)

        self.view_body = self.build_object_groups(attribute)
