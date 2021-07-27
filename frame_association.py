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
from frame_person import PersonGrampsFrame
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
class AssociationGrampsFrame(PersonGrampsFrame):
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
        PersonGrampsFrame.__init__(self, grstate, context, self.ref_person, obj_ref=person_ref, groups=groups)

        association = person_ref.get_relation()
        if not association:
            association = _("[None Provided]")
        hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
        hbox.pack_end(self.make_label(_("Association"), left=False), False, False, 0)
        self.ref_body.pack_start(hbox, False, False, 0)
        hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
        hbox.pack_end(self.make_label(association, left=False), False, False, 0)
        self.ref_body.pack_start(hbox, False, False, 0)

        relation = grstate.uistate.relationship.get_one_relationship(
            grstate.dbstate.db, person, self.ref_person
        )
        if relation:
            hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
            hbox.pack_end(self.make_label(_("Relationship"), left=False), False, False, 0)
            self.ref_body.pack_start(hbox, False, False, 0)
            hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
            hbox.pack_end(self.make_label(relation.capitalize(), left=False), False, False, 0)
            self.ref_body.pack_start(hbox, False, False, 0)
            
        self.enable_drag()
        self.enable_drop()
        self.set_css_style()
