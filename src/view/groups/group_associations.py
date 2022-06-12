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
AssociationsCardGroup
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import PersonRef
from gramps.gui.editors import EditPersonRef

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..cards import PersonBackRefCard, PersonRefCard
from .group_list import CardGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AssociationsCardGroup Class
#
# ------------------------------------------------------------------------
class AssociationsCardGroup(CardGroupList):
    """
    The AssociationsCardGroup class provides a container for managing
    all of the associations a person has with other people.
    """

    def __init__(self, grstate, groptions, obj):
        CardGroupList.__init__(self, grstate, groptions, obj)
        groptions.set_ref_mode(
            self.grstate.config.get("group.association.reference-mode")
        )
        back_list = [
            y
            for (x, y) in grstate.dbstate.db.find_backlink_handles(
                obj.handle, ["Person"]
            )
        ]

        for person_ref in obj.person_ref_list:
            card = PersonRefCard(
                grstate,
                groptions,
                obj,
                person_ref,
            )
            self.add_card(card)
            if person_ref.ref in back_list:
                self._add_back_person(person_ref.ref)
                back_list.remove(person_ref.ref)

        if back_list:
            for person_handle in back_list:
                self._add_back_person(person_handle)
        self.show_all()

    def _add_back_person(self, person_handle):
        """
        Add a person with a back reference.
        """
        back_person = self.fetch("Person", person_handle)
        main_person = self.group_base.obj.handle
        for back_person_ref in back_person.person_ref_list:
            if back_person_ref.ref == main_person:
                card = PersonBackRefCard(
                    self.grstate,
                    self.groptions,
                    back_person,
                    back_person_ref,
                )
                self.add_card(card)
                return

    def save_reordered_list(self):
        """
        Save a reordered list of associations.
        """
        new_list = []
        for card in self.row_cards:
            for ref in self.group_base.obj.person_ref_list:
                if ref.ref == card.primary.obj.handle:
                    new_list.append(ref)
                    break
        message = " ".join(
            (
                _("Reordered"),
                _("Associations"),
                _("for"),
                _("Person"),
                self.group_base.obj.gramps_id,
            )
        )
        self.group_base.obj.set_person_ref_list(new_list)
        self.group_base.commit(self.grstate, message)

    def save_new_object(self, handle, insert_row):
        """
        Add a new person to the list of associations.
        """
        for card in self.row_cards:
            if card.primary.obj.handle == handle:
                return

        person_ref = PersonRef()
        person_ref.ref = handle
        callback = lambda x: self.save_new_person(x, insert_row)
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

    def save_new_person(self, person_ref, insert_row):
        """
        Save the new person added to the list of associations.
        """
        new_list = []
        for card in self.row_cards:
            for ref in self.group_base.obj.person_ref_list:
                if ref.ref == card.primary.obj.handle:
                    new_list.append(ref)
        new_list.insert(insert_row, person_ref)
        person = self.fetch("Person", person_ref.ref)
        message = " ".join(
            (
                _("Added"),
                _("Person"),
                person.gramps_id,
                _("Association"),
                _("to"),
                _("Person"),
                self.group_base.obj.gramps_id,
            )
        )
        self.group_base.obj.set_person_ref_list(new_list)
        self.group_base.commit(self.grstate, message)
