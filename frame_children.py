#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
FamilyProfileFrame
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
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Person, Family, Span
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import BaseProfile
from frame_person import PersonProfileFrame
from frame_couple import CoupleProfileFrame

from frame_utils import format_date_string, get_key_person_events, get_key_family_events, TextLink


# ------------------------------------------------------------------------
#
# Internationalisation
#
# ------------------------------------------------------------------------
try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# ChildrenProfileFrame class
#
# ------------------------------------------------------------------------
class ChildrenProfileFrame(Gtk.VBox, BaseProfile):

    def __init__(self, dbstate, uistate, family, context, space, config, router,
                 parent=None, relation=None, children="Children"):

        Gtk.VBox.__init__(self, hexpand=True, spacing=3)
        BaseProfile.__init__(self, dbstate, uistate, space, config, router)
        self.family = family
        self.context = context
        self.parent = parent
        self.relation = relation
        self.children = children
        self.number = 0

        context = "child"
        if self.context == "parent":
            context = "sibling"

        sizegroup = Gtk.SizeGroup()
        sizegroup.set_mode(Gtk.SizeGroupMode.HORIZONTAL)

        for ref in self.family.get_child_ref_list():
            if ref:
                child = self.dbstate.db.get_person_from_handle(ref.ref)
                child_number = self.number + 1
                if not self.option(context, "number-children"):
                    child_number = 0
                profile = PersonProfileFrame(self.dbstate, self.uistate, child, context,
                                             self.space, self.config, self.router,
                                             number=child_number, relation=self.relation, group=sizegroup)
                profile.family_backlink_handle = self.family.handle
                self.pack_start(profile, True, True, 0)
#                add_style_single_frame(profile)
                self.number = self.number + 1
