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
import pickle

#-------------------------------------------------------------------------
#
# Set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("plugin.relview")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext # else "nearby" comments are ignored
from gramps.gen.lib import (ChildRef, EventRoleType, EventType, Family,
                            FamilyRelType, Name, Person, Surname)
from gramps.gen.lib.date import Today
from gramps.gen.db import DbTxn
from gramps.gui.views.navigationview import NavigationView
from gramps.gui.uimanager import ActionGroup
from gramps.gui.editors import EditPerson, EditFamily
from gramps.gui.editors import FilterEditor
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.alive import probably_alive
from gramps.gui.utils import open_file_with_default_application
from gramps.gen.datehandler import displayer, get_date
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gen.config import config
from gramps.gui import widgets
from gramps.gui.widgets.reorderfam import Reorder
from gramps.gui.selectors import SelectorFactory
from gramps.gen.errors import WindowActiveError
from gramps.gui.views.bookmarks import PersonBookmarks
from gramps.gen.const import CUSTOM_FILTERS
from gramps.gen.utils.db import (get_birth_or_fallback, get_death_or_fallback,
                          preset_name)
from gramps.gui.ddtargets import DdTargets
from gramps.gen.utils.symbols import Symbols

_NAME_START = 0
_LABEL_START = 0
_LABEL_STOP = 1
_DATA_START = _LABEL_STOP
_DATA_STOP = _DATA_START+1
_BTN_START = _DATA_STOP
_BTN_STOP = _BTN_START+2
_PLABEL_START = 1
_PLABEL_STOP = _PLABEL_START+1
_PDATA_START = _PLABEL_STOP
_PDATA_STOP = _PDATA_START+2
_PDTLS_START = _PLABEL_STOP
_PDTLS_STOP = _PDTLS_START+2
_CLABEL_START = _PLABEL_START+1
_CLABEL_STOP = _CLABEL_START+1
_CDATA_START = _CLABEL_STOP
_CDATA_STOP = _CDATA_START+1
_CDTLS_START = _CDATA_START
_CDTLS_STOP = _CDTLS_START+1
_ALABEL_START = 0
_ALABEL_STOP = _ALABEL_START+1
_ADATA_START = _ALABEL_STOP
_ADATA_STOP = _ADATA_START+3
_SDATA_START = 2
_SDATA_STOP = 4
_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_SPACE = Gdk.keyval_from_name("space")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3

#-------------------------------------------------------------------------
#
# Plugin Modules
#
#-------------------------------------------------------------------------
from frame_css import add_style_double_frame, add_style_single_frame
from frame_groups import get_parent_profiles, get_spouse_profiles, get_citation_profiles, get_timeline_profiles
from frame_image import ImageFrame
from frame_person import PersonProfileFrame
from frame_utils import EventFormatSelector, TagModeSelector


