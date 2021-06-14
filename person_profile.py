# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2015-2016  Nick Hall
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
Person Profile View
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from html import escape
from operator import itemgetter
import pickle
import logging
import os
import re

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GdkPixbuf

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------

from gramps.gen.config import config
from gramps.gen.lib import Family, ChildRef, Person
from gramps.gui.uimanager import ActionGroup
from gramps.gui.selectors import SelectorFactory
from gramps.gen.errors import WindowActiveError
from gramps.gui.views.bookmarks import PersonBookmarks
from gramps.gui.editors import FilterEditor
from gramps.gen.const import CUSTOM_FILTERS
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

# plugin modules
from navigationview import NavigationView
from person_profile_page import PersonProfilePage
from frame_utils import EventFormatSelector, TagModeSelector

_LOG = logging.getLogger("plugin.relview")

class PersonProfile(NavigationView):
    """
    View showing a textual representation of the relationships and events of
    the active person.
    """
    #settings in the config file
    CONFIGSETTINGS = (
        ('preferences.profile.person.layout.use-thick-borders', True),
        ('preferences.profile.person.layout.use-color-scheme', True),
        ('preferences.profile.person.layout.use-smaller-detail-font', True),
        ('preferences.profile.person.layout.enable-tooltips', True),
        ('preferences.profile.person.layout.spouses-left', True),
        ('preferences.profile.person.layout.families-stacked', False),
        ('preferences.profile.person.layout.show-timeline', True),
        ('preferences.profile.person.layout.show-citations', False),

        ('preferences.profile.person.active.event-format', 0),
        ('preferences.profile.person.active.show-gender', True),
        ('preferences.profile.person.active.show-age', True),
        ('preferences.profile.person.active.show-baptism', True),
        ('preferences.profile.person.active.show-burial', True),
        ('preferences.profile.person.active.show-relation', True),
        ('preferences.profile.person.active.show-image', True),
        ('preferences.profile.person.active.show-image-large', True),
        ('preferences.profile.person.active.show-image-first', False),
        ('preferences.profile.person.active.tag-format', 1),
        ('preferences.profile.person.active.tag-width', 2),

        ('preferences.profile.person.parent.event-format', 0),
        ('preferences.profile.person.parent.show-matrilineal', False),
        ('preferences.profile.person.parent.expand-children', True),
        ('preferences.profile.person.parent.show-gender', True),
        ('preferences.profile.person.parent.show-age', True),
        ('preferences.profile.person.parent.show-baptism', True),
        ('preferences.profile.person.parent.show-burial', True),
        ('preferences.profile.person.parent.show-divorce', True),
        ('preferences.profile.person.parent.show-image', True),
        ('preferences.profile.person.parent.tag-format', 1),
        ('preferences.profile.person.parent.tag-width', 2),

        ('preferences.profile.person.spouse.event-format', 0),
        ('preferences.profile.person.spouse.expand-children', True),
        ('preferences.profile.person.spouse.show-spouse-only', True),
        ('preferences.profile.person.spouse.show-gender', True),
        ('preferences.profile.person.spouse.show-age', True),
        ('preferences.profile.person.spouse.show-baptism', True),
        ('preferences.profile.person.spouse.show-burial', True),
        ('preferences.profile.person.spouse.show-divorce', True),
        ('preferences.profile.person.spouse.show-image', True),
        ('preferences.profile.person.spouse.tag-format', 1),
        ('preferences.profile.person.spouse.tag-width', 2),

        ('preferences.profile.person.child.event-format', 0),
        ('preferences.profile.person.child.number-children', False),
        ('preferences.profile.person.child.show-gender', True),
        ('preferences.profile.person.child.show-age', True),
        ('preferences.profile.person.child.show-baptism', True),
        ('preferences.profile.person.child.show-burial', True),
        ('preferences.profile.person.child.show-image', True),
        ('preferences.profile.person.child.show-image-first', False),
        ('preferences.profile.person.child.tag-format', 1),
        ('preferences.profile.person.child.tag-width', 2),

        ('preferences.profile.person.sibling.event-format', 0),
        ('preferences.profile.person.sibling.number-children', False),
        ('preferences.profile.person.sibling.show-gender', True),
        ('preferences.profile.person.sibling.show-age', True),
        ('preferences.profile.person.sibling.show-baptism', True),
        ('preferences.profile.person.sibling.show-burial', True),
        ('preferences.profile.person.sibling.show-tags', True),
        ('preferences.profile.person.sibling.show-image', True),
        ('preferences.profile.person.sibling.show-image-first', False),
        ('preferences.profile.person.sibling.tag-format', 1),
        ('preferences.profile.person.sibling.tag-width', 2),

        ('preferences.profile.person.timeline.show-description', True),
        ('preferences.profile.person.timeline.show-source-count', True),
        ('preferences.profile.person.timeline.show-citation-count', True),
        ('preferences.profile.person.timeline.show-best-confidence', True),
        ('preferences.profile.person.timeline.show-tags', True),
        ('preferences.profile.person.timeline.show-age', True), 
        ('preferences.profile.person.timeline.show-image', True),

        ('preferences.profile.person.timeline.show-class-vital', True),
        ('preferences.profile.person.timeline.show-class-family', True),
        ('preferences.profile.person.timeline.show-class-religious', True),
        ('preferences.profile.person.timeline.show-class-vocational', True),
        ('preferences.profile.person.timeline.show-class-academic', True),
        ('preferences.profile.person.timeline.show-class-travel', True),
        ('preferences.profile.person.timeline.show-class-legal', True),
        ('preferences.profile.person.timeline.show-class-residence', True),
        ('preferences.profile.person.timeline.show-class-other', True),
        ('preferences.profile.person.timeline.show-class-custom', True),

        ('preferences.profile.person.timeline.generations-ancestors', 1),
        ('preferences.profile.person.timeline.generations-offspring', 1),
        
        ('preferences.profile.person.timeline.show-family-father', True),
        ('preferences.profile.person.timeline.show-family-mother', True),
        ('preferences.profile.person.timeline.show-family-brother', True),
        ('preferences.profile.person.timeline.show-family-sister', True),
        ('preferences.profile.person.timeline.show-family-wife', True),
        ('preferences.profile.person.timeline.show-family-husband', True),
        ('preferences.profile.person.timeline.show-family-son', True),
        ('preferences.profile.person.timeline.show-family-daughter', True),
        
        ('preferences.profile.person.citation.show-confidence', True),
        ('preferences.profile.person.citation.show-publisher', True),
        ('preferences.profile.person.citation.show-image', True),
        )

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        NavigationView.__init__(self, _('Person Profile View'),
                                      pdata, dbstate, uistate,
                                      PersonBookmarks,
                                      nav_group)

        dbstate.connect('database-changed', self.change_db)
        uistate.connect('nameformat-changed', self.build_tree)
        self.redrawing = False

        self.pages = {}
        self._add_page(PersonProfilePage(self.dbstate, self.uistate, self._config))
        self.active_page = None

        self.additional_uis.append(self.additional_ui)

    def _add_page(self, page):
        page.connect('object-changed', self.object_changed)
        self.pages[page.obj_type()] = page

    def _connect_db_signals(self):
        """
        implement from base class DbGUIElement
        Register the callbacks we need.
        """
        # Add a signal to pick up event changes, bug #1416
        self.callman.add_db_signal('event-update', self.family_update)
        self.callman.add_db_signal('citation-update', self.redraw)

        self.callman.add_db_signal('person-add', self.person_update)
        self.callman.add_db_signal('person-update', self.person_update)
        self.callman.add_db_signal('person-rebuild', self.person_rebuild)
        self.callman.add_db_signal('family-update', self.family_update)
        self.callman.add_db_signal('family-add',    self.family_add)
        self.callman.add_db_signal('family-delete', self.family_delete)
        self.callman.add_db_signal('family-rebuild', self.family_rebuild)

        self.callman.add_db_signal('person-delete', self.redraw)

    def navigation_type(self):
        return 'Person'

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView
        :return: bool
        """
        return True

    def goto_handle(self, handle):
        self.change_object(handle)

    def config_update(self, client, cnxn_id, entry, data):
        for page in self.pages.values():
            page.config_update()
        self.redraw()

    def build_tree(self):
        self.redraw()

    def person_update(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_object(person):
                    pass
            else:
                self.change_object(None)
        else:
            self.dirty = True

    def person_rebuild(self):
        """Large change to person database"""
        if self.active:
            self.bookmarks.redraw()
            person = self.get_active()
            if person:
                while not self.change_object(person):
                    pass
            else:
                self.change_object(None)
        else:
            self.dirty = True

    def family_update(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_object(person):
                    pass
            else:
                self.change_object(None)
        else:
            self.dirty = True

    def family_add(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_object(person):
                    pass
            else:
                self.change_object(None)
        else:
            self.dirty = True

    def family_delete(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_object(person):
                    pass
            else:
                self.change_object(None)
        else:
            self.dirty = True

    def family_rebuild(self):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_object(person):
                    pass
            else:
                self.change_object(None)
        else:
            self.dirty = True

    def change_page(self):
        NavigationView.change_page(self)
        self.uistate.clear_filter_results()

    def get_stock(self):
        """
        Return the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-relation'

    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'gramps-relation'

    def build_widget(self):
        """
        Build the widget that contains the view, see
        :class:`~gui.views.pageview.PageView
        """
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.set_border_width(12)

        self.header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.header.show()

        container.set_spacing(6)
        container.pack_start(self.header, True, True, 0)
        container.show_all()

        return container

    additional_ui = [  # Defines the UI string for UIManager
        '''
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">'''
        '''Organize Bookmarks...</attribute>
        </item>
      </section>
      <section>
        <item>
          <attribute name="action">win.HomePerson</attribute>
          <attribute name="label" translatable="yes">_Home</attribute>
        </item>
      </section>
      </placeholder>
''',
        '''
      <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label" translatable="yes">Edit...</attribute>
        </item>
        <item>
          <attribute name="action">win.AddParents</attribute>
          <attribute name="label" translatable="yes">'''
        '''Add New Parents...</attribute>
        </item>
        <item>
          <attribute name="action">win.ShareFamily</attribute>
          <attribute name="label" translatable="yes">'''
        '''Add Existing Parents...</attribute>
        </item>
        <item>
          <attribute name="action">win.AddSpouse</attribute>
          <attribute name="label" translatable="yes">Add Partner...</attribute>
        </item>
        <item>
          <attribute name="action">win.ChangeOrder</attribute>
          <attribute name="label" translatable="yes">_Reorder</attribute>
        </item>
        <item>
          <attribute name="action">win.AddParticipant</attribute>
          <attribute name="label" translatable="yes">Add Participant...</attribute>
        </item>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">'''
        '''Person Filter Editor</attribute>
        </item>
      </placeholder>
''',
        '''
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label" translatable="no">%s...</attribute>
        </item>
      </section>
''' % _('Organize Bookmarks'),  # Following are the Toolbar items
        '''
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the previous object in the history</property>
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
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the next object in the history</property>
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
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the default person</property>
        <property name="label" translatable="yes">_Home</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
''',
        '''
    <placeholder id='BarCommonEdit'>
    <child groups='RO'>
      <object class="GtkToolButton" id="EditButton">
        <property name="icon-name">gtk-edit</property>
        <property name="action-name">win.Edit</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Edit the active person</property>
        <property name="label" translatable="yes">Edit...</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='Family'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-add</property>
        <property name="action-name">win.AddParents</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Add a new set of parents</property>
        <property name="label" translatable="yes">Add</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='Family'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-open</property>
        <property name="action-name">win.ShareFamily</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Add person as child to an existing family</property>
        <property name="label" translatable="yes">Share</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='Family'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-spouse</property>
        <property name="action-name">win.AddSpouse</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Add a new family with person as parent</property>
        <property name="label" translatable="yes">Partner</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='ChangeOrder'>
      <object class="GtkToolButton">
        <property name="icon-name">view-sort-ascending</property>
        <property name="action-name">win.ChangeOrder</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Change order of parents and families</property>
        <property name="label" translatable="yes">_Reorder</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='Event'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-add</property>
        <property name="action-name">win.AddParticipant</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Add a new participant to the event</property>
        <property name="label" translatable="yes">_Reorder</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='Event'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-open</property>
        <property name="action-name">win.ShareParticipant</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Add an existing participant to the event</property>
        <property name="label" translatable="yes">_Reorder</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
     ''']

    def define_actions(self):
        NavigationView.define_actions(self)
        for page in self.pages.values():
            page.define_actions(self)

        self._add_action('Edit', self.edit_active, '<PRIMARY>Return')
        self._add_action('FilterEdit', callback=self.filter_editor)
        self._add_action('PRIMARY-J', self.jump, '<PRIMARY>J')

    def filter_editor(self, *obj):
        try:
            FilterEditor('Person', CUSTOM_FILTERS,
                         self.dbstate, self.uistate)
        except WindowActiveError:
            return

    def edit_active(self, *obj):
        self.active_page.edit_active()

    def change_db(self, db):
        #reset the connects
        self._change_db(db)
        if self.active:
                self.bookmarks.redraw()
        self.history.clear()
        self.redraw()

    def redraw(self, *obj):
        active_person = self.get_active()
        if active_person:
            self.change_object(active_person)
        else:
            self.change_object(None)

    def object_changed(self, obj_type, handle):
        self.change_active((obj_type, handle))
        self.change_object((obj_type, handle))

    def change_object(self, obj_tuple):

        if obj_tuple is None:
            return


        if self.redrawing:
            return False
        self.redrawing = True

        obj_type, handle, = obj_tuple
        if obj_type == 'Person':
            obj = self.dbstate.db.get_person_from_handle(handle)
        elif obj_type == 'Event':
            obj = self.dbstate.db.get_event_from_handle(handle)

        for page in self.pages.values():
            page.disable_actions(self.uimanager)

        page = self.pages[obj_type]

        page.enable_actions(self.uimanager, obj)
        self.uimanager.update_menu()

        edit_button = self.uimanager.get_widget("EditButton")
        if edit_button:
            if obj_type == 'Person':
                tooltip = _('Edit the active person')
            elif obj_type == 'Event':
                tooltip = _('Edit the active event')
            edit_button.set_tooltip_text(tooltip)

        list(map(self.header.remove, self.header.get_children()))
        mbox = page.display_profile(obj)
        self.header.pack_start(mbox, True, True, 0)

        self.redrawing = False
        self.uistate.modify_statusbar(self.dbstate)

        self.dirty = False

        self.active_page = page

        return True

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        for item in self.CONFIGSETTINGS:
            self._config.connect(item[0],
                self.config_update)
        config.connect("interface.toolbar-on", self.config_update)

    def layout_panel(self, configdialog):
        """
        Builds layout and styling options section for the configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        configdialog.add_text(grid,
                _('Layout Options'),
                0, bold=True)        
        configdialog.add_checkbox(grid,
                _('Place spouses & children on left side'),
                1, 'preferences.profile.person.layout.spouses-left')
        configdialog.add_checkbox(grid,
                _('Stack parents & spouses in a single column'),
                2, 'preferences.profile.person.layout.families-stacked')
        configdialog.add_checkbox(grid,
                _('Show event timeline'),
                3, 'preferences.profile.person.layout.show-timeline')
        configdialog.add_checkbox(grid,
                _('Show associated citations'),
                4, 'preferences.profile.person.layout.show-citations')
        configdialog.add_text(grid,
                _('Styling Options'),
                5, bold=True)
        configdialog.add_checkbox(grid,
                _('Use smaller font for detail attributes'),
                6, 'preferences.profile.person.layout.use-smaller-detail-font')
        configdialog.add_checkbox(grid,
                _('Use thicker borders'),
                7, 'preferences.profile.person.layout.use-thick-borders')
        configdialog.add_checkbox(grid,
                _('Use color schema'),
                8, 'preferences.profile.person.layout.use-color-scheme')
        configdialog.add_checkbox(grid,
                _('Enable tooltips'),
                9, 'preferences.profile.person.layout.enable-tooltips')
        return _('Layout'), grid

    def active_panel(self, configdialog):
        """
        Builds active person options section for the configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(False)
        configdialog.add_text(grid,
                _('Display Options'),
                0, bold=True)
        event_format = EventFormatSelector('preferences.profile.person.active.event-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}: ".format(_('Event display mode')))
        grid.attach(label, 1, 1, 1, 1)
        grid.attach(event_format, 2, 1, 1, 1)
        tag_mode = TagModeSelector('preferences.profile.person.active.tag-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}: ".format(_('Tag display mode')))
        grid.attach(label, 1, 2, 1, 1)
        grid.attach(tag_mode, 2, 2, 1, 1)
        configdialog.add_spinner(grid,
                _('Maximum tags per line'),
                3, 'preferences.profile.person.active.tag-width',
                (1,6))
        configdialog.add_checkbox(grid,
                _('Show image'),
                4, 'preferences.profile.person.active.show-image')
        configdialog.add_checkbox(grid,
                _('Use large image format'),
                5, 'preferences.profile.person.active.show-image-large')
        configdialog.add_checkbox(grid,
                _('Show image first on left hand side'),
                6, 'preferences.profile.person.active.show-image-first')
        configdialog.add_text(grid,
                _('Display Attributes'),
                7, bold=True)
        configdialog.add_checkbox(grid,
                _('Show gender'),
                8, 'preferences.profile.person.active.show-gender')
        configdialog.add_checkbox(grid,
                _('Show baptism if available and not used as birth equivalent'),
                9, 'preferences.profile.person.active.show-baptism')
        configdialog.add_checkbox(grid,
                _('Show burial if available and not used as death equivalent'),
                10, 'preferences.profile.person.active.show-burial')
        configdialog.add_checkbox(grid,
                _('Show age at death and if selected burial'),
                11, 'preferences.profile.person.active.show-age')
        configdialog.add_checkbox(grid,
                _('Show relationship to home person'),
                12, 'preferences.profile.person.active.show-relation')
        return _('Person'), grid
    
    def parents_panel(self, configdialog):
        """
        Builds parents options section for the configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(False)
        configdialog.add_text(grid,
                _('Display Options'),
                0, bold=True)
        event_format = EventFormatSelector('preferences.profile.person.parent.event-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}: ".format(_('Event display mode')))
        grid.attach(label, 1, 1, 1, 1)
        grid.attach(event_format, 2, 1, 1, 1)
        tag_mode = TagModeSelector('preferences.profile.person.parent.tag-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}: ".format(_('Tag display mode')))
        grid.attach(label, 1, 2, 1, 1)
        grid.attach(tag_mode, 2, 2, 1, 1)
        configdialog.add_spinner(grid,
                _('Maximum tags per line'),
                3, 'preferences.profile.person.parent.tag-width',
                (1,6))
        configdialog.add_checkbox(grid,
                _('Show image'),
                4, 'preferences.profile.person.parent.show-image')
        configdialog.add_checkbox(grid,
                _('Matrilineal mode'),
                5, 'preferences.profile.person.parent.show-matrilineal')
        configdialog.add_checkbox(grid,
                _('Expand children by default'),
                6, 'preferences.profile.person.parent.expand-children')
        configdialog.add_text(grid,
                _('Display Attributes'),
                7, bold=True)
        configdialog.add_checkbox(grid,
                _('Show gender'),
                8, 'preferences.profile.person.parent.show-gender')
        configdialog.add_checkbox(grid,
                _('Show baptism if available and not used as birth equivalent'),
                9, 'preferences.profile.person.parent.show-baptism')
        configdialog.add_checkbox(grid,
                _('Show burial if available and not used as birth equivalent'),
                10, 'preferences.profile.person.parent.show-burial')
        configdialog.add_checkbox(grid,
                _('Show age at death and if selected burial'),
                11, 'preferences.profile.person.parent.show-age')
        configdialog.add_checkbox(grid,
                _('Show divorce or divorce equivalent'),
                12, 'preferences.profile.person.parent.show-divorce')
        return _('Parents'), grid
    
    def spouses_panel(self, configdialog):
        """
        Builds spouses options section for the configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(False)
        configdialog.add_text(grid,
                _('Display Options'),
                0, bold=True)
        event_format = EventFormatSelector('preferences.profile.person.spouse.event-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}".format(_('Event display mode')))
        grid.attach(label, 1, 1, 1, 1)
        grid.attach(event_format, 2, 1, 1, 1)
        tag_mode = TagModeSelector('preferences.profile.person.spouse.tag-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}: ".format(_('Tag display mode')))
        grid.attach(label, 1, 2, 1, 1)
        grid.attach(tag_mode, 2, 2, 1, 1)
        configdialog.add_spinner(grid,
                _('Maximum tags per line'),
                3, 'preferences.profile.person.spouse.tag-width',
                (1,6))
        configdialog.add_checkbox(grid,
                _('Show image'),
                4, 'preferences.profile.person.spouse.show-image')
        configdialog.add_checkbox(grid,
                _('Show spouse only'),
                5, 'preferences.profile.person.spouse.show-spouse-only')
        configdialog.add_checkbox(grid,
                _('Expand children by default'),
                6, 'preferences.profile.person.spouse.expand-children')
        configdialog.add_text(grid,
                _('Display Attributes'),
                7, bold=True)
        configdialog.add_checkbox(grid,
                _('Show gender'),
                8, 'preferences.profile.person.spouse.show-gender')
        configdialog.add_checkbox(grid,
                _('Show baptism if available and not used as birth equivalent'),
                9, 'preferences.profile.person.spouse.show-baptism')
        configdialog.add_checkbox(grid,
                _('Show burial if available and not used as death equivalent'),
                10, 'preferences.profile.person.spouse.show-burial')
        configdialog.add_checkbox(grid,
                _('Show age at death and if selected burial'),
                11, 'preferences.profile.person.spouse.show-age')
        configdialog.add_checkbox(grid,
                _('Show divorce or divorce equivalent'),
                12, 'preferences.profile.person.spouse.show-divorce')
        return _('Spouses'), grid
    
    def children_panel(self, configdialog):
        """
        Builds children options section for the configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(False)
        configdialog.add_text(grid,
                _('Display Options'),
                0, bold=True)
        event_format = EventFormatSelector('preferences.profile.person.child.event-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}: ".format(_('Event display mode')))
        grid.attach(label, 1, 1, 1, 1)
        grid.attach(event_format, 2, 1, 1, 1)
        tag_mode = TagModeSelector('preferences.profile.person.child.tag-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}: ".format(_('Tag display mode')))
        grid.attach(label, 1, 2, 1, 1)
        grid.attach(tag_mode, 2, 2, 1, 1)
        configdialog.add_spinner(grid,
                _('Maximum tags per line'),
                3, 'preferences.profile.person.child.tag-width',
                (1,6))
        configdialog.add_checkbox(grid,
                _('Show image'),
                4, 'preferences.profile.person.child.show-image')
        configdialog.add_checkbox(grid,
                _('Number children'),
                5, 'preferences.profile.person.child.number-children')
        configdialog.add_text(grid,
                _('Display Attributes'),
                6, bold=True)
        configdialog.add_checkbox(grid,
                _('Show gender'),
                7, 'preferences.profile.person.child.show-gender')
        configdialog.add_checkbox(grid,
                _('Show baptism if available and not used as birth equivalent'),
                8, 'preferences.profile.person.child.show-baptism')
        configdialog.add_checkbox(grid,
                _('Show burial if available and not used as death equivalent'),
                9, 'preferences.profile.person.child.show-burial')
        configdialog.add_checkbox(grid,
                _('Show age at death and if selected burial'),
                10, 'preferences.profile.person.child.show-age')
        return _('Children'), grid

    def siblings_panel(self, configdialog):
        """
        Builds siblings options section for the configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(False)
        configdialog.add_text(grid,
                _('Display Options'),
                0, bold=True)
        event_format = EventFormatSelector('preferences.profile.person.sibling.event-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}: ".format(_('Event display mode')))
        grid.attach(label, 1, 1, 1, 1)
        grid.attach(event_format, 2, 1, 1, 1)
        tag_mode = TagModeSelector('preferences.profile.person.sibling.tag-format', self._config)
        label = Gtk.Label(halign=Gtk.Align.START, label="{}: ".format(_('Tag display mode')))
        grid.attach(label, 1, 2, 1, 1)
        grid.attach(tag_mode, 2, 2, 1, 1)
        configdialog.add_spinner(grid,
                _('Maximum tags per line'),
                3, 'preferences.profile.person.sibling.tag-width',
                (1,6))
        configdialog.add_checkbox(grid,
                _('Show image'),
                4, 'preferences.profile.person.sibling.show-image')
        configdialog.add_checkbox(grid,
                _('Number children'),
                5, 'preferences.profile.person.sibling.number-children')
        configdialog.add_text(grid,
                _('Display Attributes'),
                6, bold=True)
        configdialog.add_checkbox(grid,
                _('Show gender'),
                7, 'preferences.profile.person.sibling.show-gender')
        configdialog.add_checkbox(grid,
                _('Show baptism if available and not used as birth equivalent'),
                8, 'preferences.profile.person.sibling.show-baptism')
        configdialog.add_checkbox(grid,
                _('Show burial if available and not used as death equivalent'),
                9, 'preferences.profile.person.sibling.show-burial')
        configdialog.add_checkbox(grid,
                _('Show age at death and if selected burial'),
                10, 'preferences.profile.person.sibling.show-age')
        return _('Siblings'), grid

    def timeline_panel(self, configdialog):
        """
        Builds active person timeline options section for the configuration dialog
        """
        grid1 = Gtk.Grid()
        grid1.set_border_width(12)
        grid1.set_column_spacing(6)
        grid1.set_row_spacing(6)
        grid1.set_column_homogeneous(False)
        configdialog.add_text(grid1,
                _('Display Attributes'),
                0, bold=True)
        configdialog.add_checkbox(grid1,
                _('Show age'),
                1, 'preferences.profile.person.timeline.show-age')
        configdialog.add_checkbox(grid1,
                _('Show description'),
                2, 'preferences.profile.person.timeline.show-description')
        configdialog.add_checkbox(grid1,
                _('Show source count'),
                3, 'preferences.profile.person.timeline.show-source-count')
        configdialog.add_checkbox(grid1,
                _('Show citation count'),
                4, 'preferences.profile.person.timeline.show-citation-count')
        configdialog.add_checkbox(grid1,
                _('Show best confidence rating'),
                5, 'preferences.profile.person.timeline.show-best-confidence')
        configdialog.add_checkbox(grid1,
                _('Show tags'),
                6, 'preferences.profile.person.timeline.show-tags')
        configdialog.add_checkbox(grid1,
                _('Show image'),
                7, 'preferences.profile.person.timeline.show-image')
        
        grid2 = Gtk.Grid()
        grid2.set_border_width(12)
        grid2.set_column_spacing(6)
        grid2.set_row_spacing(6)
        grid2.set_column_homogeneous(False)
        configdialog.add_text(grid2,
                _('Category Filters'),
                0, bold=True)
        configdialog.add_checkbox(grid2,
                _('Show vital'),
                1, 'preferences.profile.person.timeline.show-class-vital')
        configdialog.add_checkbox(grid2,
                _('Show family'),
                2, 'preferences.profile.person.timeline.show-class-family')
        configdialog.add_checkbox(grid2,
                _('Show religious'),
                3, 'preferences.profile.person.timeline.show-class-religious')
        configdialog.add_checkbox(grid2,
                _('Show vocational'),
                4, 'preferences.profile.person.timeline.show-class-vocational')
        configdialog.add_checkbox(grid2,
                _('Show academic'),
                5, 'preferences.profile.person.timeline.show-class-academic')
        configdialog.add_checkbox(grid2,
                _('Show travel'),
                6, 'preferences.profile.person.timeline.show-class-travel')        
        configdialog.add_checkbox(grid2,
                _('Show legal'),
                7, 'preferences.profile.person.timeline.show-class-legal')        
        configdialog.add_checkbox(grid2,
                _('Show residence'),
                8, 'preferences.profile.person.timeline.show-class-residence')        
        configdialog.add_checkbox(grid2,
                _('Show other'),
                9, 'preferences.profile.person.timeline.show-class-other')        
        configdialog.add_checkbox(grid2,
                _('Show custom'),
                10, 'preferences.profile.person.timeline.show-class-custom')
        
        grid3 = Gtk.Grid()
        grid3.set_border_width(12)
        grid3.set_column_spacing(6)
        grid3.set_row_spacing(6)
        grid3.set_column_homogeneous(False)
        configdialog.add_text(grid3,
                _('Relation Filters'),
                0, bold=True)
        configdialog.add_spinner(grid3,
                _('Generations of ancestors to examine'),
                1, 'preferences.profile.person.timeline.generations-ancestors',
                (1,3))
        configdialog.add_spinner(grid3,
                _('Generations of offspring to examine'),
                2, 'preferences.profile.person.timeline.generations-offspring',
                (1,3))
        configdialog.add_checkbox(grid3,
                _('Include events for father and grandfathers'),
                3, 'preferences.profile.person.timeline.show-family-father')
        configdialog.add_checkbox(grid3,
                _('Include events for mother and grandmothers'),
                4, 'preferences.profile.person.timeline.show-family-mother')
        configdialog.add_checkbox(grid3,
                _('Include events for brothers and stepbrothers'),
                5, 'preferences.profile.person.timeline.show-family-brother')
        configdialog.add_checkbox(grid3,
                _('Include events for sisters and stepsisters'),
                6, 'preferences.profile.person.timeline.show-family-sister')
        configdialog.add_checkbox(grid3,
                _('Include events for wives'),
                7, 'preferences.profile.person.timeline.show-family-wife')
        configdialog.add_checkbox(grid3,
                _('Include events for husbands'),
                8, 'preferences.profile.person.timeline.show-family-husband')
        configdialog.add_checkbox(grid3,
                _('Include events for sons and grandsons'),
                9, 'preferences.profile.person.timeline.show-family-son')        
        configdialog.add_checkbox(grid3,
                _('Include events for daughters and granddaughters'),
                10, 'preferences.profile.person.timeline.show-family-daughter')
        grid = Gtk.Grid()
        grid.attach(grid1, 0, 0, 1, 1)
        grid.attach(grid2, 1, 0, 1, 1)
        grid.attach(grid3, 2, 0, 1, 1)
        return _('Timeline'), grid
    
    def citations_panel(self, configdialog):
        """
        Builds citations options section for configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(False)
        configdialog.add_text(grid,
                _('Attributes'),
                0, bold=True)
        configdialog.add_checkbox(grid,
                _('Show confidence rating'),
                1, 'preferences.profile.person.citation.show-confidence')
        configdialog.add_checkbox(grid,
                _('Show publisher'),
                2, 'preferences.profile.person.citation.show-publisher')
        configdialog.add_checkbox(grid,
                _('Show image'),
                3, 'preferences.profile.person.citation.show-image')
        return _('Citations'), grid
    
    def _config_update_theme(self, obj):
        """
        callback from the theme checkbox
        """
        if obj.get_active():
            self.theme = 'WEBPAGE'
            self._config.set('preferences.relation-display-theme',
                              'WEBPAGE')
        else:
            self.theme = 'CLASSIC'
            self._config.set('preferences.relation-display-theme',
                              'CLASSIC')

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the
        notebook pages of the Configure dialog

        :return: list of functions
        """
        return [self.layout_panel, self.active_panel, self.parents_panel, self.siblings_panel, self.spouses_panel, self.children_panel, self.timeline_panel, self.citations_panel]

    def set_active(self):
        """
        Called when the page is displayed.
        """
        NavigationView.set_active(self)
        self.uistate.viewmanager.tags.tag_enable(update_menu=False)

    def set_inactive(self):
        """
        Called when the page is no longer displayed.
        """
        NavigationView.set_inactive(self)
        self.uistate.viewmanager.tags.tag_disable()

    def selected_handles(self):
        return [self.get_active()[1]]

    def add_tag(self, trans, object_handle, tag_handle):
        """
        Add the given tag to the active object.
        """
        self.active_page.add_tag(trans, object_handle, tag_handle)

