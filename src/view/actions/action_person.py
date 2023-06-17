#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2015-2016  Nick Hall
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
PersonAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import (
    ChildRef,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    Person,
    PersonRef,
)
from gramps.gui.editors import (
    EditEventRef,
    EditFamily,
    EditPerson,
    EditPersonRef,
)
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from .action_base import GrampsAction
from .action_const import RECIPROCAL_ASSOCIATIONS
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PersonAction Class
#
# ------------------------------------------------------------------------
class PersonAction(GrampsAction):
    """
    Class to support actions on or with person objects.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)
        if self.action_object.obj_type != "Person":
            raise AttributeError(
                "action_object is %s not a Person"
                % self.action_object.obj_type
            )

    def goto_person(self, *_dummy_args):
        """
        Request to navigate to person page.
        """
        self.grstate.load_primary_page("Person", self.action_object.obj)

    def _edit_person(self, person, focus=False, callback=None):
        """
        Launch the person editor.
        """
        if focus and callback is None:
            callback = lambda x: self.pivot_focus(x, "Person")
        try:
            EditPerson(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                person,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_person(self, *_dummy_args, focus=False):
        """
        Edit the person.
        """
        self._edit_person(self.action_object.obj, focus=focus)

    def add_existing_event(self, *_dummy_args):
        """
        Add person to existing event.
        """
        get_event_selector = SelectorFactory("Event")
        skip = [x.ref for x in self.action_object.obj.event_ref_list]
        event_selector = get_event_selector(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        event = event_selector.run()
        if event:
            self.add_new_event(None, event_handle=event.handle)

    def add_new_event(self, _dummy_arg=None, event_handle=None):
        """
        Add a new event for a person.
        """
        new_event_ref = EventRef()
        if event_handle:
            for event_ref in self.action_object.obj.event_ref_list:
                if event_ref.ref == event_handle:
                    return
            new_event = self.db.get_event_from_handle(event_handle)
            new_event_ref.ref = event_handle
            new_event_ref.set_role(EventRoleType(EventRoleType.UNKNOWN))
        else:
            new_event = Event()
            new_event_ref.set_role(EventRoleType(EventRoleType.PRIMARY))
        try:
            EditEventRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                new_event,
                new_event_ref,
                self._added_new_event,
            )
        except WindowActiveError:
            pass

    def _added_new_event(self, event_ref, event):
        """
        Finish adding a new event for a person.
        """
        event_ref.ref = event.handle
        message = _("Added Person %s as Participant to Event %s") % (
            self.describe_object(self.action_object.obj),
            self.describe_object(event),
        )
        if event.get_type() == EventType.BIRTH:
            if self.action_object.obj.get_birth_ref() is None:
                self.action_object.obj.set_birth_ref(event_ref)
            else:
                self.action_object.obj.add_event_ref(event_ref)
        elif event.get_type() == EventType.DEATH:
            if self.action_object.obj.get_death_ref() is None:
                self.action_object.obj.set_death_ref(event_ref)
            else:
                self.action_object.obj.add_event_ref(event_ref)
        else:
            self.action_object.obj.add_event_ref(event_ref)
        self.action_object.commit(self.grstate, message)

    def add_new_parents(self, *_dummy_args):
        """
        Add new parents for the person.
        """
        family = Family()
        child_ref = ChildRef()
        child_ref.ref = self.action_object.obj.handle
        family.add_child_ref(child_ref)
        try:
            EditFamily(self.grstate.dbstate, self.grstate.uistate, [], family)
        except WindowActiveError:
            pass

    def add_existing_parents(self, *_dummy_args):
        """
        Add existing parents for the person.
        """
        get_family_selector = SelectorFactory("Family")
        skip = set(self.action_object.obj.family_list)
        family_selector = get_family_selector(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        family = family_selector.run()
        if family:
            self.grstate.dbstate.db.add_child_to_family(
                family, self.action_object.obj
            )

    def add_new_family(self, *_dummy_args):
        """
        Add person as head of a new family.
        """
        family = Family()
        if self.action_object.obj.gender == Person.MALE:
            family.set_father_handle(self.action_object.obj.handle)
        else:
            family.set_mother_handle(self.action_object.obj.handle)
        try:
            EditFamily(self.grstate.dbstate, self.grstate.uistate, [], family)
        except WindowActiveError:
            pass

    def set_main_parents(self, *_dummy_args):
        """
        Set preferred parents.
        """
        message = _("Setting Family %s as Main Parents for Person %s") % (
            self.describe_object(self.target_object.obj),
            self.describe_object(self.action_object.obj),
        )
        self.action_object.obj.set_main_parent_family_handle(
            self.target_object.obj.handle
        )
        self.action_object.commit(self.grstate, message)

    def set_default_person(self, *_dummy_args):
        """
        Set the default person.
        """
        self.grstate.dbstate.db.set_default_person_handle(
            self.action_object.obj.handle
        )

    def set_birth_event(self, *_dummy_args):
        """
        Set as primary birth event.
        """
        if self.target_object.obj_type != "Event":
            raise AttributeError(
                "target_object is %s and not Event"
                % self.target_object.obj_type
            )
        if self.target_object.obj.get_type() != EventType.BIRTH:
            raise AttributeError("target_object not a birth event")
        message = _("Set Event %s as Preferred for Person %s") % (
            self.describe_object(self.target_object.obj),
            self.describe_object(self.action_object.obj),
        )
        birth_ref = EventRef()
        birth_ref.ref = self.target_object.obj.handle
        birth_ref.set_role(EventRoleType(EventRoleType.PRIMARY))
        self.action_object.obj.set_birth_ref(birth_ref)
        self.action_object.commit(self.grstate, message)

    def set_death_event(self, *_dummy_args):
        """
        Set as primary death event.
        """
        if self.target_object.obj_type != "Event":
            raise AttributeError(
                "target_object is %s and not Event"
                % self.target_object.obj_type
            )
        if self.target_object.obj.get_type() != EventType.DEATH:
            raise AttributeError("target_object not a death event")
        message = _("Set Event %s as Preferred for Person %s") % (
            self.describe_object(self.target_object.obj),
            self.describe_object(self.action_object.obj),
        )
        death_ref = EventRef()
        death_ref.ref = self.target_object.obj.handle
        death_ref.set_role(EventRoleType(EventRoleType.PRIMARY))
        self.action_object.obj.set_death_ref(death_ref)
        self.action_object.commit(self.grstate, message)

    def _edit_person_reference(self, person_ref, callback):
        """
        Launch the person reference editor.
        """
        try:
            EditPersonRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                person_ref,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_person_reference(self, *_dummy_args):
        """
        Edit the person reference.
        """
        if self.target_object.obj_type == "Person":
            person_ref = None
            for ref in self.action_object.obj.get_personref_list():
                if ref.ref == self.target_object.obj.handle:
                    person_ref = ref
                    break
            if not person_ref:
                raise AttributeError(
                    "target_object refers to PersonRef that does not exist"
                )
        elif self.target_object.obj_type == "PersonRef":
            person_ref = self.target_object.obj
        else:
            raise AttributeError(
                "target_object is %s not a Person or PersonRef"
                % self.target_object.obj_type
            )
        self._edit_person_reference(person_ref, self._edited_person_reference)

    def _edited_person_reference(self, person_ref):
        """
        Save the person reference.
        """
        if person_ref:
            person = self.db.get_person_from_handle(person_ref.ref)
            message = _(
                "Edited Association for Person %s"
            ) % self.describe_object(person)
            self.action_object.commit(self.grstate, message)

    def add_new_person_reference(self, *_dummy_args):
        """
        Create a new person for the person reference.
        """
        self._edit_person(Person(), self._add_new_person_reference)

    def add_existing_person_reference(self, *_dummy_args):
        """
        Select an existing person for the person reference.
        """
        get_person_selector = SelectorFactory("Person")
        skip = [x.ref for x in self.action_object.obj.person_ref_list]
        skip.append(self.action_object.obj.handle)
        person_selector = get_person_selector(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        person_handle = person_selector.run()
        if person_handle:
            self._add_new_person_reference(person_handle)

    def _add_new_person_reference(self, person_obj_or_handle):
        """
        Add a new person reference aka association.
        """
        if isinstance(person_obj_or_handle, str):
            person_handle = person_obj_or_handle
        else:
            person_handle = person_obj_or_handle.handle
        for person_ref in self.action_object.obj.person_ref_list:
            if person_ref.ref == person_handle:
                return
        ref = PersonRef()
        ref.ref = person_handle
        self._edit_person_reference(ref, self._added_new_person_reference)

    def _added_new_person_reference(self, reference):
        """
        Finish adding a new person reference aka association.
        """
        person = self.db.get_person_from_handle(reference.ref)
        message = _("Added Association from Person %s to Person %s") % (
            self.describe_object(person),
            self.describe_object(self.action_object.obj),
        )
        self.action_object.obj.add_person_ref(reference)
        self.action_object.commit(self.grstate, message)

        if self.grstate.config.get("general.create-reciprocal-associations"):
            ref = PersonRef()
            ref.ref = self.action_object.obj.handle
            ref.set_note_list(reference.note_list)
            ref.set_citation_list(reference.citation_list)
            ref.set_privacy(reference.privacy)
            if reference.get_relation() in RECIPROCAL_ASSOCIATIONS:
                ref.set_relation(
                    RECIPROCAL_ASSOCIATIONS[reference.get_relation()]
                )
            callback = lambda x: self._added_reciprocal_reference(
                x, reference.ref
            )
            self._edit_person_reference(ref, callback)

    def _added_reciprocal_reference(self, reference, reciprocal_handle):
        """
        Finish adding a reciprocal person reference aka association.
        """
        person = GrampsObject(
            self.db.get_person_from_handle(reciprocal_handle)
        )
        message = _("Added Association from Person %s to Person %s") % (
            self.describe_object(self.action_object.obj),
            self.describe_object(person.obj),
        )
        person.obj.add_person_ref(reference)
        person.commit(self.grstate, message)

    def remove_person_reference(self, *_dummy_args):
        """
        Remove a person reference aka association.
        """
        if self.target_object.obj_type == "Person":
            person = self.target_object.obj
        elif self.target_object.obj_type == "PersonRef":
            person = self.db.get_person_from_handle(self.target_object.obj.ref)
        else:
            raise AttributeError(
                "target_object is %s not a Person or PersonRef"
                % self.target_object.obj_type
            )

        message1 = _("Remove Association %s?") % self.describe_object(person)
        message2 = _(
            "Removing the association will remove the person reference "
            "between the people in the database."
        )
        self.verify_action(
            message1,
            message2,
            _("Remove Association"),
            self._remove_person_reference,
            recover_message=False,
        )

    def _remove_person_reference(self, *_dummy_args):
        """
        Actually remove the person association.
        """
        if self.target_object.obj_type == "Person":
            person = self.target_object.obj
        elif self.target_object.obj_type == "PersonRef":
            person = self.db.get_person_from_handle(self.target_object.obj.ref)
        new_list = []
        for ref in self.action_object.obj.person_ref_list:
            if not ref.ref == person.handle:
                new_list.append(ref)
        message = _("Removed Association from Person %s to Person %s") % (
            self.describe_object(person),
            self.describe_object(self.action_object.obj),
        )
        self.action_object.obj.set_person_ref_list(new_list)
        self.action_object.commit(self.grstate, message)


factory.register_action("Person", PersonAction)
