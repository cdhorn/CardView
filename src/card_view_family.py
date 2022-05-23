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
FamilyCardView
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Family
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
# FamilyCardView Class
#
# -------------------------------------------------------------------------
class FamilyCardView(CardView):
    """
    Card view for a Family
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        CardView.__init__(
            self,
            _("Family"),
            pdata,
            dbstate,
            uistate,
            nav_group,
        )

    def navigation_type(self):
        """
        Return active navigation type.
        """
        return "Family"

    additional_ui = [
        MENU_LOCALEXPORT,
        MENU_ADDEDITBOOK,
        MENU_COMMONGO,
        MENU_COMMONEDIT,
        """
        <placeholder id='otheredit'>
          <item>
            <attribute name="action">win.AddNewChild</attribute>
            <attribute name="label" translatable="yes">"""
        """Add New Child...</attribute>
          </item>
          <item>
            <attribute name="action">win.AddExistingChild</attribute>
            <attribute name="label" translatable="yes">"""
        """Add Existing Child...</attribute>
          </item>
        </placeholder>
        """,
        TOOLBAR_COMMONNAVIGATION,
        """
        <placeholder id='BarCommonEdit'>
          <child groups='RW'>
            <object class="GtkToolButton" id="AddButton">
              <property name="icon-name">list-add</property>
              <property name="action-name">win.Add</property>
              <property name="tooltip_text">%s</property>
              <property name="label" translatable="yes">_Add...</property>
              <property name="use-underline">True</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RW'>
            <object class="GtkToolButton" id="EditButton">
              <property name="icon-name">gtk-edit</property>
              <property name="action-name">win.Edit</property>
              <property name="tooltip_text">%s</property>
              <property name="label" translatable="yes">Edit...</property>
              <property name="use-underline">True</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RW'>
            <object class="GtkToolButton" id="DeleteButton">
              <property name="icon-name">list-remove</property>
              <property name="action-name">win.Remove</property>
              <property name="tooltip_text">%s</property>
              <property name="label" translatable="yes">_Delete</property>
              <property name="use-underline">True</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RW'>
            <object class="GtkToolButton">
              <property name="icon-name">gramps-parents-add</property>
              <property name="action-name">win.AddNewChild</property>
              <property name="tooltip_text" translatable="yes">"""
        """Add a new person as a child of the family</property>
              <property name="label" translatable="yes">Add</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RW'>
            <object class="GtkToolButton">
              <property name="icon-name">gramps-parents-open</property>
              <property name="action-name">win.AddExistingChild</property>
              <property name="tooltip_text" translatable="yes">"""
        """Add an existing person as a child of the family</property>
              <property name="label" translatable="yes">Share</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
        </placeholder>
        """
        % (
            ADD_TOOLTIPS["Family"],
            EDIT_TOOLTIPS["Family"],
            DELETE_TOOLTIPS["Family"],
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
                ("AddNewChild", self._add_new_child),
                ("AddExistingChild", self._add_existing_child),
                ("Add", self._add_new_family),
                ("Remove", self._delete_family),
            ]
        )
        self._add_action_group(self.first_action_group)

    def _add_new_child(self, *_dummy_obj):
        """
        Add a new person as a child member of the family.
        """
        family = self.current_context.primary_obj.obj
        action = action_handler("Family", self.grstate, family)
        action.add_new_child()

    def _add_existing_child(self, *_dummy_obj):
        """
        Add an existing person as a child member of the family.
        """
        family = self.current_context.primary_obj.obj
        action = action_handler("Family", self.grstate, family)
        action.add_existing_child()

    def _add_new_family(self, *_dummy_obj):
        """
        Add a new family to the database.
        """
        action = action_handler("Family", self.grstate, Family())
        action.edit_family()

    def _delete_family(self, *_dummy_obj):
        """
        Delete family.
        """
        family = self.current_context.primary_obj.obj
        action = action_handler("Family", self.grstate, family)
        action.delete_object(family)
