#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2021-2022  Christopher Horn
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
RepositoryCardView
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Repository
from gramps.gui.uimanager import ActionGroup

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from card_view import CardView
from card_view_const import (
    MENU_LOCALEXPORT,
    MENU_ADDEDITBOOK,
    MENU_COMMONGO,
    MENU_COMMONEDIT,
    MENU_OTHEREDIT,
    TOOLBAR_BARCOMMONEDIT,
    TOOLBAR_COMMONNAVIGATION,
    TOOLBAR_MOREBUTTONS,
    ADD_TOOLTIPS,
    EDIT_TOOLTIPS,
    DELETE_TOOLTIPS,
)
from view.actions import action_handler

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# RepositoryCardView Class
#
# -------------------------------------------------------------------------
class RepositoryCardView(CardView):
    """
    Card view for a Repository
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        CardView.__init__(
            self,
            _("Repository"),
            pdata,
            dbstate,
            uistate,
            nav_group,
        )

    def navigation_type(self):
        """
        Return active navigation type.
        """
        return "Repository"

    additional_ui = [
        MENU_LOCALEXPORT,
        MENU_ADDEDITBOOK,
        MENU_COMMONGO,
        MENU_COMMONEDIT,
        MENU_OTHEREDIT,
        TOOLBAR_COMMONNAVIGATION,
        TOOLBAR_BARCOMMONEDIT
        % (
            ADD_TOOLTIPS["Repository"],
            EDIT_TOOLTIPS["Repository"],
            DELETE_TOOLTIPS["Repository"],
        ),
        TOOLBAR_MOREBUTTONS,
    ]

    def define_actions(self):
        """
        Define page specific actions.
        """
        CardView.define_actions(self)
        self.first_action_group = ActionGroup(name="RW")
        self.first_action_group.add_actions(
            [
                ("Add", self._add_new_repository),
                ("Remove", self._delete_repository),
            ]
        )
        self._add_action_group(self.first_action_group)

    def _add_new_repository(self, *_dummy_obj):
        """
        Add a new repository to the database.
        """
        action = action_handler("Repository", self.grstate, Repository())
        action.edit_repository()

    def _delete_repository(self, *_dummy_obj):
        """
        Delete repository.
        """
        repository = self.current_context.primary_obj.obj
        action = action_handler("Repository", self.grstate, repository)
        action.delete_object(repository)
