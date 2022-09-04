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
StatisticsObjectView
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..cards import FamilyTreeCard
from ..common.common_classes import GrampsOptions
from ..groups.group_builder import group_builder
from .view_base import GrampsObjectView


# -------------------------------------------------------------------------
#
# StatisticsView Class
#
# -------------------------------------------------------------------------
class StatisticsObjectView(GrampsObjectView):
    """
    Provides the statistics view.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        groptions = GrampsOptions("active.tree")
        self.view_object = FamilyTreeCard(self.grstate, groptions)
        self.view_focus = self.wrap_focal_widget(self.view_object)
        self.view_header.pack_start(self.view_focus, False, False, 0)
        self.view_body = self.build_statistics_groups()

    def build_statistics_groups(self):
        """
        Gather and build the statistics groups.
        """
        groups = self.grstate.config.get("layout.statistics.groups").split(",")

        object_groups = {}
        for group in groups:
            if self.grstate.config.get("layout.statistics.%s.visible" % group):
                object_groups.update(
                    {group: group_builder(self.grstate, group, None, None)}
                )
        return self.render_group_view(
            object_groups, space_override="layout.statistics"
        )
