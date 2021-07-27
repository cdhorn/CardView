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
AssociationGrampsFrame
"""

from html import escape

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
from gramps.gen.utils.alive import probably_alive


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_class import GrampsFrame
from frame_utils import (
    _GENDERS,
    get_person_color_css,
    TextLink,
)

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# AssociationGrampsFrame class
#
# ------------------------------------------------------------------------
class AssociationGrampsFrame(GrampsFrame):
    """
    The AssociationGrampsFrame exposes some of the basic facts about an Association.
    """

    def __init__(
        self,
        grstate,
        context,
        person,
        person_ref,
        groups=None,
    ):
        self.person = person
        self.person_ref = person_ref
        self.ref_person = grstate.dbstate.db.get_person_from_handle(person_ref.ref)
        GrampsFrame.__init__(self, grstate, context, person, groups=groups)

        display_name = name_displayer.display(self.ref_person)
        name = TextLink(
            display_name, "Person", person_ref.ref, self.switch_object, bold=True
        )
        name_box = Gtk.HBox(spacing=2)
        if self.option(context, "sex-mode") == 1:
            name_box.pack_start(Gtk.Label(label=_GENDERS[self.ref_person.gender]), False, False, 0)
        name_box.pack_start(name, False, False, 0)
        if self.option(context, "sex-mode") == 2:
            name_box.pack_start(Gtk.Label(label=_GENDERS[self.ref_person.gender]), False, False, 0)
        self.title.pack_start(name_box, True, True, 0)

        association = person_ref.get_relation()
        if not association:
            association = _("[None Provided]")
        label = self.make_label(_("Association"))
        fact = self.make_label(association)
        self.add_fact(fact, label=label)

        relation = grstate.uistate.relationship.get_one_relationship(
            grstate.dbstate.db, person, self.ref_person
        )
        if relation:
            label = self.make_label(_("Relationship"))
            fact = self.make_label(relation.capitalize())
            self.add_fact(fact, label=label)

        self.living = probably_alive(self.ref_person, grstate.dbstate.db)
        
        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def get_color_css(self):
        return get_person_color_css(self.ref_person, self.grstate.config, living=self.living)

    def get_gramps_id_label(self):
        """
        Build the label for a gramps id including lock icon if object marked private.
        """
        label = Gtk.Label(use_markup=True, label=self.markup.format(escape(self.ref_person.gramps_id)))
        hbox = Gtk.HBox()
        hbox.pack_end(label, False, False, 0)
        if self.person_ref.private:
            image = Gtk.Image()
            image.set_from_icon_name("gramps-lock", Gtk.IconSize.BUTTON)
            hbox.pack_end(image, False, False, 0)
        return hbox

    def build_action_menu(self, obj, event):
        return
