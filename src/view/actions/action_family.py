#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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
FamilyAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
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
    Name,
    Person,
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
# Plugin Modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# FamilyAction Class
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

    def edit_family(self, *_dummy_args, focus=False, callback=None):
        """
        Edit the family.
        """
        if focus and callback is None:
            callback = lambda x: self.pivot_focus(x, "Family")
        try:
            EditFamily(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
                callback,
            )
        except WindowActiveError:
            pass

    def add_new_event(self, _dummy_arg=None, event_handle=None):
        """
        Add a new event for a family.
        """
        new_event_ref = EventRef()
        if event_handle:
            for event_ref in self.action_object.obj.event_ref_list:
                if event_ref.ref == event_handle:
                    return
            event = self.db.get_event_from_handle(event_handle)
            new_event_ref.ref = event_handle
        else:
            new_event = Event()
            new_event.set_type(EventType(EventType.MARRIAGE))
        new_event_ref.set_role(EventRoleType(EventRoleType.FAMILY))
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
        Finish adding a new event for a family.
        """
        event_ref.ref = event.handle
        message = _("Added Family %s to Event %s") % (
            self.describe_object(self.action_object.obj),
            self.describe_object(event),
        )
        self.action_object.obj.add_event_ref(event_ref)
        self.action_object.commit(self.grstate, message)

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
            name, self.target_object.obj, self._edited_child_reference
        )

    def _edited_child_reference(self, child_ref):
        """
        Save edited child reference.
        """
        if child_ref:
            child = self.db.get_person_from_handle(child_ref.ref)
            message = _(
                "Edited Child Reference for %s"
            ) % self.describe_object(child)
            self.action_object.commit(self.grstate, message)

    def add_new_child(self, *_dummy_args):
        """
        Add a new child to a family. First create the person.
        """
        child = Person()
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)
        father_handle = self.action_object.obj.father_handle
        if father_handle:
            parent = self.db.get_person_from_handle(father_handle)
        else:
            mother_handle = self.action_object.obj.mother_handle
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
        child_ref.ref = child.handle
        callback = lambda x: self._added_child(child_ref, child)
        name = self.describe_object(child)
        self._edit_child_reference(name, child_ref, callback)

    def _added_child(self, child_ref, child):
        """
        Finish adding the child to the family.
        """
        message = _("Added Child %s to Family %s") % (
            self.describe_object(child),
            self.describe_object(self.action_object.obj),
        )
        self.grstate.uistate.set_busy_cursor(True)
        with DbTxn(message, self.db) as trans:
            self.action_object.obj.add_child_ref(child_ref)
            self.db.commit_family(self.action_object.obj, trans)
            child.add_parent_family_handle(self.action_object.obj.handle)
            self.db.commit_person(child, trans)
        self.grstate.uistate.set_busy_cursor(False)

    def add_existing_child(self, *_dummy_args):
        """
        Add the child to the family. First select the person.
        """
        family = self.action_object.obj
        get_person_selector = SelectorFactory("Person")
        skip_list = [family.father_handle, family.mother_handle]
        skip_list.extend(x.ref for x in family.child_ref_list)
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
        for child_ref in self.action_object.obj.child_ref_list:
            if child_ref.ref == person.handle:
                found = True
                break
        if found:
            person_name = self.describe_object(person)
            family_text = self.describe_object(self.action_object.obj)

            message1 = _("Remove Child %s?") % person_name
            message2 = (
                _(
                    "Removing the child will remove the child reference "
                    "from the family %s in the database."
                )
                % family_text
            )
            self.verify_action(
                message1,
                message2,
                _("Remove Child"),
                self._remove_child_reference,
                recover_message=False,
            )

    def _remove_child_reference(self, *_dummy_args):
        """
        Actually remove the child reference.
        """
        if self.target_object.obj_type == "Person":
            person = self.target_object.obj
        elif self.target_object.obj_type == "ChildRef":
            person = self.db.get_person_from_handle(self.target_object.obj)
        self.grstate.uistate.set_busy_cursor(True)
        self.db.remove_child_from_family(
            person.handle, self.action_object.obj.handle
        )
        self.grstate.uistate.set_busy_cursor(False)

    def add_missing_spouse(self, *_dummy_args):
        """
        Add missing spouse for the family.
        """
        if self.target_object.obj_type != "Person":
            raise AttributeError(
                "target_object is %s not a Person"
                % self.target_object.obj_type
            )
        spouse_handle = self.target_object.obj.handle
        if not self.action_object.obj.father_handle:
            self.action_object.obj.set_father_handle(spouse_handle)
        elif not self.action_object.obj.mother_handle:
            self.action_object.obj.set_mother_handle(spouse_handle)
        else:
            return
        self.edit_family()

    def _remove_partner(self, partner):
        """
        Confirm and remove partner from family.
        """
        person_name = self.describe_object(partner)
        message1 = _("Remove Partner %s?") % person_name
        message2 = _(
            "Removing the partner or spouse will remove the person from "
            "the family in the database."
        )
        callback = lambda x: self._removing_partner(partner)
        self.verify_action(
            message1,
            message2,
            _("Remove Partner"),
            callback,
            recover_message=False,
        )

    def _removing_partner(self, partner):
        """
        Actually remove the partner from the family.
        """
        self.grstate.uistate.set_busy_cursor(True)
        self.db.remove_parent_from_family(
            partner.handle, self.action_object.obj.handle
        )
        self.grstate.uistate.set_busy_cursor(False)

    def remove_partner(self, *_dummy_args):
        """
        Remove a partner from a family.
        """
        if self.target_object.obj_type != "Person":
            raise AttributeError(
                "target_object is %s not a Person"
                % self.target_object.obj_type
            )
        parent_handle = self.target_object.obj.handle
        father_handle = self.action_object.obj.father_handle
        mother_handle = self.action_object.obj.mother_handle
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
        spouse_handle = self.target_object.obj.handle
        father_handle = self.action_object.obj.father_handle
        mother_handle = self.action_object.obj.mother_handle
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
        message = _("Setting Family %s as Main Parents for Person %s") % (
            self.describe_object(self.action_object.obj),
            self.describe_object(self.target_object.obj),
        )
        self.target_object.obj.set_main_parent_family_handle(
            self.action_object.obj.handle
        )
        self.target_object.commit(self.grstate, message)


factory.register_action("Family", FamilyAction)
