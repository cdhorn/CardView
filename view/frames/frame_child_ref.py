#
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
ChildRefFrame
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..menus.menu_utils import menu_item
from .frame_person import PersonFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# ChildRefFrame class
#
# ------------------------------------------------------------------------
class ChildRefFrame(PersonFrame):
    """
    The ChildRefFrame exposes some of the basic facts about a Child.
    """

    def __init__(
        self,
        grstate,
        groptions,
        family,
        child_ref,
    ):
        child = grstate.fetch("Person", child_ref.ref)
        PersonFrame.__init__(
            self,
            grstate,
            groptions,
            child,
            reference_tuple=(family, child_ref),
        )
        if groptions.ref_mode:
            if child_ref.get_father_relation():
                relation_type = str(child_ref.get_father_relation())
                self.add_ref_item(_("Father"), relation_type)
            if child_ref.get_mother_relation():
                relation_type = str(child_ref.get_mother_relation())
                self.add_ref_item(_("Mother"), relation_type)
            self.show_ref_items()

    def add_ref_custom_actions(self, context_menu):
        """
        Build the action menu for a right click on a reference object.
        """
        action = action_handler(
            "Family", self.grstate, self.reference_base, self.reference
        )
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(
            menu_item("gtk-edit", label, action.edit_child_reference)
        )
        label = " ".join((_("Delete"), _("reference")))
        context_menu.append(
            menu_item("list-remove", label, action.remove_child)
        )
