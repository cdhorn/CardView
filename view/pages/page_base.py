# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
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
GrampsPageView
"""

# -------------------------------------------------------------------------
#
# GTK Modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..bars.bar_media import GrampsMediaBarGroup
from ..common.common_classes import GrampsState
from ..common.common_const import GROUP_LABELS
from ..common.common_utils import make_scrollable
from ..groups.group_utils import build_group
from .page_config_colors import (
    CONFIDENCE_OPTIONS,
    CONFIDENCE_TYPE,
    EVENT_OPTIONS,
    EVENT_TYPE,
    RELATION_OPTIONS,
    RELATION_TYPE,
    ROLE_OPTIONS,
    ROLE_TYPE,
    build_color_grid,
)
from .page_config_global import build_global_grid
from .page_config_layout import build_layout_grid
from .page_config_objects import (
    ConfigNotebook,
    build_address_grid,
    build_citation_grid,
    build_event_grid,
    build_family_grid,
    build_ldsord_grid,
    build_media_grid,
    build_name_grid,
    build_note_grid,
    build_person_grid,
    build_place_grid,
    build_repository_grid,
    build_source_grid,
)
from .page_config_timeline import (
    build_family_timeline_grid,
    build_person_timeline_grid,
)
from .page_utils import create_grid
from ..views.view_builder import view_builder

_ = glocale.translation.sgettext


class GrampsPageView:
    """
    Provides functionality common to all page views.
    """

    def __init__(self, page_type, grstate):
        self.grstate = grstate
        self.page_type = page_type
        self.grstate.set_page_type(page_type)
        self.active_profile = None
        self.action_group = None
        self.child = None
        self.colors = None
        self.config = self.grstate.config
        self.container = None

    def define_actions(self, view):
        """
        Define page specific actions.
        """

    def enable_actions(self, uimanager, _dummy_obj):
        """
        Enable page specific actions.
        """
        if self.action_group:
            uimanager.set_actions_visible(self.action_group, True)

    def disable_actions(self, uimanager):
        """
        Disable page specific actions.
        """
        if self.action_group:
            uimanager.set_actions_visible(self.action_group, False)

    def render_page(self, window, context):
        """
        Render the page contents.
        """
        if not context:
            return

        object_view = view_builder(self.grstate, context)
        self.active_profile = object_view.view_object
        window.pack_start(object_view, True, True, 0)
        self.post_render_page()

    def post_render_page(self):
        """
        Perform any post render page setup tasks.
        """

    def edit_active(self, *_dummy_obj):
        """
        Edit the active page object.
        """
        if self.active_profile:
            self.active_profile.edit_primary_object()

    def add_tag(self, trans, object_handle, tag_handle):
        """
        Add a tag to the active page object.
        """
        if self.active_profile:
            if (
                self.active_profile.primary.obj.get_handle()
                == object_handle[1]
            ):
                self.active_profile.primary.obj.add_tag(tag_handle)
                commit_method = self.grstate.dbstate.db.method(
                    "commit_%s", self.active_profile.primary.obj_type
                )
                commit_method(self.active_profile.primary.obj, trans)

    def _object_panel(self, configdialog, space, extra=False):
        """
        Build an object options panel.
        """
        group = "group" in space
        grid = create_grid()
        notebook = ConfigNotebook(vexpand=True, hexpand=True)
        page = build_person_grid(
            configdialog, self.grstate, space, "person", extra=extra
        )
        notebook.append_page(page, tab_label=Gtk.Label(label=_("Person")))
        render_page = lambda: build_person_grid(
            configdialog, self.grstate, space, "parent"
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Parent")), render_page
        )
        if "group" in space:
            render_page = lambda: build_person_grid(
                configdialog, self.grstate, space, "sibling"
            )
            notebook.append_deferred_page(
                Gtk.Label(label=_("Sibling")), render_page
            )
        render_page = lambda: build_person_grid(
            configdialog, self.grstate, space, "spouse"
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Spouse")), render_page
        )
        if "group" in space:
            render_page = lambda: build_person_grid(
                configdialog, self.grstate, space, "child"
            )
            notebook.append_deferred_page(
                Gtk.Label(label=_("Child")), render_page
            )
        render_page = lambda: build_person_grid(
            configdialog, self.grstate, space, "participant"
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Participant")), render_page
        )
        render_page = lambda: build_person_grid(
            configdialog, self.grstate, space, "association"
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Association")), render_page
        )
        render_page = lambda: build_family_grid(
            configdialog, self.grstate, space
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Family")), render_page
        )
        render_page = lambda: build_event_grid(
            configdialog, self.grstate, space
        )
        notebook.append_deferred_page(Gtk.Label(label=_("Event")), render_page)
        render_page = lambda: build_place_grid(
            configdialog, self.grstate, space
        )
        if "group" in space:
            render_page = lambda: build_ldsord_grid(
                configdialog, self.grstate, space, "ldsord"
            )
            notebook.append_deferred_page(
                Gtk.Label(label=_("LdsOrd")), render_page
            )
        notebook.append_deferred_page(Gtk.Label(label=_("Place")), render_page)
        render_page = lambda: build_citation_grid(
            configdialog, self.grstate, space
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Citation")), render_page
        )
        render_page = lambda: build_source_grid(
            configdialog, self.grstate, space
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Source")), render_page
        )
        render_page = lambda: build_repository_grid(
            configdialog, self.grstate, space
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Repository")), render_page
        )
        render_page = lambda: build_media_grid(
            configdialog, self.grstate, space, group=group
        )
        notebook.append_deferred_page(Gtk.Label(label=_("Media")), render_page)
        render_page = lambda: build_note_grid(
            configdialog, self.grstate, space
        )
        notebook.append_deferred_page(Gtk.Label(label=_("Note")), render_page)
        if "group" in space:
            render_page = lambda: build_name_grid(
                configdialog, self.grstate, space, "name"
            )
            notebook.append_deferred_page(
                Gtk.Label(label=_("Name")), render_page
            )
            render_page = lambda: build_address_grid(
                configdialog, self.grstate, space, "address"
            )
            notebook.append_deferred_page(
                Gtk.Label(label=_("Address")), render_page
            )
        grid.attach(notebook, 1, 0, 1, 1)
        return grid

    def global_panel(self, configdialog):
        """
        Build global options panel for the configuration dialog.
        """
        return _("Global"), build_global_grid(configdialog, self.grstate)

    def layout_panel(self, configdialog):
        """
        Build layout panel for the configuration dialog.
        """
        return _("Layout"), build_layout_grid(configdialog, self.grstate)

    def active_panel(self, configdialog):
        """
        Build active object options panel for the configuration dialog.
        """
        return _("Active"), self._object_panel(
            configdialog, "options.active", extra=True
        )

    def group_panel(self, configdialog):
        """
        Build object group options panel for the configuration dialog.
        """
        return _("Groups"), self._object_panel(configdialog, "options.group")

    def timeline_panel(self, configdialog):
        """
        Build timeline options panel for the configuration dialog.
        """
        grid = create_grid()
        notebook = ConfigNotebook(vexpand=True, hexpand=True)
        page = build_person_timeline_grid(configdialog, self.grstate)
        notebook.append_page(page, tab_label=Gtk.Label(label=_("Person")))
        render_page = lambda: build_family_timeline_grid(
            configdialog, self.grstate
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Family")), render_page
        )
        grid.attach(notebook, 1, 0, 1, 1)
        return _("Timelines"), grid

    def color_panel(self, configdialog):
        """
        Build color scheme options panel for the configuration dialog.
        """
        grid = create_grid()
        notebook = ConfigNotebook(vexpand=True, hexpand=True)
        page = build_color_grid(
            configdialog, self.grstate, CONFIDENCE_TYPE, CONFIDENCE_OPTIONS
        )
        notebook.append_page(page, tab_label=Gtk.Label(label=_("Confidence")))
        render_page = lambda: build_color_grid(
            configdialog, self.grstate, EVENT_TYPE, EVENT_OPTIONS
        )
        notebook.append_deferred_page(Gtk.Label(label=_("Event")), render_page)
        render_page = lambda: build_color_grid(
            configdialog, self.grstate, ROLE_TYPE, ROLE_OPTIONS
        )
        notebook.append_deferred_page(Gtk.Label(label=_("Role")), render_page)
        render_page = lambda: build_color_grid(
            configdialog, self.grstate, RELATION_TYPE, RELATION_OPTIONS
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Relationship")), render_page
        )
        grid.attach(notebook, 1, 0, 1, 1)
        return _("Colors"), grid

    def get_configure_page_funcs(self):
        """
        Return functions for generating configuration dialog notebook pages.
        """
        return [
            self.global_panel,
            self.layout_panel,
            self.active_panel,
            self.group_panel,
            self.timeline_panel,
            self.color_panel,
        ]
