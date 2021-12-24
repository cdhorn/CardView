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
PersonBackRefGrampsFrame
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

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
from ..common.common_utils import menu_item
from .frame_person import PersonGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PersonBackRefGrampsFrame class
#
# ------------------------------------------------------------------------
class PersonBackRefGrampsFrame(PersonGrampsFrame):
    """
    The PersonBackRefGrampsFrame exposes some of the basic facts about an
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
        PersonGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            person,
            reference_tuple=(person, person_ref),
        )
        if not groptions.ref_mode:
            return

        vbox = None
        association = person_ref.get_relation()
        if not association:
            association = _("[None Provided]")
        left = groptions.ref_mode == 1
        reference_type = "".join(("[", _("Back Reference"), "]"))
        for active_person_ref in active_person.get_person_ref_list():
            if active_person_ref.ref == person.get_handle():
                reference_type = "".join(("[", _("Reciprocal"), "]"))
        if groptions.ref_mode in [1, 3]:
            self.ref_widgets["body"].pack_start(
                self.get_label(reference_type, left=left), False, False, 0
            )
            self.ref_widgets["body"].pack_start(
                self.get_label(_("Association"), left=left), False, False, 0
            )
            self.ref_widgets["body"].pack_start(
                self.get_label(association, left=left), False, False, 0
            )
        else:
            vbox = Gtk.VBox()
            vbox.pack_start(
                self.get_label(reference_type, left=left), False, False, 0
            )
            vbox.pack_start(
                self.get_label("".join((_("Association"), ": ", association))),
                True,
                True,
                0,
            )

        relation = grstate.uistate.relationship.get_one_relationship(
            grstate.dbstate.db, person, active_person
        )
        if relation:
            if groptions.ref_mode in [1, 3]:
                self.ref_widgets["body"].pack_start(
                    self.get_label(_("Relationship"), left=left),
                    False,
                    False,
                    0,
                )
                self.ref_widgets["body"].pack_start(
                    self.get_label(relation.capitalize(), left=left),
                    False,
                    False,
                    0,
                )
            else:
                vbox.pack_start(
                    self.get_label(
                        "".join(
                            (_("Relationship"), ": ", relation.capitalize())
                        )
                    ),
                    True,
                    True,
                    0,
                )

        if vbox:
            self.ref_widgets["body"].pack_start(vbox, True, True, 0)

    def add_ref_custom_actions(self, context_menu):
        """
        Add custom action menu items for an associate.
        """
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(menu_item("gtk-edit", label, self.edit_person_ref))
        label = " ".join((_("Delete"), _("reference")))
        context_menu.append(
            menu_item(
                "list-remove",
                label,
                self.remove_association,
                self.reference.obj,
            )
        )
