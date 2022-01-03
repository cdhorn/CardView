#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
FamilyAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import (
    ChildRef,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Person,
    Name,
    Surname,
)
from gramps.gen.utils.db import preset_name
from gramps.gui.editors import (
    EditChildRef,
    EditEventRef,
    EditFamily,
    EditPerson,
)
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# FamilyAction class
#
# ------------------------------------------------------------------------
class FamilyAction(GrampsAction):
    """
    Class to support actions on or with family objects.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)
        if self.action_object.obj_type != "Family":
            raise AttributeError(
                "action_object is %s and not Family"
                % self.action_object.obj_type
            )

    def edit_family(self, *_dummy_args):
        """
        Edit the family.
        """
        try:
            EditFamily(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
            )
        except WindowActiveError:
            pass

    def add_new_event(self, _dummy_arg=None, event_handle=None):
        """
        Add a new event for a family.
        """
        event_ref = EventRef()
        if event_handle:
            for event_ref in self.action_object.obj.get_event_ref_list():
                if event_ref.ref == event_handle:
                    return
            event = self.db.get_event_from_handle(event_handle)
            event_ref.ref = event_handle
        else:
            event = Event()
            event.set_type(EventType(EventType.MARRIAGE))
        event_ref.set_role(EventRoleType(EventRoleType.FAMILY))
        try:
            EditEventRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                event,
                event_ref,
                self._added_new_event,
            )
        except WindowActiveError:
            pass

    def _added_new_event(self, event_ref, event):
        """
        Finish adding a new event for a family.
        """
        event_ref.ref = event.get_handle()
        message = " ".join(
            (
                _("Added"),
                _("Family"),
                self.action_object.obj.get_gramps_id(),
                _("to"),
                _("Event"),
                event.get_gramps_id(),
            )
        )
        with DbTxn(message, self.db) as trans:
            self.db.commit_event(event, trans)
            self.action_object.obj.add_event_ref(event_ref)
            self.db.commit_family(self.action_object.obj, trans)

    def _edit_child_reference(self, name, child_ref, callback=None):
        """
        Launch child reference editor.
        """
        try:
            EditChildRef(
                name,
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                child_ref,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_child_reference(self, *_dummy_args):
        """
        Edit the child reference.
        """
        if self.target_object.obj_type != "ChildRef":
            raise AttributeError(
                "target_object is %s not a Person or ChildRef"
                % self.target_object.obj_type
            )
        child = self.db.get_person_from_handle(self.target_object.obj.ref)
        name = self.describe_object(child)
        self._edit_child_reference(
            name, self.target_object.obj.ref, self._edited_child_reference
        )

    def _edited_child_reference(self, child_ref):
        """
        Save edited child reference.
        """
        if child_ref:
            child = self.db.get_person_from_handle(child_ref.ref)
            message = self.commit_message(
                _("ChildRef"), child.get_gramps_id(), action="update"
            )
            self.action_object.commit(self.grstate, message)

    def add_new_child(self, *_dummy_args):
        """
        Add a new child to a family. First create the person.
        """
        child = Person()
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)
        father_handle = self.action_object.obj.get_father_handle()
        if father_handle:
            parent = self.db.get_person_from_handle(father_handle)
        else:
            mother_handle = self.action_object.obj.get_mother_handle()
            if mother_handle:
                parent = self.db.get_person_from_handle(mother_handle)
        if parent:
            preset_name(parent, name)
        child.set_primary_name(name)
        try:
            EditPerson(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                child,
                callback=self._adding_child,
            )
        except WindowActiveError:
            pass

    def _adding_child(self, child):
        """
        Second set parental relations.
        """
        child_ref = ChildRef()
        child_ref.ref = child.get_handle()
        callback = lambda x: self._added_child(x, child)
        name = self.describe_object(child)
        self._edit_child_reference(name, child_ref, callback)

    def _added_child(self, child_ref, child):
        """
        Finish adding the child to the family.
        """
        message = " ".join(
            (
                _("Added"),
                _("Child"),
                child.get_gramps_id(),
                _("to"),
                _("Family"),
                self.action_object.obj.get_gramps_id(),
            )
        )
        with DbTxn(message, self.db) as trans:
            self.action_object.obj.add_child_ref(child_ref)
            self.db.commit_family(self.action_object.obj, trans)
            child.add_parent_family_handle(self.action_object.obj.get_handle())
            self.db.commit_person(child, trans)

    def add_existing_child(self, *_dummy_args):
        """
        Add the child to the family. First select the person.
        """
        family = self.action_object.obj
        get_person_selector = SelectorFactory("Person")
        skip_list = [family.get_father_handle(), family.get_mother_handle()]
        skip_list.extend(x.ref for x in family.get_child_ref_list())
        person_selector = get_person_selector(
            self.grstate.dbstate,
            self.grstate.uistate,
            [],
            _("Select Child"),
            skip=skip_list,
        )
        child = person_selector.run()
        if child:
            self._adding_child(child)

    def remove_child(self, *_dummy_args):
        """
        Remove a child from the family.
        """
        if self.target_object.obj_type == "Person":
            person = self.target_object.obj
        elif self.target_object.obj_type == "ChildRef":
            person = self.db.get_person_from_handle(self.target_object.obj)
        else:
            raise AttributeError(
                "target_object is %s not a Person or ChildRef"
            )
        found = False
        for child_ref in self.action_object.obj.get_child_ref_list():
            if child_ref.ref == person.get_handle():
                found = True
                break
        if found:
            person_name = self.describe_object(person)
            family_text = self.describe_object(self.action_object.obj)
            message = " ".join(
                (
                    _("You are about to remove"),
                    person_name,
                    "from the family of",
                    family_text,
                    ".",
                )
            )
            if self.confirm_action(_("Warning"), message):
                self.db.remove_child_from_family(
                    person.get_handle(), self.action_object.obj.get_handle()
                )

    def add_missing_spouse(self, *_dummy_args):
        """
        Add missing spouse for the family.
        """
        if self.target_object.obj_type != "Person":
            raise AttributeError(
                "target_object is %s not a Person"
                % self.target_object.obj_type
            )
        spouse_handle = self.target_object.obj.get_handle()
        if not self.action_object.obj.get_father_handle():
            self.action_object.obj.set_father_handle(spouse_handle)
        elif not self.action_object.obj.get_mother_handle():
            self.action_object.obj.set_mother_handle(spouse_handle)
        else:
            return
        self.edit_family()

    def _remove_partner(self, partner):
        """
        Confirm and remove partner from family.
        """
        person_name = self.describe_object(partner)
        message = " ".join(
            (
                _("You are about to remove"),
                person_name,
                _("as a parent of this family."),
            )
        )
        if self.confirm_action(_("Warning"), message):
            self.db.remove_parent_from_family(
                partner.get_handle(), self.action_object.obj.get_handle()
            )

    def remove_partner(self, *_dummy_args):
        """
        Remove a partner from a family.
        """
        if self.target_object.obj_type != "Person":
            raise AttributeError(
                "target_object is %s not a Person"
                % self.target_object.obj_type
            )
        parent_handle = self.target_object.obj.get_handle()
        father_handle = self.action_object.obj.get_father_handle()
        mother_handle = self.action_object.obj.get_mother_handle()
        if parent_handle in [father_handle, mother_handle]:
            self._remove_partner(self.target_object.obj)

    def remove_spouse(self, *_dummy_args):
        """
        Remove a spouse from a family.
        """
        if self.target_object.obj_type != "Person":
            raise AttributeError(
                "target_object is %s not a Person"
                % self.target_object.obj_type
            )
        spouse_handle = self.target_object.obj.get_handle()
        father_handle = self.action_object.obj.get_father_handle()
        mother_handle = self.action_object.obj.get_mother_handle()
        if spouse_handle in [father_handle, mother_handle]:
            partner = None
            if spouse_handle == father_handle and mother_handle:
                partner = self.db.get_person_from_handle(mother_handle)
            elif spouse_handle == mother_handle and father_handle:
                partner = self.db.get_person_from_handle(father_handle)
            if partner:
                self._remove_partner(partner)

    def set_main_parents(self, *_dummy_args):
        """
        Set preferred parents.
        """
        message = " ".join(
            (
                _("Setting"),
                _("Family"),
                self.action_object.obj.get_gramps_id(),
                _("as"),
                _("Main"),
                _("Parents"),
                _("for"),
                _("Person"),
                self.target_object.obj.get_gramps_id(),
            )
        )
        self.target_object.obj.set_main_parent_family_handle(
            self.action_object.obj.get_handle()
        )
        self.target_object.commit(self.grstate, message)


factory.register_action("Family", FamilyAction)
