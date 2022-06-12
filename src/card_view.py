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
CardView class
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import pickle
import time

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
from gramps.gui.display import display_url

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from global_navigation import GlobalNavigationView
from view.common.common_classes import GrampsContext, GrampsState
from view.common.common_const import PAGE_LABELS
from view.common.common_utils import get_initial_object
from view.config.config_const import HELP_VIEW
from view.config.config_profile import ProfileManager
from view.config.config_templates import (
    ConfigTemplatesDialog,
    EditTemplateOptions,
    build_templates_panel,
)
from view.services.service_windows import WindowService
from view.services.service_images import ImagesService
from view.actions import action_handler
from view.views.view_builder import view_builder

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# CardView Class
#
# -------------------------------------------------------------------------
class CardView(GlobalNavigationView):
    """
    A browseable card based view across all the associated objects in a tree.
    """

    CONFIGSETTINGS = (("templates.active", "Default"),)

    additional_ui = []

    def __init__(self, title, pdata, dbstate, uistate, nav_group=1):
        self._config_view = None
        self.grstate = None
        GlobalNavigationView.__init__(
            self,
            title,
            pdata,
            dbstate,
            uistate,
            nav_group,
        )
        self.dirty = True

        self._config_callback_ids = []
        self._load_config()
        self.methods = {}
        self._init_methods()
        self._init_state(dbstate, uistate)
        self._init_history = False

        self.current_view = None
        self.current_context = None

        self.defer_refresh = False
        self.defer_refresh_id = None
        self.config_request = None
        self.additional_uis.append(self.additional_ui)
        dbstate.connect("database-changed", self._handle_db_change)
        uistate.connect("nameformat-changed", self.build_tree)
        uistate.connect("placeformat-changed", self.build_tree)
        uistate.connect("font-changed", self.build_tree)
        self.first_action_group = None
        self.second_action_group = None
        self.second_action_group_sensitive = False
        self.image_service = ImagesService()

    def _load_config(self):
        """
        Load view configuration.
        """
        self.config_disconnect()
        profile = ProfileManager(self.dbstate, self._config)
        self._config_view = profile.get_active_options()
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

    def fetch_thumbnail(self, path, rectangle, size):
        """
        Fetch a thumbnail from cache when possible.
        """
        return self.image_service.get_thumbnail_image(path, rectangle, size)

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
                key = "%s%s" % (obj_type, suffix)
                self.callman.add_db_signal(key, self.build_tree)

    def navigation_type(self):
        """
        Return active navigation type.
        """
        return None

    def navigation_group_key(self):
        """
        Return active navigation group key.
        """
        return "cardview"

    def can_configure(self):
        """
        Return indicator view is configurable.
        """
        return True

    def get_default_gramplets(self):
        """
        Return the default Gramplets.
        """
        return ((), ())

    def reload_config(self, refresh_only=False, defer_refresh=True):
        """
        Reload all config settings and initiate redraw.
        """
        self._config.load()
        self._config_view.save()
        if not refresh_only:
            self._load_config()
        if defer_refresh:
            self._defer_config_refresh()
        else:
            self._perform_config_refresh()

    def config_connect(self):
        """
        Connect configuration callbacks so can update on changes.
        """
        if not self._config_view:
            return
        for section in self._config_view.get_sections():
            for setting in self._config_view.get_section_settings(section):
                key = "%s.%s" % (section, setting)
                if self._config_view.is_set(key):
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
        if self.defer_refresh_id:
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
        self.current_view = Gtk.VBox()
        return self.current_view

    def define_actions(self):
        """
        Define supported page actions.
        """
        GlobalNavigationView.define_actions(self)
        self._add_action("ViewHelp", self.launch_help)
        self._add_action("OpenPinnedView", self.launch_view_window)
        self._add_action("Edit", self.edit_active, "<PRIMARY>Return")
        self._add_action("PRIMARY-J", self.jump, "<PRIMARY>J")

    def _handle_db_change(self, db):
        """
        Reset page if database changed.
        """
        self._change_db(db)
        self._clear_current_view()
        if self.active:
            self.bookmarks.redraw()
        WindowService().close_all_windows()
        self.current_context = None
        self._init_methods()
        self.history.clear()
        self._init_history = False
        self.image_service.get_thumbnail_image.cache_clear()
        self._load_config()
        if self.active:
            self.build_tree()
        else:
            self.dirty = True

    def change_page(self):
        """
        Called when the page changes.
        """
        GlobalNavigationView.change_page(self)
        self.uistate.clear_filter_results()
        if self.current_context and self.current_context.primary_obj:
            self._set_status_bar(self.current_context)

    def goto_handle(self, handle):
        """
        Goto a specific object.
        """
        if self.current_context:
            if self.current_context.page_location != handle:
                self.change_object(handle)
        else:
            self.change_object(handle)

    def build_tree(self, *_dummy_args):
        """
        Perform redraw to populate tree.
        """
        self.dirty = True
        if self.active:
            active_object = self.history.present()
            if active_object:
                self.change_object(active_object)
            else:
                self.change_object(None)
        WindowService().refresh_all_windows()

    def _clear_current_view(self):
        """
        Clear view for object change.
        """
        list(
            map(
                self.current_view.remove,
                self.current_view.get_children(),
            )
        )
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
        if self.dirty_redraw_trigger:
            self.dirty_redraw_trigger = False
            self._render_page(context)
        else:
            self.change_active(context.page_location)

    def change_object(self, obj_tuple):
        """
        Change the page view to load a new active object.
        """
        if obj_tuple and obj_tuple[0] != self.navigation_type():
            target = obj_tuple[0]
            if target == "Person" and self._config_view.get(
                "general.link-people-to-relationships-view"
            ):
                target = "Relationship"
            return self.change_category(target)
        if self.dirty or self.dirty_redraw_trigger:
            self.dirty_redraw_trigger = False
            if not obj_tuple:
                obj_tuple = self._get_initial_object()
            if not obj_tuple or not obj_tuple[1]:
                self._clear_current_view()
            else:
                page_context = GrampsContext()
                page_context.load_page_location(self.grstate, obj_tuple)
                if page_context.primary_obj:
                    self._render_page(page_context)

    def _render_page(self, page_context):
        """
        Render a new page view.
        """
        if page_context.primary_obj.obj_type != self.navigation_type():
            return self.change_category(page_context.primary_obj.obj_type)
        start = time.time()

        self._clear_current_view()
        view = view_builder(self.grstate, page_context)
        self.current_view.pack_start(view, True, True, 0)
        self.post_render_page()

        if page_context.primary_obj.obj_type != "Tag":
            self.set_bookmarks(page_context.primary_obj.obj_type)
            self.bookmarks.redraw()
            self.uimanager.update_menu()
            print(
                "render_page: {} {}".format(
                    page_context.primary_obj.obj.gramps_id,
                    time.time() - start,
                )
            )
        else:
            self.bookmarks.undisplay()
        self.current_context = page_context
        self._set_status_bar(page_context)
        self.dirty = False

    def _set_status_bar(self, page_context):
        """
        Set the status bar label
        """
        self.uistate.modify_statusbar(self.dbstate)
        primary_obj_type = page_context.primary_obj.obj_type
        name, dummy_obj = navigation_label(
            self.dbstate.db,
            primary_obj_type,
            page_context.primary_obj.obj.handle,
        )
        if (
            primary_obj_type == "Person"
            and global_config.get("interface.statusbar") > 1
        ):
            relation = self.uistate.display_relationship(
                self.dbstate, page_context.primary_obj.obj.handle
            )
            if relation:
                name = "%s (%s)" % (name, relation.strip())
        if primary_obj_type == "Tag":
            name = "[%s] %s" % (
                _("Tag"),
                page_context.primary_obj.obj.get_name(),
            )
        if (
            page_context.page_type in PAGE_LABELS
            and page_context.page_type != "Tag"
        ):
            name = "%s - %s" % (name, PAGE_LABELS[page_context.page_type])
        if name:
            self.uistate.status.pop(self.uistate.status_id)
            self.uistate.status.push(self.uistate.status_id, name)

    def set_active(self):
        """
        Called when the page is displayed.
        """
        if not self.dbstate.is_open():
            return
        if not self._init_history:
            self._get_initial_object()
        GlobalNavigationView.set_active(self)
        self.uistate.viewmanager.tags.tag_enable(update_menu=False)

    def _get_initial_object(self):
        """
        Set initial object to render.
        """
        present = self.get_active()
        if present and present[0] == self.navigation_type():
            return present

        list_history = self.uistate.get_history(self.navigation_type())
        if list_history and list_history.present():
            obj_tuple = (
                self.navigation_type(),
                list_history.present(),
                None,
                None,
                None,
                None,
            )
        else:
            obj_tuple = get_initial_object(
                self.dbstate.db, self.navigation_type()
            )
        if obj_tuple:
            hobj = self.get_history()
            hobj.lock = True
            self._init_history = True
            self.history.push(obj_tuple, quiet=True, initial=True)
            hobj.lock = False
            return obj_tuple
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
        GlobalNavigationView.set_inactive(self)
        self.uistate.viewmanager.tags.tag_disable()
        if not self.dbstate.db.is_open():
            self._clear_current_view()

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

    def launch_help(self, *_dummy_args):
        """
        Launch help page.
        """
        display_url(HELP_VIEW)

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
        if self.current_context:
            windows = WindowService()
            windows.launch_view_window(self.grstate, self.current_context)

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
            "Configure Card View",
            panels=[self.build_requested_config_page],
        )

    def configure(self):
        """
        Open the configure dialog for the view.
        """
        title = _("Configure %(cat)s - %(view)s") % {
            "cat": self.get_translated_category(),
            "view": self.title,
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

    def enable_actions(self, uimanager, _dummy_obj):
        """
        Enable page specific actions.
        """
        if self.first_action_group:
            uimanager.set_actions_visible(self.first_action_group, True)
        if self.second_action_group:
            uimanager.set_actions_visible(self.second_action_group, True)
            uimanager.set_actions_sensitive(
                self.second_action_group, self.second_action_group_sensitive
            )

    def disable_actions(self, uimanager):
        """
        Disable page specific actions.
        """
        if self.first_action_group:
            uimanager.set_actions_visible(self.first_action_group, False)
        if self.second_action_group:
            uimanager.set_actions_visible(self.second_action_group, False)

    def post_render_page(self):
        """
        Perform any post render page setup tasks.
        """

    def edit_active(self, *_dummy_obj):
        """
        Edit the active page object.
        """
        if self.current_context:
            active_object = self.current_context.primary_obj
            action = action_handler(
                active_object.obj_type, self.grstate, active_object.obj
            )
            action.edit_object()

    def add_tag(self, trans, object_handle, tag_handle):
        """
        Add a tag to the active page object.
        """
        if self.current_context:
            active = self.current_context.primary_obj
            if (
                active.obj_type not in ["Tag"]
                and active.obj.handle == object_handle[1]
            ):
                active.obj.add_tag(tag_handle)
                commit_method = self.grstate.dbstate.db.method(
                    "commit_%s", active.obj_type
                )
                commit_method(active.obj, trans)
