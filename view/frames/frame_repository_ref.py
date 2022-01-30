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
RepositoryRefFrame
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
from ..menus.menu_utils import menu_item
from .frame_repository import RepositoryFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# RepositoryRefFrame Class
#
# ------------------------------------------------------------------------
class RepositoryRefFrame(RepositoryFrame):
    """
    The RepositoryRefFrame exposes some of the basic facts about a
    Repository and the reference to it.
    """

    def __init__(self, grstate, groptions, source, repo_ref=None):
        repository = grstate.fetch("Repository", repo_ref.ref)
        RepositoryFrame.__init__(
            self,
            grstate,
            groptions,
            repository,
            reference_tuple=(source, repo_ref),
        )
        if groptions.ref_mode:
            if self.get_option("show-call-number") and repo_ref.call_number:
                self.add_ref_item(_("Call number"), repo_ref.call_number)
            if self.get_option("show-media-type") and repo_ref.media_type:
                media_type = glocale.translation.sgettext(
                    repo_ref.media_type.xml_str()
                )
                self.add_ref_item(_("Media type"), media_type)
            self.show_ref_items()

        self.dnd_drop_targets.append(DdTargets.SOURCE_LINK.target())
        self.ref_enable_drop(
            self.ref_eventbox,
            self.dnd_drop_ref_targets,
            self.ref_drag_data_received,
        )

    def _ref_child_drop_handler(self, dnd_type, obj_or_handle, data):
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
        return self._ref_base_drop_handler(dnd_type, obj_or_handle, data)

    def add_ref_custom_actions(self, context_menu):
        """
        Build the action menu for a right click on a reference object.
        """
        action = action_handler(
            "Source", self.grstate, self.reference_base, self.reference
        )
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(
            menu_item("gtk-edit", label, action.edit_repository_reference)
        )
        if self.grstate.config.get("menu.delete"):
            label = " ".join((_("Delete"), _("reference")))
            context_menu.append(
                menu_item(
                    "list-remove", label, action.remove_repository_reference
                )
            )
