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
PersonRefGrampsFrame
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
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gui.editors import EditPersonRef

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
# PersonRefGrampsFrame class
#
# ------------------------------------------------------------------------
class PersonRefGrampsFrame(PersonGrampsFrame):
    """
    The PersonRefGrampsFrame exposes some of the basic facts about an
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
        PersonGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            associate,
            reference_tuple=(person, person_ref),
        )
        if not groptions.ref_mode:
            return

        vbox = None
        association = person_ref.get_relation()
        if not association:
            association = _("[None Provided]")
        left = groptions.ref_mode == 1
        if groptions.ref_mode in [1, 3]:
            self.ref_widgets["body"].pack_start(
                self.make_label(_("Association"), left=left), False, False, 0
            )
            self.ref_widgets["body"].pack_start(
                self.make_label(association, left=left), False, False, 0
            )
        else:
            vbox = Gtk.VBox()
            vbox.pack_start(
                self.make_label(": ".join((_("Association"), association))),
                True,
                True,
                0,
            )

        relation = grstate.uistate.relationship.get_one_relationship(
            grstate.dbstate.db, person, associate
        )
        if relation:
            if groptions.ref_mode in [1, 3]:
                self.ref_widgets["body"].pack_start(
                    self.make_label(_("Relationship"), left=left),
                    False,
                    False,
                    0,
                )
                self.ref_widgets["body"].pack_start(
                    self.make_label(relation.capitalize(), left=left),
                    False,
                    False,
                    0,
                )
            else:
                vbox.pack_start(
                    self.make_label(
                        ": ".join((_("Relationship"), relation.capitalize()))
                    ),
                    True,
                    True,
                    0,
                )

        if vbox:
            self.ref_widgets["body"].pack_start(vbox, True, True, 0)

    def add_ref_custom_actions(self, action_menu):
        """
        Add custom action menu items for an associate.
        """
        label = " ".join((_("Edit"), _("reference")))
        action_menu.append(menu_item("gtk-edit", label, self.edit_person_ref))
        label = " ".join((_("Delete"), _("reference")))
        action_menu.append(
            menu_item(
                "list-remove",
                label,
                self.remove_person_ref,
                self.reference.obj,
            )
        )

    def remove_person_ref(self, _dummy_obj, person_ref):
        """
        Remove an association.
        """
        person = self.fetch("Person", person_ref.ref)
        text = "".join((name_displayer.display(person),))
        prefix = _(
            "You are about to remove the following association with this "
            "person:"
        )
        extra = _(
            "Note this does not delete the person. You can also use the "
            "undo option under edit if you change your mind later."
        )
        if self.confirm_action(
            _("Warning"), prefix, "\n\n<b>", text, "</b>\n\n", extra
        ):
            new_list = []
            for ref in self.base.obj.get_person_ref_list():
                if not ref.ref == person_ref.ref:
                    new_list.append(ref)
            message = " ".join(
                (
                    _("Removed"),
                    _("PersonRef"),
                    person.get_gramps_id(),
                    _("from"),
                    _("Person"),
                    self.base.obj.get_gramps_id(),
                )
            )
            self.base.obj.set_person_ref_list(new_list)
            self.base.commit(self.grstate, message)
