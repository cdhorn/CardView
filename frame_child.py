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
ChildGrampsFrame
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
# ChildGrampsFrame class
#
# ------------------------------------------------------------------------
class ChildGrampsFrame(PersonGrampsFrame):
    """
    The ChildGrampsFrame exposes some of the basic facts about a Child.
    """

    def __init__(
        self,
        grstate,
        context,
        child,
        child_ref,
        relation=None,
        number=0,
        groups=None,
        family_backlink=None
    ):
        PersonGrampsFrame.__init__(
            self, grstate, context, child, obj_ref=child_ref,
            relation=relation, number=number, groups=groups,
            family_backlink=family_backlink
        )
        if not child_ref:
            return

        if child_ref.get_father_relation():
                reltype = child_ref.get_father_relation()
                hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
                hbox.pack_end(self.make_label(_("Father"), left=False), False, False, 0)
                self.ref_body.pack_start(hbox, False, False, 0)
                hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
                hbox.pack_end(self.make_label(str(reltype), left=False), False, False, 0)
                self.ref_body.pack_start(hbox, False, False, 0)
    
        if child_ref.get_mother_relation():
            reltype = child_ref.get_mother_relation()
            hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
            hbox.pack_end(self.make_label(_("Mother"), left=False), False, False, 0)
            self.ref_body.pack_start(hbox, False, False, 0)
            hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
            hbox.pack_end(self.make_label(str(reltype), left=False), False, False, 0)
            self.ref_body.pack_start(hbox, False, False, 0)
