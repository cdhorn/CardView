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
FamilyObjectView
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from .view_base import GrampsObjectView
from .view_const import FRAME_MAP


class FamilyObjectView(GrampsObjectView):
    """
    Provides the family object view.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        family = self.grcontext.primary_obj.obj

        groups = {
            "partner1": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "partner2": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        groptions = GrampsOptions("options.active.spouse", size_groups=groups)
        groptions.set_vertical(False)
        self.view_object = FRAME_MAP["Family"](
            self.grstate,
            groptions,
            family,
        )
        self.view_focus = self.wrap_focal_widget(self.view_object)

        pbox = None
        if self.grstate.config.get("options.active.family.show-parents"):
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
                self.view_object.parent1, p1groups
            )
            p2parents = self._get_primary_parents(
                self.view_object.parent2, p2groups
            )
            if p1parents:
                groups["partner1"].add_widget(p1parents)
                pbox.pack_start(p1parents, expand=True, fill=True, padding=0)
            if p2parents:
                groups["partner2"].add_widget(p2parents)
                pbox.pack_start(p2parents, expand=True, fill=True, padding=0)
        if pbox:
            self.view_header.pack_start(pbox, False, False, 0)
        self.view_header.pack_start(self.view_focus, False, False, 0)

        self.view_body = self.build_object_groups(self.grcontext.primary_obj)

    def _get_primary_parents(self, person, size_groups):
        """
        Return widget with primary parents of a person.
        """
        if person:
            primary_handle = person.get_main_parents_family_handle()
            if primary_handle:
                family = self.grstate.dbstate.db.get_family_from_handle(
                    primary_handle
                )
                groptions = GrampsOptions(
                    "options.active.parent", size_groups=size_groups
                )
                groptions.set_relation(person)
                return FRAME_MAP["Family"](
                    self.grstate,
                    groptions,
                    family,
                )
        return None
