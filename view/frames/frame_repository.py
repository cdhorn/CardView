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
RepositoryFrame
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
from ..actions import action_handler
from ..common.common_utils import format_address
from .frame_reference import ReferenceFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# RepositoryFrame Class
#
# ------------------------------------------------------------------------
class RepositoryFrame(ReferenceFrame):
    """
    The RepositoryFrame exposes some of the basic facts about a
    Repository.
    """

    def __init__(self, grstate, groptions, repository, reference_tuple=None):
        ReferenceFrame.__init__(
            self,
            grstate,
            groptions,
            repository,
            reference_tuple=reference_tuple,
        )
        self.__add_repository_title(repository)
        self.__add_repository_address(repository)
        self.__add_repository_type(repository)
        self.enable_drag()
        self.dnd_drop_targets.append(DdTargets.SOURCE_LINK.target())
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_repository_title(self, repository):
        """
        Add repository title.
        """
        title = self.get_link(
            repository.name,
            "Repository",
            repository.get_handle(),
        )
        self.widgets["title"].pack_start(title, True, False, 0)

    def __add_repository_address(self, repository):
        """
        Add repository address.
        """
        address_list = repository.get_address_list()
        if address_list:
            address = address_list[0]
            lines = format_address(address)
            for line in lines:
                self.add_fact(self.get_label(line))
            if address.phone:
                self.add_fact(self.get_label(address.phone))

    def __add_repository_type(self, repository):
        """
        Add repository type.
        """
        if self.get_option("show-repository-type") and repository.get_type():
            label = self.get_label(str(repository.get_type()), left=False)
            self.widgets["attributes"].add_fact(label)

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a repository.
        """
        if DdTargets.SOURCE_LINK.drag_type == dnd_type:
            source = self.fetch("Source", obj_or_handle)
            action = action_handler(
                "Repository", self.grstate, self.primary, source
            )
            action.add_new_source()
            return True
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)
