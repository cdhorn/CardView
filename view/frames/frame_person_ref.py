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
PersonRefFrame
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
# PersonRefFrame class
#
# ------------------------------------------------------------------------
class PersonRefFrame(PersonFrame):
    """
    The PersonRefFrame exposes some of the basic facts about an
    Association.
    """

    def __init__(
        self,
        grstate,
        groptions,
        person,
        person_ref,
    ):
        associate = grstate.fetch("Person", person_ref.ref)
        PersonFrame.__init__(
            self,
            grstate,
            groptions,
            associate,
            reference_tuple=(person, person_ref),
        )
        if groptions.ref_mode:
            association = person_ref.get_relation()
            if not association:
                association = _("[None Provided]")
            self.add_ref_item(_("Association"), association)
            relation = grstate.uistate.relationship.get_one_relationship(
                grstate.dbstate.db, person, associate
            )
            if relation:
                self.add_ref_item(_("Relationship"), relation.capitalize())
            self.show_ref_items()

    def add_ref_custom_actions(self, context_menu):
        """
        Add custom action menu items for an associate.
        """
        action = action_handler(
            "Person", self.grstate, self.primary, self.reference
        )
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(
            menu_item("gtk-edit", label, action.edit_person_reference)
        )
        label = " ".join((_("Delete"), _("reference")))
        context_menu.append(
            menu_item(
                "list-remove",
                label,
                action.remove_person_reference,
            )
        )
