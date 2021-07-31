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
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_primary import PrimaryGrampsFrame
from frame_person import PersonGrampsFrame
from frame_utils import get_family_color_css, get_key_family_events

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# CoupleGrampsFrame class
#
# ------------------------------------------------------------------------
class CoupleGrampsFrame(PrimaryGrampsFrame):
    """
    The CoupleGrampsFrame exposes some of the basic information about a Couple.
    """

    def __init__(
        self,
        grstate,
        context,
        family,
        parent=None,
        relation=None,
        vertical=True,
        groups=None,
    ):
        PrimaryGrampsFrame.__init__(self, grstate, context, family, groups=groups, vertical=vertical)
        self.family = family
        self.parent = parent
        self.relation = relation

        self.parent1, self.parent2 = self._get_parents()
        profile = self._get_profile(self.parent1)
        if profile:
            self.partner1.add(profile)
        if self.parent2:
            profile = self._get_profile(self.parent2)
            if profile:
                self.partner2.add(profile)

        marriage, divorce = get_key_family_events(grstate.dbstate.db, self.family)
        if marriage:
            self.add_event(marriage)

        self.divorced = False
        if divorce:
            self.divorced = True
            if self.option(context, "show-divorce"):
                self.add_event(divorce)
        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def build_layout(self):
        """
        Construct framework for couple layout, overrides base class.
        """
        vcontent = Gtk.VBox(spacing=3)
        self.body.pack_start(vcontent, expand=True, fill=True, padding=0)
        if self.vertical:
            self.partner1 = Gtk.HBox(hexpand=True)
            vcontent.pack_start(self.partner1, expand=True, fill=True, padding=0)
            dcontent = Gtk.VBox()
            self.eventbox.add(dcontent)
            vcontent.pack_start(self.eventbox, expand=True, fill=True, padding=0)
            hcontent = Gtk.HBox(hexpand=True)
            hcontent.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
            hcontent.pack_start(self.extra_grid, expand=True, fill=True, padding=0)
            hcontent.pack_start(self.metadata, expand=True, fill=True, padding=0)
            dcontent.pack_start(hcontent, expand=True, fill=True, padding=0)
            dcontent.pack_start(self.tags, expand=True, fill=True, padding=0)
            self.partner2 = Gtk.HBox(hexpand=True)
            vcontent.pack_start(self.partner2, expand=True, fill=True, padding=0)
        else:
            group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
            partners = Gtk.HBox(hexpand=True, spacing=3)
            vcontent.pack_start(partners, expand=True, fill=True, padding=0)
            self.partner1 = Gtk.HBox(hexpand=True)
            group.add_widget(self.partner1)
            if self.groups and 'partner1' in self.groups:
                self.groups['partner1'].add_widget(self.partner1)
            partners.pack_start(self.partner1, expand=True, fill=True, padding=0)
            self.partner2 = Gtk.HBox(hexpand=True)
            group.add_widget(self.partner2)
            if self.groups and 'partner2' in self.groups:
                self.groups['partner2'].add_widget(self.partner2)
            partners.pack_start(self.partner2, expand=True, fill=True, padding=0)
            dcontent = Gtk.VBox()
            self.eventbox.add(dcontent)
            vcontent.pack_start(self.eventbox, expand=True, fill=True, padding=0)
            hcontent = Gtk.HBox(hexpand=True)
            hcontent.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
            hcontent.pack_start(self.extra_grid, expand=True, fill=True, padding=0)
            hcontent.pack_start(self.metadata, expand=True, fill=True, padding=0)
            dcontent.pack_start(hcontent, expand=True, fill=True, padding=0)
            dcontent.pack_start(self.tags, expand=True, fill=True, padding=0)

    def _get_profile(self, person):
        if person:
            working_context = self.context
            if working_context == "family":
                working_context = "people"
            profile = PersonGrampsFrame(
                self.grstate,
                working_context,                
                person,
                groups=self.groups,
                family_backlink=self.family.handle
            )
            return profile
        return None

    def _get_parents(self):
        father = None
        if self.family.get_father_handle():
            father = self.grstate.dbstate.db.get_person_from_handle(self.family.get_father_handle())
        mother = None
        if self.family.get_mother_handle():
            mother = self.grstate.dbstate.db.get_person_from_handle(self.family.get_mother_handle())

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
            if partner1 and partner1.handle == self.parent.handle or not partner1:
                partner1 = partner2
            partner2 = None
        return partner1, partner2

    def add_custom_actions(self):
        """
        Add action menu items for the person based on the context in which
        they are present in relation to the active person.
        """
        if self.context in ["parent", "spouse"]:
            self.action_menu.append(self._add_new_family_event_option())
            self.action_menu.append(self._add_new_child_to_family_option())
            self.action_menu.append(self._add_existing_child_to_family_option())

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.option("page", "use-color-scheme"):
            return ""

        return get_family_color_css(self.obj, self.grstate.config, divorced=self.divorced)
