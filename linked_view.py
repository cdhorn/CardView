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
LinkedView class
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import pickle
import time
from functools import lru_cache

# -------------------------------------------------------------------------
#
# GTK Modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject, Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db.dummydb import DummyDb
from gramps.gen.errors import WindowActiveError
from gramps.gen.utils.db import navigation_label
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gui.display import display_url
from gramps.gui.views.bookmarks import PersonBookmarks

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from extended_navigation import ExtendedNavigationView
from view.common.common_classes import GrampsContext, GrampsState
from view.common.common_utils import get_initial_object
from view.config.config_const import PAGES
from view.config.config_defaults import VIEWDEFAULTS
from view.config.config_profile import ProfileManager
from view.config.config_templates import (
    ConfigTemplatesDialog,
    EditTemplateOptions,
    build_templates_panel,
)
from view.pages.page_builder import page_builder
from view.services.service_windows import WindowService

_ = glocale.translation.sgettext

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
}

HELP_URL = "https://www.gramps-project.org/wiki/index.php/Addon:LinkedView"


# -------------------------------------------------------------------------
#
# LinkedView Class
#
# -------------------------------------------------------------------------
class LinkedView(ExtendedNavigationView):
    """
    A browseable view across all the associated objects in a tree.
    """

    CONFIGSETTINGS = (
        ("hpane.slider-position", 0),
        ("templates.active", "Default"),
        ("templates.templates", ["Default"]),
        ("vpane.slider-position", 0),
    )

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        self._config_view = None
        self.grstate = None
        ExtendedNavigationView.__init__(
            self,
            _("Linked"),
            pdata,
            dbstate,
            uistate,
            PersonBookmarks,
            nav_group,
        )
        self.passed_uistate = uistate
        self.passed_navtype = None
        if uistate.viewmanager.active_page:
            self.passed_navtype = (
                uistate.viewmanager.active_page.navigation_type()
            )
        self.dirty = True
        self.child = None
        self._config_callback_ids = []
        self._load_config()
        self.methods = {}
        self._init_methods()
        self._init_state(dbstate, uistate)
        self.pages = {}
        self._init_pages()
        self.page_view = None
        self.active_page = None
        self.active_type = None
        self.defer_refresh = False
        self.defer_refresh_id = None
        self.config_request = None
        self.in_change_object = False
        self.additional_uis.append(self.additional_ui)
        dbstate.connect("database-changed", self._handle_db_change)
        uistate.connect("nameformat-changed", self.build_tree)
        uistate.connect("placeformat-changed", self.build_tree)

    def _load_config(self):
        """
        Load view configuration.
        """
        self.config_disconnect()
        profile_name = self._config.get("templates.active")
        user_ini_file = "_".join(("Browse_linkview_template", profile_name))
        if self.dbstate and self.dbstate.db:
            db_ini_file = "Browse_linkview_database"
            dbid = self.dbstate.db.get_dbid()
            if dbid:
                db_ini_file = "_".join((db_ini_file, dbid))
        else:
            db_ini_file = None
        profile_manager = ProfileManager(
            self.ident, VIEWDEFAULTS, user_ini_file, db_ini_file
        )
        self._config_view = profile_manager.get_config_manager()
        self._config_view.save()
        self.config_connect()
        if self.grstate:
            self.grstate.set_config(self._config_view)

    def _init_methods(self):
        """
        Initialize query methods cache.
        """
        for obj_type in [
            "Person",
            "Family",
            "Event",
            "Place",
            "Citation",
            "Source",
            "Note",
            "Media",
            "Tag",
            "Repository",
        ]:
            query_method = self.dbstate.db.method(
                "get_%s_from_handle", obj_type
            )
            self.methods.update({obj_type: query_method})

    def _init_state(self, dbstate, uistate):
        """
        Initialize state.
        """
        callbacks = {
            "methods": self.methods,
            "load-page": self.load_page,
            "reload-config": self.reload_config,
            "fetch-thumbnail": self.fetch_thumbnail,
            "fetch-page-context": self.fetch_page_context,
            "copy-to-clipboard": self.clipboard_copy,
            "update-history-reference": self.update_history_reference,
            "show-group": self.launch_group_window,
            "launch-config": self.launch_config,
            "set-dirty-redraw-trigger": self.set_dirty_redraw_trigger,
        }
        self.grstate = GrampsState(
            dbstate, uistate, callbacks, self._config_view
        )
        self.grstate.set_templates(self._config)

    def _init_pages(self):
        """
        Load page handlers.
        """
        for (page_type, dummy_page_lang) in PAGES:
            self.pages[page_type] = page_builder(self, page_type, self.grstate)

    @lru_cache(maxsize=32)
    def fetch_thumbnail(self, path, rectangle, size):
        """
        Fetch a thumbnail from cache when possible.
        """
        return get_thumbnail_image(path, rectangle=rectangle, size=size)

    def fetch_page_context(self):
        """
        Return page context.
        """
        grcontext = GrampsContext()
        grcontext.load_page_location(self.grstate, self.get_active())
        return grcontext

    def set_dirty_redraw_trigger(self):
        """
        Mark current page dirty.
        """
        self.dirty_redraw_trigger = True

    def _connect_db_signals(self):
        """
        Register the callbacks we need.
        """
        for obj_type in [
            "person",
            "family",
            "event",
            "place",
            "source",
            "citation",
            "media",
            "repository",
            "note",
            "tag",
        ]:
            for suffix in ["-add", "-update", "-delete", "-rebuild"]:
                key = "".join((obj_type, suffix))
                self.callman.add_db_signal(key, self.build_tree)

    def navigation_type(self):
        """
        Return active navigation type.
        """
        return self.active_type

    def can_configure(self):
        """
        Return indicator view is configurable.
        """
        return True

    def reload_config(self, refresh_only=False):
        """
        Reload all config settings and initiate redraw.
        """
        self._config.load()
        self._config_view.save()
        if not refresh_only:
            self._load_config()
        self._defer_config_refresh()

    def config_connect(self):
        """
        Connect configuration callbacks so can update on changes.
        Always skip active.last_object as otherwise triggers a second redraw.
        """
        if not self._config_view:
            return
        for section in self._config_view.get_sections():
            for setting in self._config_view.get_section_settings(section):
                key = ".".join((section, setting))
                if (
                    "active.last_object" not in key
                    and self._config_view.is_set(key)
                ):
                    try:
                        callback_id = self._config_view.connect(
                            key, self._defer_config_refresh
                        )
                        self._config_callback_ids.append(callback_id)
                    except KeyError:
                        pass

    def config_disconnect(self):
        """
        Disconnect configuration callbacks.
        """
        for callback_id in self._config_callback_ids:
            self._config_view.disconnect(callback_id)
        self._config_callback_ids.clear()

    def _defer_config_refresh(self, *_dummy_args):
        """
        Defer configuration rebuild events a short bit.
        """
        if not self.defer_refresh_id:
            self.defer_refresh_id = GObject.timeout_add(
                3000, self._perform_config_refresh
            )
        else:
            self.defer_refresh = True

    def _perform_config_refresh(self):
        """
        Perform the view rebuild due to a configuration change.
        """
        if self.defer_refresh:
            self.defer_refresh = False
            return True
        self.defer_refresh = False
        self.build_tree()
        GObject.source_remove(self.defer_refresh_id)
        self.defer_refresh_id = None
        return False

    def templates_panel(self, configdialog):
        """
        Build templates manager panel for the configuration dialog.
        """
        return _("Templates"), build_templates_panel(
            configdialog, self.grstate
        )

    def _get_configure_page_funcs(self):
        """
        Return functions to build the configuration dialogs.
        """
        return [self.templates_panel]

    def get_stock(self):
        """
        Return the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return "gramps-relation-linked"

    def get_viewtype_stock(self):
        """
        Type of view in category.
        """
        return "gramps-relation-linked"

    def build_widget(self):
        """
        Build the widget that contains the view.
        """
        self.page_view = Gtk.VBox()
        return self.page_view

    additional_ui = [  # Defines the UI string for UIManager
        """
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">"""
        """Organize Bookmarks...</attribute>
        </item>
      </section>
      <section>
        <item>
          <attribute name="action">win.HomePerson</attribute>
          <attribute name="label" translatable="yes">_Home</attribute>
        </item>
      </section>
      </placeholder>
""",
        """
      <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label" translatable="yes">Edit...</attribute>
        </item>
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
          <attribute name="label" translatable="yes">_Reorder</attribute>
        </item>
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
        """
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
"""
        % _("Organize Bookmarks"),  # Following are the Toolbar items
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
    <child groups='RO'>
      <object class="GtkToolButton" id="EditButton">
        <property name="icon-name">gtk-edit</property>
        <property name="action-name">win.Edit</property>
        <property name="tooltip_text" translatable="yes">"""
        """Edit the active person</property>
        <property name="label" translatable="yes">Edit...</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='BrowsePerson'>
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
    <child groups='BrowsePerson'>
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
    <child groups='BrowsePerson'>
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
    <child groups='BrowseChangeOrder'>
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
    <child groups='BrowseFamily'>
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
    <child groups='BrowseFamily'>
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
    <child groups='BrowseEvent'>
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
    <child groups='BrowseEvent'>
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
""",
        """
    <placeholder id='MoreButtons'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">help-browser</property>
        <property name="action-name">win.ViewHelp</property>
        <property name="tooltip_text" translatable="yes">"""
        """View help</property>
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
        <property name="action-name">win.CopyPageView</property>
        <property name="tooltip_text" translatable="yes">"""
        """Copy page</property>
        <property name="label" translatable="yes">Copy</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
""",
    ]

    def define_actions(self):
        """
        Define supported page actions.
        """
        ExtendedNavigationView.define_actions(self)
        for page in self.pages.values():
            page.define_actions()

        self._add_action("ViewHelp", self.launch_help)
        self._add_action("CopyPageView", self.launch_view_window)
        self._add_action("Edit", self._edit_active, "<PRIMARY>Return")
        self._add_action("PRIMARY-J", self.jump, "<PRIMARY>J")

    def add_action_group(self, action_group):
        """
        Wrapper to expose private _add_action_group to pages.
        """
        self._add_action_group(action_group)

    def _edit_active(self, *_dummy_obj):
        """
        Edit active object.
        """
        self.active_page.edit_active()

    def _handle_db_change(self, db):
        """
        Reset page if database changed.
        """
        if not isinstance(db, DummyDb):
            self._change_db(db)
            self._init_methods()
            if self.active:
                self.bookmarks.redraw()
            WindowService().close_all_windows()
            self.history.clear()
            self.fetch_thumbnail.cache_clear()
            self._load_config()
            self.build_tree()

    def change_page(self):
        """
        Called when the page changes.
        """
        ExtendedNavigationView.change_page(self)
        self.uistate.clear_filter_results()

    def goto_handle(self, handle):
        """
        Goto a specific object.
        """
        self.change_object(handle)

    def build_tree(self, *_dummy_args):
        """
        Perform redraw to populate tree.
        """
        self.dirty = True
        if self.active:
            active_object = self.get_active()
            if active_object:
                self.change_object(active_object)
            else:
                self.change_object(None)
        WindowService().refresh_all_windows()

    def _clear_change(self):
        """
        Clear view for object change.
        """
        list(map(self.page_view.remove, self.page_view.get_children()))
        if not self.dbstate.is_open():
            self.uistate.status.pop(self.uistate.status_id)
            self.uistate.status.push(
                self.uistate.status_id, _("No active object")
            )

    def load_page(self, new_context):
        """
        Load the proper page for the given context.
        """
        if not new_context:
            return
        try:
            context = pickle.loads(new_context)
        except pickle.UnpicklingError:
            return
        self.dirty = True
        self.change_active(context.page_location)

    def change_object(self, obj_tuple):
        """
        Change the page view to load a new active object.
        """
        if not self.dirty:
            return
        if not obj_tuple:
            obj_tuple = self._get_initial_object()
            if not obj_tuple:
                self._clear_change()
                return

        if self.in_change_object:
            return
        self.in_change_object = True

        page_context = GrampsContext()
        page_context.load_page_location(self.grstate, obj_tuple)
        if page_context.primary_obj:
            self._render_page(page_context)
            self._config_view.set(
                "active.last_object",
                ":".join(
                    (
                        page_context.primary_obj.obj_type,
                        page_context.primary_obj.obj.get_handle(),
                    )
                ),
            )
            self._config_view.save()
        self.in_change_object = False
        return

    def _render_page(self, page_context):
        """
        Render a new page view.
        """
        start = time.time()
        if self.active_page:
            self.active_page.disable_actions(self.uimanager)

        self._clear_change()
        page = self.pages[page_context.page_type]
        page.render_page(self.page_view, page_context)
        page.enable_actions(self.uimanager, page_context.primary_obj)
        self.uimanager.update_menu()

        primary_obj_type = page_context.primary_obj.obj_type
        edit_button = self.uimanager.get_widget("EditButton")
        if edit_button and primary_obj_type in EDIT_TOOLTIPS:
            tooltip = EDIT_TOOLTIPS[primary_obj_type]
            edit_button.set_tooltip_text(tooltip)

        self.uistate.modify_statusbar(self.dbstate)

        self.active_page = page
        self.active_type = primary_obj_type
        name, dummy_obj = navigation_label(
            self.dbstate.db,
            primary_obj_type,
            page_context.primary_obj.obj.get_handle(),
        )
        if (
            primary_obj_type == "Person"
            and global_config.get("interface.statusbar") > 1
        ):
            relation = self.uistate.display_relationship(
                self.dbstate, page_context.primary_obj.obj.get_handle()
            )
            if relation:
                name = "".join((name, " (", relation.strip(), ")"))
        if name:
            self.uistate.status.pop(self.uistate.status_id)
            self.uistate.status.push(self.uistate.status_id, name)
        self.dirty = False
        if page_context.primary_obj.obj_type != "Tag":
            print(
                "render_page: {} {}".format(
                    page_context.primary_obj.obj.get_gramps_id(),
                    time.time() - start,
                )
            )

    def set_active(self):
        """
        Called when the page is displayed.
        """
        if not self.history.history:
            self._get_initial_object()
        ExtendedNavigationView.set_active(self)
        self.uistate.viewmanager.tags.tag_enable(update_menu=False)

    def _get_initial_object(self):
        """
        Get initial object to render.
        """
        if self.passed_uistate.history_lookup:
            obj_tuple = self._get_history_object()
        if not obj_tuple:
            obj_tuple = get_initial_object(self.dbstate.db, self._config_view)
        if obj_tuple:
            self.history.push(obj_tuple, quiet=True, initial=True)
            return obj_tuple
        return None

    def _get_history_object(self):
        """
        Attempt to find last object referenced using the passed uistate copy
        as the views may be using divergent history navigation classes.
        """
        for nav_obj in self.passed_uistate.history_lookup:
            obj_type, dummy_nav_type = nav_obj
            if obj_type == self.passed_navtype:
                obj_history = self.passed_uistate.history_lookup[nav_obj]
                if obj_history and obj_history.present():
                    return (
                        obj_type,
                        obj_history.present(),
                        None,
                        None,
                        None,
                        None,
                    )
        return None

    def update_history_reference(self, old, new):
        """
        Replace secondary reference in history entries with a new one.
        Used to keep history in sync with secondary object updates.
        """
        return self.history.replace_secondary(old, new)

    def set_inactive(self):
        """
        Called when the page is no longer displayed.
        """
        ExtendedNavigationView.set_inactive(self)
        self.uistate.viewmanager.tags.tag_disable()
        if not self.dbstate.db.is_open():
            self._clear_change()

    def selected_handles(self):
        """
        Return current active handle.
        """
        return [self.get_active()]

    def clipboard_copy(self, data, handle):
        """
        Copy current object to clipboard.
        """
        return self.copy_to_clipboard(data, [handle])

    def add_tag(self, trans, object_handle, tag_handle):
        """
        Add the given tag to the active object.
        """
        self.active_page.add_tag(trans, object_handle, tag_handle)

    def launch_help(self, *_dummy_args):
        """
        Launch help page.
        """
        display_url(HELP_URL)

    def launch_group_window(self, obj, group_type, title):
        """
        Display a particular group of objects.
        """
        windows = WindowService()
        windows.launch_group_window(self.grstate, obj, group_type, title)

    def launch_view_window(self, *_dummy_args):
        """
        Display a particular group of objects.
        """
        grcontext = GrampsContext()
        grcontext.load_page_location(self.grstate, self.get_active())
        windows = WindowService()
        windows.launch_view_window(self.grstate, grcontext)

    def build_requested_config_page(self, configdialog):
        """
        Build a generic configuration page for a request.
        """
        (label, builder, space, context) = self.config_request
        return label, builder(configdialog, self.grstate, space, context)

    def launch_config(self, label, builder, space, context):
        """
        Launch configuration dialog page.
        """
        self.config_request = (label, builder, space, context)
        EditTemplateOptions(
            self.grstate,
            [],
            self._config_view,
            "Configure Browse View",
            panels=[self.build_requested_config_page],
        )

    def configure(self):
        """
        Open the configure dialog for the view.
        """
        title = _("Configure %(cat)s - %(view)s") % {
            "cat": self.get_translated_category(),
            "view": self.get_title(),
        }

        if self.can_configure():
            config_funcs = self._get_configure_page_funcs()
        else:
            config_funcs = []
        if self.sidebar:
            config_funcs += self.sidebar.get_config_funcs()
        if self.bottombar:
            config_funcs += self.bottombar.get_config_funcs()

        try:
            ConfigTemplatesDialog(
                self.uistate,
                self.dbstate,
                [],
                config_funcs,
                self,
                self._config,
                dialogtitle=title,
            )

        except WindowActiveError:
            return
