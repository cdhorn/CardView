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
TagCardView
"""
import time

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Tag
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
from view.common.common_classes import GrampsContext
from view.actions import action_handler
from view.views.view_builder import view_builder

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# TagCardView Class
#
# -------------------------------------------------------------------------
class DashboardCardView(CardView):
    """
    Card view for a Tag
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=1):
        CardView.__init__(
            self,
            _("Tag"),
            pdata,
            dbstate,
            uistate,
            nav_group,
        )

    def navigation_type(self):
        """
        Return active navigation type.
        """
        return None

    def set_active(self):
        CardView.set_active(self)
        self.uistate.viewmanager.tags.tag_disable()
        self.bookmarks.undisplay()

    def set_inactive(self):
        CardView.set_inactive(self)
        self.uistate.viewmanager.tags.tag_enable(update_menu=False)
        self.bookmarks.undisplay()

    additional_ui = [
        TOOLBAR_MOREBUTTONS,
    ]

    def define_actions(self):
        """
        Define page specific actions.
        """
        CardView.define_actions(self)

    def build_tree(self, *_dummy_args):
        """
        Render a new page view.
        """
        start = time.time()

        self._clear_current_view()

        grcontext = GrampsContext()

        view = view_builder(self.grstate, grcontext)
        self.current_view.pack_start(view, True, True, 0)
        self.current_view.show_all()

        print(
            "render_page: dashboard {}".format(
                time.time() - start,
            )
        )
        self.dirty = False

    def change_page(self):
        pass
