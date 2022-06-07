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
SourceFrame
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.ddtargets import DdTargets

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..menus.menu_utils import add_repositories_menu
from .frame_primary import PrimaryFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# SourceFrame Class
#
# ------------------------------------------------------------------------
class SourceFrame(PrimaryFrame):
    """
    The SourceFrame exposes some of the basic facts about a Source.
    """

    def __init__(self, grstate, groptions, source):
        PrimaryFrame.__init__(self, grstate, groptions, source)
        self.__add_source_title(source)
        self.__add_source_author(source)
        self.__add_source_publisher(source)
        self.__add_source_abbrev(source)
        self.enable_drag()
        self.dnd_drop_targets.append(DdTargets.REPO_LINK.target())
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_source_title(self, source):
        """
        Add source title.
        """
        title = self.get_link(
            source.title,
            "Source",
            source.handle,
        )
        self.widgets["title"].pack_start(title, True, False, 0)

    def __add_source_author(self, source):
        """
        Add source author.
        """
        if source.author:
            self.add_fact(self.get_label(source.author))

    def __add_source_publisher(self, source):
        """
        Add source publisher.
        """
        if source.pubinfo:
            self.add_fact(self.get_label(source.pubinfo))

    def __add_source_abbrev(self, source):
        """
        Add source abbreviation.
        """
        if source.abbrev:
            self.add_fact(self.get_label(source.abbrev))

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        if DdTargets.REPO_LINK.drag_type == dnd_type:
            action = action_handler("Source", self.grstate, self.primary)
            action.add_new_repository_reference(obj_or_handle)
            return True
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def add_custom_actions(self, context_menu):
        """
        Add action menu items for the source.
        """
        add_repositories_menu(self.grstate, context_menu, self.primary)
