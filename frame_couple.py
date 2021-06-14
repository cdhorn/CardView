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
from frame_css import add_style_single_frame, add_style_double_frame
from frame_image import ImageFrame
from frame_person import PersonProfileFrame
from frame_base import BaseProfile

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
# FamilyProfileFrame class
#
# ------------------------------------------------------------------------
class CoupleProfileFrame(Gtk.VBox, BaseProfile):

    def __init__(self, dbstate, uistate, family, context, space, config, router, parent=None, relation=None):
        Gtk.VBox.__init__(self, expand=False)
        BaseProfile.__init__(self, dbstate, uistate, space, config, router)
        self.obj = family
        self.family = family
        self.context= context
        self.parent = parent
        self.relation = relation

        self.frame = Gtk.Frame()
        parent_grid = Gtk.Grid(margin_right=3, margin_left=3, margin_top=3, margin_bottom=3, row_spacing=2)
        self.event_box = Gtk.EventBox()
        self.event_box.add(parent_grid)
        self.event_box.connect('button-press-event', self.build_action_menu)
        self.frame.add(self.event_box)
        self.pack_start(self.frame, expand=True, fill=True, padding=0)

        partner1, partner2 = self._get_parents()
        profile, image = self._get_profile(partner1)
        if profile:
            if image:
                parent_grid.attach(profile, 0, 0, 1, 1)
                parent_grid.attach(image, 1, 0, 1, 1)
                add_style_double_frame(profile, image)
            else:
                parent_grid.attach(profile, 0, 0, 2, 1)
                add_style_single_frame(profile)

        couple_section = Gtk.VBox()
        if not self.color_scheme:
            couple_section.pack_start(Gtk.HSeparator(), True, True, 0)

        couple_facts = Gtk.HBox()
        couple_facts.pack_start(self.facts_grid, True, True, 0)

        marriage, divorce = get_key_family_events(self.dbstate.db, self.family)
        added_event = False
        if marriage:
            self.add_event(marriage)
            added_event = True

        self.divorced = False
        if divorce:
            self.divorced = True
            if self.option(context, "show-divorce"):
                self.add_couple_event(divorce)
                added_event = True

        metadata_section = Gtk.VBox()
        gramps_id = self.get_gramps_id_label()
        metadata_section.pack_start(gramps_id, False, False, 0)

        flowbox = self.get_tags_flowbox()
        if flowbox:
            metadata_section.pack_start(flowbox, False, False, 0)

        couple_facts.pack_end(metadata_section, False, False, 0)
        couple_section.pack_start(couple_facts, True, True, 0)
        parent_grid.attach(couple_section, 0, 1, 1, 1)

        if partner2:
            if added_event and not self.color_scheme:
                couple_section.pack_start(Gtk.HSeparator(), True, True, 0)
    
            profile, image = self._get_profile(partner2)
            if profile:
                if image:
                    parent_grid.attach(profile, 0, 2, 1, 1)
                    parent_grid.attach(image, 1, 2, 1, 1)
                    add_style_double_frame(profile, image)
                else:
                    parent_grid.attach(profile, 0, 2, 2, 1)
                    add_style_single_frame(profile)

        add_style_single_frame(self)
        self.show_all()

    def _get_profile(self, person):
        if person:
            profile = PersonProfileFrame(
                self.dbstate,
                self.uistate,
                person,
                self.context,
                self.space,
                self.config,
                self.router
            )
            profile.family_backlink_handle = self.family.handle
            image = None
            if self.option(self.context, "show-image"):
                image = ImageFrame(self.dbstate.db, self.uistate, person, size=0)
            return profile, image
        return None, None
        
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
        if self.context == "spouse" and self.parent and self.option(self.context, "show-spouse-only"):
            if partner1.handle == self.parent.handle:
                partner1 = partner2
            partner2 = None
        return partner1, partner2
