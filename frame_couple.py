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
CoupleGrampsFrame
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
from frame_base import GrampsFrame
from frame_person import PersonGrampsFrame
from frame_utils import get_key_family_events


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
# CoupleGrampsFrame class
#
# ------------------------------------------------------------------------
class CoupleGrampsFrame(GrampsFrame):
    """
    The CoupleGrampsFrame exposes some of the basic information about a Couple.
    """

    def __init__(
        self,
        dbstate,
        uistate,
        family,
        context,
        space,
        config,
        router,
        parent=None,
        relation=None,
    ):
        GrampsFrame.__init__(self, dbstate, uistate, space, config, family, context)
        self.family = family
        self.parent = parent
        self.relation = relation
        self.router = router

        self.section = Gtk.VBox(
            margin_right=3, margin_left=3, margin_top=3, margin_bottom=3, spacing=2
        )
        self.body.add(self.section)

        self.groups = {
            "image": Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL),
            "data": Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL),
        }
        partner1, partner2 = self._get_parents()
        profile = self._get_profile(partner1)
        if profile:
            self.section.pack_start(profile, True, True, 0)

        couple_facts = Gtk.HBox()
        couple_facts.pack_start(self.facts_grid, True, True, 0)

        marriage, divorce = get_key_family_events(self.dbstate.db, self.family)
        if marriage:
            self.add_event(marriage)

        self.divorced = False
        if divorce:
            self.divorced = True
            if self.option(context, "show-divorce"):
                self.add_event(divorce)

        metadata_section = Gtk.VBox()
        gramps_id = self.get_gramps_id_label()
        metadata_section.pack_start(gramps_id, False, False, 0)

        flowbox = self.get_tags_flowbox()
        if flowbox:
            metadata_section.pack_start(flowbox, False, False, 0)

        couple_facts.pack_end(metadata_section, False, False, 0)
        self.section.pack_start(couple_facts, True, True, 0)

        if partner2:
            profile = self._get_profile(partner2)
            if profile:
                self.section.pack_start(profile, True, True, 0)

        self.set_css_style()
        self.show_all()

    def _get_profile(self, person):
        if person:
            profile = PersonGrampsFrame(
                self.dbstate,
                self.uistate,
                person,
                self.context,
                self.space,
                self.config,
                self.router,
                groups=self.groups,
            )
            profile.family_backlink_handle = self.family.handle
            return profile
        return None

    def _get_parents(self):
        father = None
        if self.family.father_handle:
            father = self.dbstate.db.get_person_from_handle(self.family.father_handle)
        mother = None
        if self.family.mother_handle:
            mother = self.dbstate.db.get_person_from_handle(self.family.mother_handle)

        partner1 = father
        partner2 = mother
        if self.option(self.context, "show-matrilineal"):
            partner1 = mother
            partner2 = father
        if (
            self.context == "spouse"
            and self.parent
            and self.option(self.context, "show-spouse-only")
        ):
            if partner1.handle == self.parent.handle:
                partner1 = partner2
            partner2 = None
        return partner1, partner2
