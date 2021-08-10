# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
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
Family Profile Page
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk


# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale


# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..bars.bar_media import MediaBarGroup
from ..frames.frame_classes import GrampsState, GrampsOptions
from ..frames.frame_couple import CoupleGrampsFrame
from ..groups.group_utils import (
    get_children_group,
    get_citations_group,
    get_media_group,
    get_notes_group,
    get_timeline_group,
    get_urls_group,
)
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class FamilyProfilePage(BaseProfilePage):
    """
    Provides the family profile page view with information about the family.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)
        self.order_action = None
        self.family_action = None
        self.reorder_sensitive = None
        self.child = None
        self.colors = None
        self.active_profile = None

    def obj_type(self):
        return "Family"

    def page_type(self):
        return "Family"

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def _get_primary_parents(self, grstate, person, groups):
        if person:
            primary_handle = person.get_main_parents_family_handle()
            if primary_handle:
                family = self.dbstate.db.get_family_from_handle(primary_handle)
                groptions = GrampsOptions(
                    "options.active.parent", size_groups=groups
                )
                groptions.set_relation(person)
                return CoupleGrampsFrame(
                    grstate,
                    groptions,
                    family,
                )
        return None

    def render_page(self, header, vbox, family, secondary=None):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not family:
            return

        groups = {
            "partner1": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "partner2": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        p1groups = {
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        p2groups = {
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router, self.config, self.page_type().lower()
        )
        groptions = GrampsOptions("options.active.spouse", size_groups=groups)
        groptions.set_vertical(False)
        self.active_profile = CoupleGrampsFrame(
            grstate,
            groptions,
            family,
        )

        pbox = Gtk.HBox(vexpand=False, hexpand=True, spacing=3, margin_bottom=3)
        p1parents = self._get_primary_parents(
            grstate, self.active_profile.parent1, p1groups
        )
        p2parents = self._get_primary_parents(
            grstate, self.active_profile.parent2, p2groups
        )
        if p1parents:
            groups["partner1"].add_widget(p1parents)
            pbox.pack_start(p1parents, expand=True, fill=True, padding=0)
        if p2parents:
            groups["partner2"].add_widget(p2parents)
            pbox.pack_start(p2parents, expand=True, fill=True, padding=0)

        vbox.pack_start(pbox, expand=True, fill=True, padding=0)
        vbox.pack_start(self.active_profile, expand=True, fill=True, padding=0)

        if self.config.get("options.global.enable-media-bar"):
            bar = MediaBarGroup(grstate, None, family)
            if bar:
                vbox.pack_start(bar, False, False, 0)

        groups = self.config.get("options.page.family.layout.groups").split(",")
        obj_groups = {}

        if "child" in groups:
            obj_groups.update({"child": get_children_group(grstate, family)})
        if "timeline" in groups:
            obj_groups.update({"timeline": get_timeline_group(grstate, family)})
        if "citation" in groups:
            obj_groups.update(
                {"citation": get_citations_group(grstate, family)}
            )
        if "url" in groups:
            obj_groups.update({"url": get_urls_group(grstate, family)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, family)})
        if "media" in groups:
            obj_groups.update({"media": get_media_group(grstate, family)})
        body = self.render_group_view(obj_groups)

        vbox.pack_start(body, True, True, 0)
        vbox.show_all()
