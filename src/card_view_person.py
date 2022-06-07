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
PersonCardView
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Person, Surname
from gramps.gui.uimanager import ActionGroup
from gramps.gui.widgets.reorderfam import Reorder

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
    TOOLBAR_MOREBUTTONS,
    ADD_TOOLTIPS,
    EDIT_TOOLTIPS,
    DELETE_TOOLTIPS,
)
from view.actions import action_handler
from view.common.common_const import BUTTON_PRIMARY
from view.common.common_utils import button_pressed

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# PersonCardView Class
#
# -------------------------------------------------------------------------
class PersonCardView(CardView):
    """
    Card view for a Person
    """

    def __init__(self, pdata, dbstate, uistate, nav_group=1):
        CardView.__init__(
            self,
            _("Person"),
            pdata,
            dbstate,
            uistate,
            nav_group,
        )

    def navigation_type(self):
        """
        Return active navigation type.
        """
        return "Person"

    additional_ui = [
        MENU_LOCALEXPORT,
        MENU_ADDEDITBOOK,
        MENU_COMMONGO,
        MENU_COMMONEDIT,
        """
        <placeholder id='otheredit'>
          <item>
            <attribute name="action">win.AddNewParents</attribute>
            <attribute name="label" translatable="yes">"""
        """Add New Parents...</attribute>
          </item>
          <item>
            <attribute name="action">win.AddExistingParents</attribute>
            <attribute name="label" translatable="yes">"""
        """Add Existing Parents...</attribute>
          </item>
          <item>
            <attribute name="action">win.AddSpouse</attribute>
            <attribute name="label" translatable="yes">"""
        """Add Partner...</attribute>
          </item>
          <item>
            <attribute name="action">win.ChangeOrder</attribute>
            <attribute name="label" translatable="yes">"""
        """Reorder Families...</attribute>
          </item>
        </placeholder>
        """,
        """
        <placeholder id='CommonNavigation'>
          <child groups='RO'>
            <object class="GtkToolButton">
              <property name="icon-name">go-previous</property>
              <property name="action-name">win.Back</property>
              <property name="tooltip_text" translatable="yes">"""
        """Go to the previous object in the history</property>
              <property name="label" translatable="yes">_Back</property>
              <property name="use-underline">True</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RO'>
            <object class="GtkToolButton">
              <property name="icon-name">go-next</property>
              <property name="action-name">win.Forward</property>
              <property name="tooltip_text" translatable="yes">"""
        """Go to the next object in the history</property>
              <property name="label" translatable="yes">_Forward</property>
              <property name="use-underline">True</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RO'>
            <object class="GtkToolButton">
              <property name="icon-name">go-home</property>
              <property name="action-name">win.HomePerson</property>
              <property name="tooltip_text" translatable="yes">"""
        """Go to the default person</property>
              <property name="label" translatable="yes">_Home</property>
              <property name="use-underline">True</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
        </placeholder>
        """,
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
              <property name="action-name">win.AddNewParents</property>
              <property name="tooltip_text" translatable="yes">"""
        """Add a new set of parents</property>
              <property name="label" translatable="yes">Add</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RW'>
            <object class="GtkToolButton">
              <property name="icon-name">gramps-parents-open</property>
              <property name="action-name">win.AddExistingParents</property>
              <property name="tooltip_text" translatable="yes">"""
        """Add person as child to an existing family</property>
              <property name="label" translatable="yes">Share</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='RW'>
            <object class="GtkToolButton">
              <property name="icon-name">gramps-spouse</property>
              <property name="action-name">win.AddSpouse</property>
              <property name="tooltip_text" translatable="yes">"""
        """Add a new family with person as parent</property>
              <property name="label" translatable="yes">Partner</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
          <child groups='Reorder'>
            <object class="GtkToolButton">
              <property name="icon-name">view-sort-ascending</property>
              <property name="action-name">win.ChangeOrder</property>
              <property name="tooltip_text" translatable="yes">"""
        """Change order of parents and families</property>
              <property name="label" translatable="yes">_Reorder</property>
              <property name="use-underline">True</property>
            </object>
            <packing>
              <property name="homogeneous">False</property>
            </packing>
          </child>
        </placeholder>
        """
        % (
            ADD_TOOLTIPS["Person"],
            EDIT_TOOLTIPS["Person"],
            DELETE_TOOLTIPS["Person"],
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
                ("AddNewParents", self._add_new_parents),
                ("AddExistingParents", self._add_existing_parents),
                ("AddSpouse", self._add_new_family),
                ("Add", self._add_new_person),
                ("Remove", self._delete_person),
            ]
        )
        self._add_action_group(self.first_action_group)
        self.second_action_group = ActionGroup(name="Reorder")
        self.second_action_group.add_actions(
            [
                ("ChangeOrder", self._reorder_families),
            ]
        )
        self._add_action_group(self.second_action_group)

    def post_render_page(self):
        """
        Perform any post render page setup tasks.
        """
        if (
            self.current_context
            and self.current_context.primary_obj.obj_type != "Tag"
        ):
            person = self.current_context.primary_obj.obj
            self.second_action_group_sensitive = (
                len(person.parent_family_list) > 1
            )
            if not self.second_action_group_sensitive:
                self.second_action_group_sensitive = (
                    len(person.family_list) > 1
                )

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
        person = self.current_context.primary_obj.obj
        try:
            Reorder(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                person.handle,
            )
        except WindowActiveError:
            pass

    def _add_new_parents(self, *_dummy_obj):
        """
        Add a new set of parents.
        """
        person = self.current_context.primary_obj.obj
        action = action_handler("Person", self.grstate, person)
        action.add_new_parents()

    def _add_existing_parents(self, *_dummy_obj):
        """
        Add an existing set of parents.
        """
        person = self.current_context.primary_obj.obj
        action = action_handler("Person", self.grstate, person)
        action.add_existing_parents()

    def _add_new_family(self, *_dummy_obj):
        """
        Add new family with or without spouse.
        """
        person = self.current_context.primary_obj.obj
        action = action_handler("Person", self.grstate, person)
        action.add_new_family()

    def _add_new_person(self, *_dummy_obj):
        """
        Add a new person to the database.
        """
        person = Person()
        person.primary_name.add_surname(Surname())
        person.primary_name.set_primary_surname(0)
        action = action_handler("Person", self.grstate, person)
        action.edit_person(focus=True)

    def _delete_person(self, *_dummy_obj):
        """
        Delete person.
        """
        person = self.current_context.primary_obj.obj
        action = action_handler("Person", self.grstate, person)
        action.delete_object(person)
