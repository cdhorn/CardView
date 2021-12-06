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
EventPageView
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gui.uimanager import ActionGroup

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from .page_base import GrampsPageView


class EventPageView(GrampsPageView):
    """
    Provides the event anchored page view.
    """

    def define_actions(self, view):
        """
        Define page specific actions.
        """
        self.action_group = ActionGroup(name="Event")
        self.action_group.add_actions(
            [
                ("AddNewPart", self._add_new_participant),
                ("AddExistingPart", self._add_existing_participant),
            ]
        )
        view.add_action_group(self.action_group)

    def _add_new_participant(self, *_dummy_obj):
        """
        Add a new person as a participant in the event.
        """
        if self.active_profile:
            self.active_profile.add_new_participant()

    def _add_existing_participant(self, *_dummy_obj):
        """
        Add an existing person as a participant in the event.
        """
        if self.active_profile:
            self.active_profile.add_existing_participant()
