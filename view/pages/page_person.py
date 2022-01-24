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
PersonPageView
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.errors import WindowActiveError
from gramps.gui.uimanager import ActionGroup
from gramps.gui.widgets.reorderfam import Reorder

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..actions import action_handler
from ..common.common_const import BUTTON_PRIMARY
from ..common.common_utils import button_pressed
from .page_base import GrampsPageView


class PersonPageView(GrampsPageView):
    """
    Provides the person anchored page view.
    """

    def define_actions(self, view):
        """
        Define page specific actions.
        """
        self.action_group = ActionGroup(name="Person")
        self.action_group.add_actions(
            [
                ("AddNewParents", self._add_new_parents),
                ("AddExistingParents", self._add_existing_parents),
                ("AddSpouse", self._add_new_family),
                ("ChangeOrder", self._reorder_families),
            ]
        )
        view.add_action_group(self.action_group)

    def post_render_page(self):
        """
        Perform any post render page setup tasks.
        """
        person = self.active_profile.primary.obj
        family_handle_list = person.get_parent_family_handle_list()
        self.reorder_sensitive = len(family_handle_list) > 1
        family_handle_list = person.get_family_handle_list()
        if not self.reorder_sensitive:
            self.reorder_sensitive = len(family_handle_list) > 1

    def reorder_button_press(self, obj, event, _dummy_handle):
        """
        Trigger reorder families.
        """
        if button_pressed(event, BUTTON_PRIMARY):
            self._reorder_families(obj)

    def _reorder_families(self, *_dummy_obj):
        """
        Reorder families.
        """
        if self.active_profile:
            try:
                Reorder(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    self.active_profile.primary.obj.get_handle(),
                )
            except WindowActiveError:
                pass

    def _add_new_parents(self, *_dummy_obj):
        """
        Add a new set of parents.
        """
        if self.active_profile:
            action = action_handler(
                "Person", self.grstate, self.active_profile.primary
            )
            action.add_new_parents()

    def _add_existing_parents(self, *_dummy_obj):
        """
        Add an existing set of parents.
        """
        if self.active_profile:
            action = action_handler(
                "Person", self.grstate, self.active_profile.primary
            )
            action.add_existing_parents()

    def _add_new_family(self, *_dummy_obj):
        """
        Add new family with or without spouse.
        """
        if self.active_profile:
            action = action_handler(
                "Person", self.grstate, self.active_profile.primary
            )
            action.add_new_family()
