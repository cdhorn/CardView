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
LinkedView class
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import pickle
import time
import uuid
from functools import lru_cache

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk, GObject

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import HandleError, WindowActiveError
from gramps.gen.utils.db import navigation_label
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gui.display import display_url
from gramps.gui.views.bookmarks import PersonBookmarks
from gramps.gui.views.pageview import ViewConfigureDialog

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from extended_navigation import ExtendedNavigationView
from view.common.common_classes import GrampsContext, GrampsState
from view.common.common_utils import (
    get_config_option,
    save_config_option,
)
from view.config.config_const import PAGES
from view.config.config_options import CONFIGSETTINGS
from view.groups.group_window import FrameGroupWindow
from view.pages.page_builder import page_builder
from view.pages.page_window import PageViewWindow

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


class LinkedView(ExtendedNavigationView):
    """
    A browseable view across all the associated objects in a tree.
    """

    # Kept separate due to sheer number of them
    CONFIGSETTINGS = CONFIGSETTINGS

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
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
        self.child = None
        self.grstate = None
        self.methods = {}
        self._init_methods()
        self.pages = {}
        self._init_pages()
        self.page_view = None
        self.active_page = None
        self.active_type = None
        self.group_windows = {}
        self.page_windows = {}
        self.defer_refresh = False
        self.defer_refresh_id = None
        self.config_request = None
        self.in_change_object = False
        self.initial_object_loaded = False
        self.additional_uis.append(self.additional_ui)
        dbstate.connect("database-changed", self._handle_db_change)
        uistate.connect("nameformat-changed", self.build_tree)
        uistate.connect("placeformat-changed", self.build_tree)

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

    def fetch_object(self, obj_type, handle):
        """
        Fetch an object from the database.
        """
        try:
            return self.methods[obj_type](handle)
        except HandleError:
            return None

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

    def mark_page_dirty(self):
        """
        Mark current page dirty.
        """
        self.dirty = True

    def _init_pages(self):
        """
        Load page handlers.
        """
        callbacks = {
            "load-page": self.load_page,
            "fetch-object": self.fetch_object,
            "fetch-thumbnail": self.fetch_thumbnail,
            "fetch-page-context": self.fetch_page_context,
            "copy-to-clipboard": self.clipboard_copy,
            "update-history-reference": self.update_history_reference,
            "show-group": self.show_group,
            "launch-config": self.launch_config,
            "mark-dirty": self.mark_page_dirty,
        }
        self.grstate = GrampsState(
            self.dbstate, self.uistate, callbacks, self._config
        )
        for (page_type, page_lang) in PAGES:
            self.pages[page_type] = page_builder(page_type, self.grstate)

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
            self.callman.add_db_signal(
                "".join((obj_type, "-add")), self.build_tree
            )
            self.callman.add_db_signal(
                "".join((obj_type, "-update")), self.build_tree
            )
            self.callman.add_db_signal(
                "".join((obj_type, "-delete")), self.build_tree
            )
            self.callman.add_db_signal(
                "".join((obj_type, "-rebuild")), self.build_tree
            )

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

    def config_connect(self):
        """
        Monitor configuration options for changes.
        First option should be options.active.last_object which
        we always need to skip otherwise we redraw page twice.
        """
        for item in self.CONFIGSETTINGS[1:]:
            self._config.connect(item[0], self._defer_config_refresh)

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
        Perform the configuration rebuild.
        """
        if self.defer_refresh:
            self.defer_refresh = False
            return True
        self.defer_refresh = False
        self.build_tree()
        GObject.source_remove(self.defer_refresh_id)
        self.defer_refresh_id = None
        return False

    def _get_configure_page_funcs(self):
        """
        Return functions to build the configuration dialogs.
        """
        return self.active_page.get_configure_page_funcs()

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
    <child groups='Person'>
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
    <child groups='Person'>
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
    <child groups='Person'>
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
    <child groups='Person'>
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
    <child groups='Family'>
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
    <child groups='Family'>
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
    <child groups='Event'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-add</property>
        <property name="action-name">win.AddNewPart</property>
        <property name="tooltip_text" translatable="yes">"""
        """Add a new participant to the event</property>
        <property name="label" translatable="yes">Add</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='Event'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-open</property>
        <property name="action-name">win.AddExistingPart</property>
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
            page.define_actions(self)

        self._add_action("ViewHelp", self.launch_help)
        self._add_action("CopyPageView", self.launch_copy)
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
        self._change_db(db)
        self._init_methods()
        if self.active:
            self.bookmarks.redraw()
        for window in [y for x, y in self.page_windows.items()]:
            window.close()
        self.page_windows.clear()
        for window in [y for x, y in self.group_windows.items()]:
            window.close()
        self.group_windows.clear()
        self.history.clear()
        self.fetch_thumbnail.cache_clear()
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
        for window in [y for x, y in self.page_windows.items()]:
            window.refresh()
        for window in [y for x, y in self.group_windows.items()]:
            window.refresh()

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
            obj_tuple = self._get_last()
            if not obj_tuple:
                self._clear_change()
                return
            self.history.push(tuple(obj_tuple), quiet=True)
            self.initial_object_loaded = True

        if self.in_change_object:
            return
        self.in_change_object = True

        page_context = GrampsContext()
        page_context.load_page_location(self.grstate, obj_tuple)
        if page_context.primary_obj:
            self._render_page(page_context)
            if self.initial_object_loaded:
                dbid = self.dbstate.db.get_dbid()
                save_config_option(
                    self._config,
                    "options.active.last_object",
                    page_context.primary_obj.obj_type,
                    page_context.primary_obj.obj.get_handle(),
                    dbid=dbid,
                )
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
        if not self.initial_object_loaded and not self.history.history:
            if self.passed_uistate and self.passed_navtype:
                self.initial_object_loaded = self._seed_history()
            if not self.initial_object_loaded:
                obj_tuple = self._get_last()
                if obj_tuple:
                    self.history.push(tuple(obj_tuple))
                    self.initial_object_loaded = True
        ExtendedNavigationView.set_active(self)
        self.uistate.viewmanager.tags.tag_enable(update_menu=False)

    def _seed_history(self):
        """
        Attempt to seed our history cache with last object using the uistate
        copy as the views may be using divergent history navigation classes.
        """
        if not self.passed_uistate.history_lookup:
            return False
        for nav_obj in self.passed_uistate.history_lookup:
            obj_type, dummy_nav_type = nav_obj
            if obj_type == self.passed_navtype:
                obj_history = self.passed_uistate.history_lookup[nav_obj]
                if obj_history and obj_history.present():
                    self.history.push(
                        (
                            obj_type,
                            obj_history.present(),
                            None,
                            None,
                            None,
                            None,
                        ),
                        quiet=True,
                    )
                    return True
        return False

    def _get_last(self):
        """
        Try to determine last accessed object.
        """
        dbid = self.dbstate.db.get_dbid()
        if not dbid:
            return None
        try:
            obj_tuple = get_config_option(
                self._config, "options.active.last_object", dbid=dbid
            )
        except ValueError:
            obj_tuple = None
        if not obj_tuple or len(obj_tuple) != 2:
            initial_person = self.dbstate.db.find_initial_person()
            if not initial_person:
                return None
            obj_tuple = ("Person", initial_person.get_handle())
        return (
            obj_tuple[0],
            obj_tuple[1],
            None,
            None,
            None,
            None,
        )

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

    def show_group(self, obj, group_type, title):
        """
        Display a particular group of objects.
        """
        max_windows = self._config.get(
            "options.global.display.max-group-windows"
        )
        if hasattr(obj, "handle"):
            key = "-".join((obj.get_handle(), group_type))
            if key in self.group_windows:
                self.group_windows[key].refresh()
                return
        else:
            key = uuid.uuid4().hex

        if max_windows == 1:
            if self.group_windows:
                for dummy_key, window in self.group_windows.items():
                    window.reload(obj, group_type)
                    break
                return
        if len(self.group_windows) >= max_windows:
            return
        self.group_windows[key] = FrameGroupWindow(
            self.grstate,
            obj,
            group_type,
            key,
            self._clear_group_window,
            title=title,
        )
        return

    def _clear_group_window(self, key):
        """
        Clear window.
        """
        if key in self.group_windows:
            del self.group_windows[key]

    def launch_help(self, *_dummy_args):
        """
        Launch help page.
        """
        display_url(HELP_URL)

    def launch_copy(self, *_dummy_args):
        """
        Display a particular group of objects.
        """
        grcontext = GrampsContext()
        grcontext.load_page_location(self.grstate, self.get_active())
        max_windows = self._config.get(
            "options.global.display.max-page-windows"
        )
        key = grcontext.obj_key
        if key in self.group_windows:
            self.page_windows[key].refresh()
            return
        if max_windows == 1:
            if self.page_windows:
                for dummy_key, window in self.page_windows.items():
                    window.reload(grcontext)
                    break
                return
        if len(self.page_windows) >= max_windows:
            return
        self.page_windows[key] = PageViewWindow(
            self.grstate, grcontext, key, self._clear_page_window
        )
        return

    def _clear_page_window(self, key):
        """
        Clear window.
        """
        if key in self.page_windows:
            del self.page_windows[key]

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
        try:
            ViewConfigureDialog(
                self.uistate,
                self.dbstate,
                [self.build_requested_config_page],
                self,
                self._config,
                "Configure Relationships - Linked",
            )
        except WindowActiveError:
            pass
