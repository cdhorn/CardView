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
DashboardObjectView
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..groups.group_builder import group_builder
from .view_base import GrampsObjectView


# -------------------------------------------------------------------------
#
# DashboardView Class
#
# -------------------------------------------------------------------------
class DashboardObjectView(GrampsObjectView):
    """
    Provides the dashboard view.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        self.view_object = None
        self.view_focus = None
        self.view_body = self.build_dashboard_groups()

    def build_dashboard_groups(self):
        """
        Gather and build the dashboard groups.
        """
        groups = self.grstate.config.get("layout.dashboard.groups").split(",")

        object_groups = {}
        for group in groups:
            if self.grstate.config.get("layout.dashboard.%s.visible" % group):
                object_groups.update(
                    {group: group_builder(self.grstate, group, None, None)}
                )
        return self.render_group_view(object_groups)
