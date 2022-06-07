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
EventRefFrame.
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.utils.db import family_name
from gramps.gui.ddtargets import DdTargets

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..menus.menu_utils import menu_item
from .frame_event import EventFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# EventRefFrame Class
#
# ------------------------------------------------------------------------
class EventRefFrame(EventFrame):
    """
    The EventRefFrame exposes some of the basic facts about an Event
    for a Person or Family
    """

    def __init__(self, grstate, groptions, obj, event_ref):
        event = grstate.fetch("Event", event_ref.ref)
        reference_tuple = (obj, event_ref)
        EventFrame.__init__(
            self, grstate, groptions, event, reference_tuple=reference_tuple
        )
        if groptions.ref_mode:
            role = str(event_ref.get_role())
            if (
                groptions.relation
                and groptions.relation.handle != self.reference_base.obj.handle
            ):
                name = None
                if self.reference_base.obj_type == "Person":
                    name = name_displayer.display(self.reference_base.obj)
                elif self.reference_base.obj_type == "Family":
                    name = family_name(
                        self.reference_base.obj, grstate.dbstate.db
                    )
                if name:
                    self.add_ref_item(name, role)
            else:
                self.add_ref_item(role, None)
            self.show_ref_items()

        self.dnd_drop_ref_targets.append(DdTargets.PERSON_LINK.target())
        self.ref_enable_drop(
            self.ref_eventbox,
            self.dnd_drop_ref_targets,
            self.ref_drag_data_received,
        )

    def _ref_child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle child reference specific drop processing.
        """
        if DdTargets.PERSON_LINK.drag_type == dnd_type:
            action = action_handler("Event", self.grstate, self.primary)
            action.add_existing_participant(person_handle=obj_or_handle)
            return True
        return self._ref_base_drop_handler(dnd_type, obj_or_handle, data)

    def add_ref_custom_actions(self, context_menu):
        """
        Add custom action menu items for the event reference.
        """
        action = action_handler(
            "Event", self.grstate, self.primary, self.reference_base
        )
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(
            menu_item("gtk-edit", label, action.edit_participant)
        )
        if self.grstate.config.get("menu.delete"):
            context_menu.append(
                menu_item(
                    "list-remove",
                    _("Delete reference"),
                    action.remove_participant,
                )
            )
