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
from gramps.gui.uimanager import ActionGroup

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from ..frames.frame_couple import CoupleGrampsFrame
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class FamilyProfilePage(BaseProfilePage):
    """
    Provides the family profile page view with information about the family.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)
        self.active_profile = None

    @property
    def obj_type(self):
        """
        Primary object underpinning page.
        """
        return "Family"

    @property
    def page_type(self):
        """
        Page type.
        """
        return "Family"

    def define_actions(self, view):
        """
        Define page specific actions.
        """
        self.action_group = ActionGroup(name="Family")
        self.action_group.add_actions(
            [
                ("AddNewChild", self._add_new_child),
                ("AddExistingChild", self._add_existing_child),
            ]
        )
        view.add_action_group(self.action_group)

    def _get_primary_parents(self, grstate, person, groups):
        """
        Return widget with primary parents of person.
        """
        if person:
            primary_handle = person.get_main_parents_family_handle()
            if primary_handle:
                family = self.grstate.dbstate.db.get_family_from_handle(
                    primary_handle
                )
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

    def render_page(self, header, vbox, context):
        """
        Render the page contents.
        """
        if not context:
            return

        family = context.primary_obj.obj
        groups = {
            "partner1": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "partner2": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        groptions = GrampsOptions("options.active.spouse", size_groups=groups)
        groptions.set_vertical(False)
        self.active_profile = CoupleGrampsFrame(
            self.grstate,
            groptions,
            family,
        )
        focal = self.wrap_focal_widget(self.active_profile)

        pbox = None
        if self.config.get("options.active.family.show-parents"):
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
            pbox = Gtk.HBox(
                vexpand=False, hexpand=True, spacing=3, margin_bottom=0
            )
            p1parents = self._get_primary_parents(
                self.grstate, self.active_profile.parent1, p1groups
            )
            p2parents = self._get_primary_parents(
                self.grstate, self.active_profile.parent2, p2groups
            )
            if p1parents:
                groups["partner1"].add_widget(p1parents)
                pbox.pack_start(p1parents, expand=True, fill=True, padding=0)
            if p2parents:
                groups["partner2"].add_widget(p2parents)
                pbox.pack_start(p2parents, expand=True, fill=True, padding=0)

        groups = self.config.get("options.page.family.layout.groups").split(
            ","
        )
        obj_groups = self.get_object_groups(groups, family)
        body = self.render_group_view(obj_groups)

        vheader = Gtk.VBox()
        if pbox:
            if focal == self.active_profile:
                vheader.set_spacing(3)
            vheader.pack_start(pbox, False, False, 0)
        vheader.pack_start(focal, False, False, 0)

        if self.config.get("options.global.pin-header"):
            header.pack_start(vheader, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(vheader, False, False, 0)
        self.add_media_bar(vbox, family)

        vbox.pack_start(body, True, True, 0)
        vbox.show_all()
