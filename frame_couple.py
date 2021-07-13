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
from frame_base import GrampsFrame
from frame_person import PersonGrampsFrame
from frame_utils import get_family_color_css, get_key_family_events

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
        router,
        family,
        context,
        space,
        config,
        parent=None,
        relation=None,
        vertical=True,
        groups=None,
        defaults=None
    ):
        GrampsFrame.__init__(self, dbstate, uistate, router, space, config, family, context, groups=groups)
        self.family = family
        self.parent = parent
        self.relation = relation

        partner1, partner2 = self._get_parents()
        profile = self._get_profile(partner1, defaults)
        if profile:
            self.partner1.add(profile)
        if partner2:
            profile = self._get_profile(partner2, defaults)
            if profile:
                self.partner2.add(profile)

        marriage, divorce = get_key_family_events(self.dbstate.db, self.family)
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

    def _get_profile(self, person, defaults):
        if person:
            working_context = self.context
            if working_context == "family":
                working_context = "people"
            profile = PersonGrampsFrame(
                self.dbstate,
                self.uistate,
                person,
                working_context,
                self.space,
                self.config,
                self.router,
                groups=self.groups,
                defaults=defaults,
                family_backlink=self.family.handle
            )
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
        if not self.config.get("preferences.profile.person.layout.use-color-scheme"):
            return ""

        return get_family_color_css(self.obj, self.config, divorced=self.divorced)