class PersonProfileView(NavigationView):
    """
    Summary view of a person in a navigatable format.
    """

    CONFIGSETTINGS = (
        ('preferences.profile.person.layout.enable-tooltips', True),
        ('preferences.profile.person.layout.pinned-header', True),
        ('preferences.profile.person.layout.spouses-left', True),
        ('preferences.profile.person.layout.families-stacked', False),
        ('preferences.profile.person.layout.show-timeline', True),
        ('preferences.profile.person.layout.show-citations', False),
        ('preferences.profile.person.layout.use-thick-borders', True),
        ('preferences.profile.person.layout.use-color-scheme', True),
        ('preferences.profile.person.layout.use-smaller-detail-font', True),

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
        NavigationView.__init__(self, _('Person Profile'),
                                      pdata, dbstate, uistate,
                                      PersonBookmarks,
                                      nav_group)

        dbstate.connect('database-changed', self.change_db)
        uistate.connect('nameformat-changed', self.build_tree)
        uistate.connect('placeformat-changed', self.build_tree)
        uistate.connect('font-changed', self.font_changed)
        self.redrawing = False

        self.child = None
        self.old_handle = None

        self.reorder_sensitive = False
        self.collapsed_items = {}

        self.additional_uis.append(self.additional_ui)
        self.symbols = Symbols()
        self.reload_symbols()

    def get_handle_from_gramps_id(self, gid):
        """
        returns the handle of the specified object
        """
        obj = self.dbstate.db.get_person_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def _connect_db_signals(self):
        """
        implement from base class DbGUIElement
        Register the callbacks we need.
        """
        # Add a signal to pick up event changes, bug #1416
        self.callman.add_db_signal('event-update', self.redraw)
        self.callman.add_db_signal('event-add', self.redraw)
        self.callman.add_db_signal('event-delete', self.redraw)
        self.callman.add_db_signal('event-rebuild', self.redraw)
        self.callman.add_db_signal('citation-update', self.redraw)
        self.callman.add_db_signal('citation-add', self.redraw)
        self.callman.add_db_signal('citation-delete', self.redraw)
        self.callman.add_db_signal('citation-rebuild', self.redraw)
        self.callman.add_db_signal('person-update', self.person_update)
        self.callman.add_db_signal('person-add', self.person_update)
        self.callman.add_db_signal('person-delete', self.redraw)
        self.callman.add_db_signal('person-rebuild', self.person_rebuild)
        self.callman.add_db_signal('family-update', self.family_update)
        self.callman.add_db_signal('family-add',    self.family_add)
        self.callman.add_db_signal('family-delete', self.family_delete)
        self.callman.add_db_signal('family-rebuild', self.family_rebuild)

    def reload_symbols(self):
        if self.uistate and self.uistate.symbols:
            gsfs = self.symbols.get_symbol_for_string
            self.male = gsfs(self.symbols.SYMBOL_MALE)
            self.female = gsfs(self.symbols.SYMBOL_FEMALE)
            self.bth = gsfs(self.symbols.SYMBOL_BIRTH)
            self.bptsm = gsfs(self.symbols.SYMBOL_BAPTISM)
            self.marriage = gsfs(self.symbols.SYMBOL_MARRIAGE)
            self.marr = gsfs(self.symbols.SYMBOL_HETEROSEXUAL)
            self.homom = gsfs(self.symbols.SYMBOL_MALE_HOMOSEXUAL)
            self.homof = gsfs(self.symbols.SYMBOL_LESBIAN)
            self.divorce = gsfs(self.symbols.SYMBOL_DIVORCE)
            self.unmarr = gsfs(self.symbols.SYMBOL_UNMARRIED_PARTNERSHIP)
            death_idx = self.uistate.death_symbol
            self.dth = self.symbols.get_death_symbol_for_char(death_idx)
            self.burial = gsfs(self.symbols.SYMBOL_BURIED)
            self.cremation = gsfs(self.symbols.SYMBOL_CREMATED)
        else:
            gsf = self.symbols.get_symbol_fallback
            self.male = gsf(self.symbols.SYMBOL_MALE)
            self.female = gsf(self.symbols.SYMBOL_FEMALE)
            self.bth = gsf(self.symbols.SYMBOL_BIRTH)
            self.bptsm = gsf(self.symbols.SYMBOL_BAPTISM)
            self.marriage = gsf(self.symbols.SYMBOL_MARRIAGE)
            self.marr = gsf(self.symbols.SYMBOL_HETEROSEXUAL)
            self.homom = gsf(self.symbols.SYMBOL_MALE_HOMOSEXUAL)
            self.homof = gsf(self.symbols.SYMBOL_LESBIAN)
            self.divorce = gsf(self.symbols.SYMBOL_DIVORCE)
            self.unmarr = gsf(self.symbols.SYMBOL_UNMARRIED_PARTNERSHIP)
            death_idx = self.symbols.DEATH_SYMBOL_LATIN_CROSS
            self.dth = self.symbols.get_death_symbol_fallback(death_idx)
            self.burial = gsf(self.symbols.SYMBOL_BURIED)
            self.cremation = gsf(self.symbols.SYMBOL_CREMATED)

    def font_changed(self):
        self.reload_symbols()
        self.build_tree()

    def navigation_type(self):
        return 'Person'

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView
        :return: bool
        """
        return True

    def goto_handle(self, handle):
        self.change_person(handle)

    def config_update(self, client, cnxn_id, entry, data):
        self.redraw()

    def build_tree(self):
        self.redraw()

    def person_update(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def person_rebuild(self):
        """Large change to person database"""
        if self.active:
            self.bookmarks.redraw()
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_update(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_add(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_delete(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_rebuild(self):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
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
        return 'gramps-person'

    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'gramps-person'

    def build_widget(self):
        """
        Build the widget that contains the view, see
        :class:`~gui.views.pageview.PageView
        """
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        container.set_border_width(6)
        self.header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.child = None
        self.scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC,
                               Gtk.PolicyType.AUTOMATIC)
        self.scroll.add_with_viewport(self.vbox)
        container.pack_start(self.header, False, False, 0)
        container.pack_end(self.scroll, True, True, 0)
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
    <child groups='RW'>
      <object class="GtkToolButton">
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
    <child groups='RW'>
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
    <child groups='RW'>
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
    <child groups='RW'>
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
    <child groups='RW'>
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
    </placeholder>
     ''']

    def define_actions(self):
        NavigationView.define_actions(self)

        self.order_action = ActionGroup(name=self.title + '/ChangeOrder')
        self.order_action.add_actions([
            ('ChangeOrder', self.reorder)])

        self.family_action = ActionGroup(name=self.title + '/Family')
        self.family_action.add_actions([
            ('Edit', self.edit_active, "<PRIMARY>Return"),
            ('AddSpouse', self.add_spouse),
            ('AddParents', self.add_parents),
            ('ShareFamily', self.select_parents)])

        self._add_action('FilterEdit', callback=self.filter_editor)
        self._add_action('PRIMARY-J', self.jump, '<PRIMARY>J')

        self._add_action_group(self.order_action)
        self._add_action_group(self.family_action)

        self.uimanager.set_actions_sensitive(self.order_action,
                                             self.reorder_sensitive)
        self.uimanager.set_actions_sensitive(self.family_action, False)
        self.uistate.viewmanager.tags.tag_enable(update_menu=False)

    def filter_editor(self, *obj):
        try:
            FilterEditor('Person', CUSTOM_FILTERS,
                         self.dbstate, self.uistate)
        except WindowActiveError:
            return

    def change_db(self, db):
        #reset the connects
        self._change_db(db)
        if self.child:
            list(map(self.vbox.remove, self.vbox.get_children()))
            list(map(self.header.remove, self.header.get_children()))
            self.child = None
        if self.active:
                self.bookmarks.redraw()
        self.redraw()

    def redraw(self, *obj):
        active_person = self.get_active()
        if active_person:
            self.change_person(active_person)
        else:
            self.change_person(None)

    def change_person(self, obj):
        self.change_active(obj)
        try:
            return self._change_person(obj)
        except AttributeError as msg:
            import traceback
            exc = traceback.format_exc()
            _LOG.error(str(msg) +"\n" + exc)
            from gramps.gui.dialog import RunDatabaseRepair
            RunDatabaseRepair(str(msg),
                              parent=self.uistate.window)
            self.redrawing = False
            return True
        
    def _change_person(self, obj):
        if self.redrawing:
            return False
        self.redrawing = True

        list(map(self.header.remove, self.header.get_children()))
        list(map(self.vbox.remove, self.vbox.get_children()))        

        person = None
        if obj:
            person = self.dbstate.db.get_person_from_handle(obj)
        if not person:
            self.uimanager.set_actions_sensitive(self.family_action, False)
            self.uimanager.set_actions_sensitive(self.order_action, False)
            self.redrawing = False
            return
        self.uimanager.set_actions_sensitive(self.family_action, True)

        header = Gtk.HBox()
        home = self.dbstate.db.get_default_person()
        self.active_profile = PersonProfileFrame(self.dbstate,
                self.uistate, person, "active", "preferences.profile.person",
                self._config, self.link_router, relation=home)
        if self._config.get("preferences.profile.person.active.show-image"):
            image = ImageFrame(self.dbstate.db,
                    self.uistate, person,
                    size=bool(self._config.get("preferences.profile.person.active.show-image-large")))
            if self._config.get("preferences.profile.person.active.show-image-first"): 
                header.pack_start(image, expand=False, fill=False, padding=0)
                add_style_double_frame(image, self.active_profile)
        header.pack_start(self.active_profile, expand=True, fill=True, padding=0)
        if self._config.get("preferences.profile.person.active.show-image"):
            if not self._config.get("preferences.profile.person.active.show-image-first"):            
                header.pack_end(image, expand=False, fill=False, padding=0)
                add_style_double_frame(self.active_profile, image)
        else:
            add_style_single_frame(self.active_profile)

        body = Gtk.HBox(expand=True, spacing=3)
        parents_box = Gtk.VBox(spacing=3)
        parents = get_parent_profiles(self.dbstate, self.uistate, person, router=self.link_router, config=self._config)
        if parents is not None:
            parents_box.pack_start(parents, expand=False, fill=False, padding=0)

        spouses_box = Gtk.VBox(spacing=3)
        spouses = get_spouse_profiles(self.dbstate, self.uistate, person, router=self.link_router, config=self._config)
        if spouses is not None:
            spouses_box.pack_start(spouses, expand=False, fill=False, padding=0)

        if self._config.get("preferences.profile.person.layout.show-timeline"):            
            timeline_box = Gtk.VBox(spacing=3)
            timeline = get_timeline_profiles(self.dbstate, self.uistate, person, router=self.link_router, config=self._config)
            if timeline is not None:
                timeline_box.pack_start(timeline, expand=False, fill=False, padding=0)

        if self._config.get("preferences.profile.person.layout.show-citations"):
            citations_box = Gtk.VBox(spacing=3)
            citations = get_citation_profiles(self.dbstate, self.uistate, person, router=self.link_router, config=self._config)
            if citations is not None:
                citations_box.pack_start(citations, expand=False, fill=False, padding=0)

        if self._config.get("preferences.profile.person.layout.families-stacked"):
            families_box = Gtk.VBox(spacing=3)
            families_box.pack_start(parents_box, expand=False, fill=False, padding=0)
            families_box.pack_start(spouses_box, expand=False, fill=False, padding=0)
            if self._config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(families_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-timeline"):
                body.pack_start(timeline_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-citations"):
                body.pack_start(citations_box, expand=True, fill=True, padding=0)
            if not self._config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(families_box, expand=True, fill=True, padding=0)
        else:
            if self._config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(spouses_box, expand=True, fill=True, padding=0)
            else:
                body.pack_start(parents_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-timeline"):
                body.pack_start(timeline_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-citations"):
                body.pack_start(citations_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(parents_box, expand=True, fill=True, padding=0)
            else:
                body.pack_start(spouses_box, expand=True, fill=True, padding=0)

        if self._config.get("preferences.profile.person.layout.pinned-header"):
            self.header.pack_start(header, False, False, 0)
            self.header.show_all()
        else:
            self.vbox.pack_start(header, False, False, 0)
        self.child = body
        self.vbox.pack_start(self.child, True, True, 0)
        self.vbox.show_all()
                
        family_handle_list = person.get_parent_family_handle_list()
        self.reorder_sensitive = len(family_handle_list)> 1
        family_handle_list = person.get_family_handle_list()
        if not self.reorder_sensitive:
            self.reorder_sensitive = len(family_handle_list)> 1

        self.redrawing = False
        self.uistate.modify_statusbar(self.dbstate)
        self.uimanager.set_actions_sensitive(self.order_action,
                                             self.reorder_sensitive)
        self.dirty = False
        return True

    def link_router(self, obj, event, handle, action):
        if action == "link-person":
            if button_activated(event, _LEFT_BUTTON):            
                self.change_person(handle)
    
    def marriage_symbol(self, family, markup=True):
        if family:
            father = mother = None
            hdl1 = family.get_father_handle()
            if hdl1:
                father = self.dbstate.db.get_person_from_handle(hdl1).gender
            hdl2 = family.get_mother_handle()
            if hdl2:
                mother = self.dbstate.db.get_person_from_handle(hdl2).gender
            if father != mother:
                symbol = self.marr
            elif father == Person.MALE:
                symbol = self.homom
            else:
                symbol = self.homof
            if markup:
                msg = '<span size="12000" >%s</span>' % symbol
            else:
                msg = symbol
        else:
            msg = ""
        return msg

    def change_to(self, obj, handle):
        self.change_active(handle)

    def reorder_button_press(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.reorder(obj)

    def reorder(self, *obj):
        if self.get_active():
            try:
                Reorder(self.dbstate, self.uistate, [], self.get_active())
            except WindowActiveError:
                pass

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        for item in self.CONFIGSETTINGS:
            self._config.connect(item[0],
                self.config_update)

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
                _('Pin active person header so it does not scroll'),
                1, 'preferences.profile.person.layout.pinned-header')
        configdialog.add_checkbox(grid,
                _('Place spouses & children on left side'),
                2, 'preferences.profile.person.layout.spouses-left')
        configdialog.add_checkbox(grid,
                _('Stack parents & spouses in a single column'),
                3, 'preferences.profile.person.layout.families-stacked')
        configdialog.add_checkbox(grid,
                _('Show event timeline'),
                4, 'preferences.profile.person.layout.show-timeline')
        configdialog.add_checkbox(grid,
                _('Show associated citations'),
                5, 'preferences.profile.person.layout.show-citations')
        configdialog.add_text(grid,
                _('Styling Options'),
                6, bold=True)
        configdialog.add_checkbox(grid,
                _('Use smaller font for detail attributes'),
                7, 'preferences.profile.person.layout.use-smaller-detail-font')
        configdialog.add_checkbox(grid,
                _('Use thicker borders'),
                8, 'preferences.profile.person.layout.use-thick-borders')
        configdialog.add_checkbox(grid,
                _('Use color schema'),
                9, 'preferences.profile.person.layout.use-color-scheme')
        configdialog.add_checkbox(grid,
                _('Enable tooltips'),
                10, 'preferences.profile.person.layout.enable-tooltips')
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

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the
        notebook pages of the Configure dialog

        :return: list of functions
        """
        return [self.layout_panel, self.active_panel, self.parents_panel,
                self.siblings_panel, self.spouses_panel, self.children_panel,
                self.timeline_panel, self.citations_panel]

    def edit_active(self, *obj):
        if self.active_profile:
            self.active_profile.edit_object()

    def add_spouse(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_spouse()
            
    def select_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_existing_parents()
            
    def add_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_parents()
            
    def add_tag(self, trans, object_handle, tag_handle):
        if self.active_profile:
            self.active_profile.add_tag(trans, object_handle, tag_handle)

def button_activated(event, mouse_button):
    if (event.type == Gdk.EventType.BUTTON_PRESS and
        event.button == mouse_button) or \
       (event.type == Gdk.EventType.KEY_PRESS and
        event.keyval in (_RETURN, _KP_ENTER, _SPACE)):
        return True
    else:
        return False


