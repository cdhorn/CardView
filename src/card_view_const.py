#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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
CardView constants
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

# -------------------------------------------------------------------------
#
# Menu Items
#
# -------------------------------------------------------------------------

MENU_LOCALEXPORT = """
      <placeholder id="LocalExport">
        <item>
          <attribute name="action">win.ExportTab</attribute>
          <attribute name="label" translatable="yes">Export View...</attribute>
        </item>
      </placeholder>
"""

MENU_ADDEDITBOOK = (
    """
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label" translatable="yes">"""
    + """_Organize Bookmarks...</attribute>
        </item>
      </section>
"""
)

MENU_COMMONGO = """
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">_Forward</attribute>
        </item>
      </section>
      </placeholder>
"""

MENU_COMMONEDIT = """
      <section id='CommonEdit' groups='RW'>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label" translatable="yes">Edit...</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
        <item>
          <attribute name="action">win.Merge</attribute>
          <attribute name="label" translatable="yes">_Merge...</attribute>
        </item>
      </section>
"""

MENU_OTHEREDIT = (
    """
        <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">"""
    + """Filter Editor</attribute>
        </item>
        </placeholder>
"""
)

# -------------------------------------------------------------------------
#
# Toolbar Items
#
# -------------------------------------------------------------------------

TOOLBAR_COMMONNAVIGATION = (
    """
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">"""
    + """Go to the previous object in the history</property>
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
    + """Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
"""
)

TOOLBAR_BARCOMMONEDIT = """
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
        <property name="label" translatable="yes">_Edit...</property>
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
    </placeholder>
"""

TOOLBAR_MOREBUTTONS = (
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
)

# -------------------------------------------------------------------------
#
# Tooltips
#
# -------------------------------------------------------------------------

ADD_TOOLTIPS = {
    "Person": _("Add a new person"),
    "Family": _("Add a new family"),
    "Event": _("Add a new event"),
    "Note": _("Add a new note"),
    "Media": _("Add a new media object"),
    "Place": _("Add a new place"),
    "Citation": _("Add a new citation"),
    "Source": _("Add a new source"),
    "Repository": _("Add a new repository"),
    "Tag": _("Add a new tag"),
}

EDIT_TOOLTIPS = {
    "Person": _("Edit the active person"),
    "Family": _("Edit the active family"),
    "Event": _("Edit the active event"),
    "Note": _("Edit the active note"),
    "Media": _("Edit the active media"),
    "Place": _("Edit the active place"),
    "Citation": _("Edit the active citation"),
    "Source": _("Edit the active source"),
    "Repository": _("Edit the active repository"),
    "Tag": _("Edit the active tag"),
}

DELETE_TOOLTIPS = {
    "Person": _("Delete the active person"),
    "Family": _("Delete the active family"),
    "Event": _("Delete the active event"),
    "Note": _("Delete the active note"),
    "Media": _("Delete the active media"),
    "Place": _("Delete the active place"),
    "Citation": _("Delete the active citation"),
    "Source": _("Delete the active source"),
    "Repository": _("Delete the active repository"),
    "Tag": _("Delete the active tag"),
}
