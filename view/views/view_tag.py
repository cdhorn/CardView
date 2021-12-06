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
TagObjectView
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from ..groups.group_builder import get_references_group
from .view_base import GrampsObjectView
from .view_const import FRAME_MAP


class TagObjectView(GrampsObjectView):
    """
    Provides the tag object view.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        tag = self.grcontext.primary_obj.obj

        groptions = GrampsOptions("options.active.tag")
        self.view_object = FRAME_MAP["Tag"](self.grstate, groptions, tag)
        self.view_focus = self.wrap_focal_widget(self.view_object)
        self.view_header.pack_start(self.view_focus, False, False, 0)

        object_list = {}
        for (
            obj_type,
            obj_handle,
        ) in self.grstate.dbstate.db.find_backlink_handles(tag.get_handle()):
            if obj_type not in object_list:
                object_list.update({obj_type: []})
            object_list[obj_type].append((obj_type, obj_handle))

        object_groups = {}
        if object_list:
            for key, value in object_list.items():
                groptions = GrampsOptions(
                    "options.group.{}".format(key.lower())
                )
                object_groups.update(
                    {
                        key.lower(): get_references_group(
                            self.grstate,
                            None,
                            None,
                            groptions=groptions,
                            obj_list=value,
                        )
                    }
                )
        self.view_body = self.render_group_view(object_groups)
