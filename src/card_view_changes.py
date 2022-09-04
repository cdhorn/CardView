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
ChangesCardView
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import time

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
from card_view import CardView
from view.common.common_classes import GrampsContext
from view.services.service_statistics import StatisticsService
from view.services.service_windows import WindowService
from view.views.view_builder import view_builder

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# ChangesCardView Class
#
# -------------------------------------------------------------------------
class ChangesCardView(CardView):
    """
    Card view for the Changes
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=1):
        CardView.__init__(
            self,
            _("Changes"),
            pdata,
            dbstate,
            uistate,
            nav_group,
        )
        self.statistics_service = StatisticsService(self.grstate)

    def set_active(self):
        CardView.set_active(self)
        self.uistate.viewmanager.tags.tag_disable()
        self.bookmarks.undisplay()

    def set_inactive(self):
        CardView.set_inactive(self)
        self.uistate.viewmanager.tags.tag_enable(update_menu=False)
        self.bookmarks.undisplay()

    additional_ui = [
        """
    <placeholder id='MoreButtons'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">help-browser</property>
        <property name="action-name">win.ViewHelp</property>
        <property name="tooltip_text" translatable="yes">"""
        + """Card View help</property>
        <property name="label" translatable="yes">Help</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkSeparatorToolItem" id="sep2"/>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">view-refresh</property>
        <property name="action-name">win.ViewRefresh</property>
        <property name="tooltip_text" translatable="yes">"""
        + """Refresh statistics</property>
        <property name="label" translatable="yes">Refresh</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">edit-copy</property>
        <property name="action-name">win.OpenPinnedView</property>
        <property name="tooltip_text" translatable="yes">"""
        + """Pin copy of current view in new window</property>
        <property name="label" translatable="yes">Pin</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
"""
    ]

    def define_actions(self):
        """
        Define page specific actions.
        """
        CardView.define_actions(self)
        self._add_action("ViewRefresh", self.refresh_statistics)

    def refresh_statistics(self, *_dummy_args):
        """
        Rebuild statistics.
        """
        self.statistics_service.recalculate_data()

    def build_tree(self, *_dummy_args):
        """
        Render a new page view.
        """
        start = time.time()

        self._clear_current_view()

        self.current_context = GrampsContext()

        view = view_builder(self.grstate, self.current_context, hint="Changes")
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

    def launch_view_window(self, *_dummy_args):
        """
        Display a particular group of objects.
        """
        if self.current_context:
            windows = WindowService()
            windows.launch_view_window(
                self.grstate, self.current_context, hint="Changes"
            )
