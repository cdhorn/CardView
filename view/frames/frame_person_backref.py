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
PersonBackRefFrame
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
from .frame_person import PersonFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PersonBackRefFrame Class
#
# ------------------------------------------------------------------------
class PersonBackRefFrame(PersonFrame):
    """
    The PersonBackRefFrame exposes some of the basic facts about an
    Association known through a back reference.
    """

    def __init__(
        self,
        grstate,
        groptions,
        person,
        person_ref,
    ):
        active_person = grstate.fetch("Person", person_ref.ref)
        PersonFrame.__init__(
            self,
            grstate,
            groptions,
            person,
            reference_tuple=(person, person_ref),
        )
        if groptions.ref_mode:
            reference_type = "".join(("[", _("Back Reference"), "]"))
            for active_person_ref in active_person.get_person_ref_list():
                if active_person_ref.ref == person.get_handle():
                    reference_type = "".join(("[", _("Reciprocal"), "]"))
            self.add_ref_item(reference_type, None)
            association = person_ref.get_relation()
            if not association:
                association = _("[None Provided]")
            self.add_ref_item(_("Association"), association)
            relation = grstate.uistate.relationship.get_one_relationship(
                grstate.dbstate.db, person, active_person
            )
            if relation:
                self.add_ref_item(_("Relationship"), relation.capitalize())
            self.show_ref_items()

        self.dnd_drop_ref_targets.append(DdTargets.PERSON_LINK.target())
        self.dnd_drop_ref_targets.append(DdTargets.EVENT.target())
        self.ref_enable_drop(
            self.ref_eventbox,
            self.dnd_drop_ref_targets,
            self.ref_drag_data_received,
        )

    def _ref_child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle child reference specific drop processing.
        """
        if DdTargets.EVENT.drag_type == dnd_type:
            action = action_handler("Person", self.grstate, self.primary)
            action.add_new_event(None, obj_or_handle)
            return True
        if DdTargets.PERSON_LINK.drag_type == dnd_type:
            action = action_handler("Person", self.grstate, self.primary)
            action._add_new_person_reference(obj_or_handle)
            return True
        return self._ref_base_drop_handler(dnd_type, obj_or_handle, data)

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
        if self.grstate.config.get("menu.delete"):
            context_menu.append(
                menu_item(
                    "list-remove",
                    _("Delete reference"),
                    action.remove_person_reference,
                )
            )
