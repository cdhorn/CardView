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
EventCardView
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Event
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
# EventCardView Class
#
# -------------------------------------------------------------------------
class EventCardView(CardView):
    """
    Card view for an Event
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=1):
        CardView.__init__(
            self,
            _("Event"),
            pdata,
            dbstate,
            uistate,
            nav_group,
        )

    def navigation_type(self):
        """
        Return active navigation type.
        """
        return "Event"

    additional_ui = [
        MENU_LOCALEXPORT,
        MENU_ADDEDITBOOK,
        MENU_COMMONGO,
        MENU_COMMONEDIT,
        """
        <placeholder id='otheredit'>
          <item>
            <attribute name="action">win.AddNewParticipant</attribute>
            <attribute name="label" translatable="yes">"""
        """Add New Participant...</attribute>
          </item>
          <item>
            <attribute name="action">win.AddExistingParticipant</attribute>
            <attribute name="label" translatable="yes">"""
        """Add Existing Participant...</attribute>
          </item>
        </placeholder>
        """,
        TOOLBAR_COMMONNAVIGATION,
        """
        <placeholder id='BarCommonEdit'>
          <child groups='RW'>
            <object class="GtkToolButton">
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
            <object class="GtkToolButton">
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
            <object class="GtkToolButton">
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
              <property name="icon-name">gramps-merge</property>
              <property name="action-name">win.Merge</property>
              <property name="tooltip_text" translatable="yes">Merge</property>
              <property name="label" translatable="yes">_Merge...</property>
              <property name="use-underline">True</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RW'>
            <object class="GtkToolButton">
              <property name="icon-name">gramps-parents-add</property>
              <property name="action-name">win.AddNewParticipant</property>
              <property name="tooltip_text" translatable="yes">"""
        """Add a new participant to the event</property>
              <property name="label" translatable="yes">Add</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RW'>
            <object class="GtkToolButton">
              <property name="icon-name">gramps-parents-open</property>
              <property name="action-name">win.AddExistingParticipant</property>
              <property name="tooltip_text" translatable="yes">"""
        """Add an existing participant to the event</property>
              <property name="label" translatable="yes">Share</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
        </placeholder>
        """
        % (
            ADD_TOOLTIPS["Event"],
            EDIT_TOOLTIPS["Event"],
            DELETE_TOOLTIPS["Event"],
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
                ("AddNewParticipant", self._add_new_participant),
                ("AddExistingParticipant", self._add_existing_participant),
                ("Add", self._add_new_event),
                ("Remove", self._delete_event),
            ]
        )
        self._add_action_group(self.first_action_group)

    def _add_new_participant(self, *_dummy_obj):
        """
        Add a new person as a participant in the event.
        """
        event = self.current_context.primary_obj.obj
        action = action_handler("Event", self.grstate, event)
        action.add_new_participant()

    def _add_existing_participant(self, *_dummy_obj):
        """
        Add an existing person as a participant in the event.
        """
        event = self.current_context.primary_obj.obj
        action = action_handler("Event", self.grstate, event)
        action.add_existing_participant()

    def _add_new_event(self, *_dummy_obj):
        """
        Add a new event to the database.
        """
        action = action_handler("Event", self.grstate, Event())
        action.edit_event(focus=True)

    def _delete_event(self, *_dummy_obj):
        """
        Delete event.
        """
        if self.current_context:
            event = self.current_context.primary_obj.obj
            action = action_handler("Event", self.grstate, event)
            action.delete_object(event)
