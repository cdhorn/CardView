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
EventAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import EventRef, EventRoleType, Person
from gramps.gui.editors import EditEvent, EditEventRef, EditPerson
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# EventAction Class
#
# ------------------------------------------------------------------------
class EventAction(GrampsAction):
    """
    Class to support actions related to events.
    """

    def __init__(self, grstate, action_object, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)
        if self.action_object.obj_type != "Event":
            raise AttributeError(
                "action_object is %s not an Event"
                % self.action_object.obj_type
            )

    def edit_event(self, *_dummy_args, focus=False, callback=None):
        """
        Launch the event editor.
        """
        if focus and callback is None:
            callback = lambda x: self.pivot_focus(x, "Event")
        try:
            EditEvent(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
                callback,
            )
        except WindowActiveError:
            pass

    def _edit_participant(self, callback=None):
        """
        Edit the event participant refererence.
        """
        if self.target_object.obj_type not in ["Person", "Family"]:
            raise AttributeError(
                "target_object is %s not a Person or Family"
                % self.target_object.obj_type
            )
        event_ref = None
        for event_ref in self.target_object.obj.get_event_ref_list():
            if event_ref.ref == self.action_object.obj.get_handle():
                break
        if event_ref:
            try:
                EditEventRef(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    self.action_object.obj,
                    event_ref,
                    callback,
                )
            except WindowActiveError:
                pass

    def edit_participant(self, *_dummy_args):
        """
        Edit the participant event reference.
        """
        self._edit_participant(callback=self._edited_participant)

    def _edited_participant(self, event_ref):
        """
        Save the event participant.
        """
        if event_ref:
            message = _("Edited Participant %s in Event %s") % (
                self.describe_object(self.target_object.obj),
                self.describe_object(self.action_object.obj),
            )
            self.target_object.obj.add_event_ref(event_ref)
            self.target_object.commit(self.grstate, message)

    def add_new_participant(self, *_dummy_args):
        """
        Add a new person as participant to an event.
        """
        self.set_target_object(Person())
        event_ref = EventRef()
        event_ref.ref = self.action_object.obj.get_handle()
        event_ref.set_role(EventRoleType(EventRoleType.UNKNOWN))
        self.target_object.obj.add_event_ref(event_ref)
        try:
            EditPerson(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.target_object.obj,
                callback=self.edit_participant,
            )
        except WindowActiveError:
            pass

    def add_existing_participant(self, *_dummy_arg, person_handle=None):
        """
        Add an existing person as participant to an event.
        """
        if person_handle:
            participant = self.db.get_person_from_handle(person_handle)
        else:
            get_person_selector = SelectorFactory("Person")
            person_selector = get_person_selector(
                self.grstate.dbstate, self.grstate.uistate
            )
            participant = person_selector.run()
        if participant:
            event_ref = EventRef()
            event_ref.ref = self.action_object.obj.get_handle()
            event_ref.set_role(EventRoleType(EventRoleType.UNKNOWN))
            self.set_target_object(participant)
            self.target_object.obj.add_event_ref(event_ref)
            self._edit_participant(self._added_participant)

    def _added_participant(self, event_ref):
        """
        Save the added participant.
        """
        if event_ref:
            message = _("Added Participant %s to Event %s") % (
                self.describe_object(self.target_object.obj),
                self.describe_object(self.action_object.obj),
            )
            self.target_object.obj.add_event_ref(event_ref)
            self.target_object.commit(self.grstate, message)

    def remove_participant(self, *_dummy_args):
        """
        Remove a participant from an event.
        """
        if self.target_object.obj_type not in ["Person", "Family"]:
            raise AttributeError(
                "target_object is %s not a Person or Family"
                % self.target_object.obj_type
            )

        participant = self.target_object
        new_list = []
        found_event_ref = None
        for event_ref in participant.obj.get_event_ref_list():
            if event_ref.ref == self.action_object.obj.get_handle():
                found_event_ref = event_ref
            else:
                new_list.append(event_ref)

        if found_event_ref:
            message1 = _("Remove Participant %s?") % self.describe_object(
                participant.obj
            )
            message2 = _(
                "Removing the participant will remove their event "
                "reference."
            )
            self.verify_action(
                message1,
                message2,
                _("Remove Participant"),
                self._remove_participant,
                recover_message=False,
            )

    def _remove_participant(self, *_dummy_args):
        """
        Actually remove the participant from the event.
        """
        new_list = []
        participant = self.target_object
        for event_ref in participant.obj.get_event_ref_list():
            if event_ref.ref != self.action_object.obj.get_handle():
                new_list.append(event_ref)
        message = _("Removed Participant %s from Event %s") % (
            self.describe_object(participant.obj),
            self.describe_object(self.action_object.obj),
        )
        birth_ref = participant.obj.get_birth_ref()
        death_ref = participant.obj.get_death_ref()
        participant.obj.set_event_ref_list(new_list)
        if birth_ref is not None:
            if birth_ref.ref != self.action_object.obj.get_handle():
                participant.obj.set_birth_ref(birth_ref)
            else:
                participant.obj.set_birth_ref(None)
            if death_ref is not None:
                if death_ref.ref != self.action_object.obj.get_handle():
                    participant.obj.set_death_ref(death_ref)
                else:
                    participant.obj.set_death_ref(None)
            participant.commit(self.grstate, message)


factory.register_action("Event", EventAction)
