#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
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
GrampsPageView
"""

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
from ..actions import action_handler
from ..views.view_builder import view_builder

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# GrampsPageView Class
#
# -------------------------------------------------------------------------
class GrampsPageView:
    """
    Provides functionality common to all page views.
    """

    def __init__(self, parent_view, page_type, grstate):
        self.parent_view = parent_view
        self.grstate = grstate
        self.page_type = page_type
        self.grstate.set_page_type(page_type)
        self.first_action_group = None
        self.second_action_group = None
        self.second_action_group_sensitive = False

    def define_actions(self):
        """
        Define page specific actions.
        """

    def enable_actions(self, uimanager, _dummy_obj):
        """
        Enable page specific actions.
        """
        if self.first_action_group:
            uimanager.set_actions_visible(self.first_action_group, True)
        if self.second_action_group:
            uimanager.set_actions_visible(self.second_action_group, True)
            uimanager.set_actions_sensitive(
                self.second_action_group, self.second_action_group_sensitive
            )

    def disable_actions(self, uimanager):
        """
        Disable page specific actions.
        """
        if self.first_action_group:
            uimanager.set_actions_visible(self.first_action_group, False)
        if self.second_action_group:
            uimanager.set_actions_visible(self.second_action_group, False)

    def render_page(self, window, context):
        """
        Render the page contents.
        """
        view = view_builder(self.grstate, context)
        window.pack_start(view, True, True, 0)
        self.post_render_page()

    def post_render_page(self):
        """
        Perform any post render page setup tasks.
        """

    def edit_active(self, *_dummy_obj):
        """
        Edit the active page object.
        """
        active = self.parent_view.get_active()
        obj = self.grstate.fetch(active[0], active[1])
        action = action_handler(active[0], self.grstate, obj)
        action.edit_object()

    def add_tag(self, trans, object_handle, tag_handle):
        """
        Add a tag to the active page object.
        """
        active = self.parent_view.get_active()
        if active[0] not in ["Tag"] and active[1] == object_handle[1]:
            obj = self.grstate.fetch(active[0], active[1])
            obj.add_tag(tag_handle)
            commit_method = self.grstate.dbstate.db.method(
                "commit_%s", active[0]
            )
            commit_method(obj, trans)
