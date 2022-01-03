#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
SourceFrame.
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.ddtargets import DdTargets

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..actions import SourceAction
from .frame_primary import PrimaryFrame
from ..menus.menu_utils import add_repositories_menu

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
            source.get_handle(),
        )
        self.widgets["title"].pack_start(title, True, False, 0)

    def __add_source_author(self, source):
        """
        Add source author.
        """
        if source.get_author():
            self.add_fact(self.get_label(source.get_author()))

    def __add_source_publisher(self, source):
        """
        Add source publisher.
        """
        if source.get_publication_info():
            self.add_fact(self.get_label(source.get_publication_info()))

    def __add_source_abbrev(self, source):
        """
        Add source abbreviation.
        """
        if source.get_abbreviation():
            self.add_fact(self.get_label(source.get_abbreviation()))

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        if DdTargets.REPO_LINK.drag_type == dnd_type:
            action = SourceAction(self.grstate, self.primary)
            action.add_new_repository_reference(obj_or_handle)
            return True
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def add_custom_actions(self, context_menu):
        """
        Add action menu items for the source.
        """
        add_repositories_menu(self.grstate, context_menu, self.primary)
