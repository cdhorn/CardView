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
Base Profile Page
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
from gramps.gen.const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..bars.bar_media import GrampsMediaBarGroup
from ..common.common_classes import GrampsState
from ..common.common_const import GROUP_LABELS
from ..groups.group_const import OBJECT_GROUPS
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
    build_citation_grid,
    build_event_grid,
    build_family_grid,
    build_media_grid,
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

_ = glocale.translation.sgettext


class BaseProfilePage:
    """
    Provides functionality common to all object profile page views.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        self.grstate = GrampsState(dbstate, uistate, callbacks, config)
        self.grstate.set_page_type(self.page_type.lower())
        self.config = config
        self.container = None
        self.active_profile = None

    @property
    def page_type(self):
        """
        Return page type.
        """

    def edit_active(self, *_dummy_obj):
        """
        Edit the active page object.
        """
        if self.active_profile:
            self.active_profile.edit_object()

    def add_tag(self, trans, object_handle, tag_handle):
        """
        Add a tag to the active page object.
        """
        if self.active_profile:
            if self.active_profile.obj.get_handle() == object_handle[1]:
                self.active_profile.obj.add_tag(tag_handle)
                commit_method = self.grstate.dbstate.db.method(
                    "commit_%s", self.active_profile.obj_type
                )
                commit_method(self.active_profile.obj, trans)

    def get_object_groups(self, groups, obj, age_base=None):
        """
        Gather the object groups.
        """
        obj_groups = {}
        for key in groups:
            if key in OBJECT_GROUPS:
                obj_groups.update(
                    {
                        key: OBJECT_GROUPS[key](
                            self.grstate, obj, age_base=age_base
                        )
                    }
                )
        return obj_groups

    def add_media_bar(self, widget, obj):
        """
        Check and if need and can build media bar add to widget for viewing.
        """
        if self.config.get("options.global.media-bar-display-mode"):
            css = self.active_profile.get_css_style()
            mediabar = GrampsMediaBarGroup(self.grstate, None, obj, css=css)
            if mediabar.total:
                widget.pack_start(mediabar, False, False, 0)

    def render_group_view(self, obj_groups):
        """
        Identify group view type and call method to render it.
        """
        space = "options.page.{}.layout".format(self.page_type.lower())
        groups = self.config.get("{}.groups".format(space)).split(",")
        if self.config.get("{}.tabbed".format(space)):
            return self.render_tabbed_group(obj_groups, space, groups)
        return self.render_untabbed_group(obj_groups, space, groups)

    def render_untabbed_group(self, obj_groups, space, groups):
        """
        Generate untabbed full page view for the groups.
        """
        gbox = None
        title = ""
        scrolled = self.config.get("{}.scrolled".format(space))
        self.container = Gtk.HBox(spacing=3)
        for group in groups:
            add_group = True
            if group not in obj_groups or not obj_groups[group]:
                add_group = False
            if not self.config.get("{}.{}.visible".format(space, group)):
                add_group = False
            if not gbox:
                gbox = Gtk.VBox(spacing=3)
            if add_group:
                gbox.pack_start(
                    obj_groups[group], expand=False, fill=True, padding=0
                )
            if not title:
                title = GROUP_LABELS[group]
            else:
                if " & " in title:
                    title = title.replace(" &", ",")
                title = "{} & {}".format(title, GROUP_LABELS[group])
            if not self.config.get("{}.{}.stacked".format(space, group)):
                if scrolled:
                    self.container.pack_start(
                        self._scrolled(gbox),
                        expand=False,
                        fill=True,
                        padding=0,
                    )
                else:
                    self.container.pack_start(
                        gbox, expand=False, fill=True, padding=0
                    )
                gbox = None
                title = ""
        if gbox and title:
            if scrolled:
                self.container.pack_start(
                    self._scrolled(gbox), expand=True, fill=True, padding=0
                )
            else:
                self.container.pack_start(
                    gbox, expand=False, fill=True, padding=0
                )
        return self.container

    def render_tabbed_group(self, obj_groups, space, groups):
        """
        Generate tabbed notebook view for the groups.
        """
        sbox = None
        title = ""
        in_stack = False
        container = Gtk.Notebook()
        for group in groups:
            add_group = True
            if group not in obj_groups or not obj_groups[group]:
                add_group = False
            if not self.config.get("{}.{}.visible".format(space, group)):
                add_group = False
            gbox = Gtk.VBox(spacing=3)
            if add_group:
                gbox.pack_start(
                    obj_groups[group], expand=True, fill=True, padding=0
                )
                if not title:
                    title = GROUP_LABELS[group]
                else:
                    if " & " in title:
                        title = title.replace(" &", ",")
                    title = "{} & {}".format(title, GROUP_LABELS[group])
            if self.config.get("{}.{}.stacked".format(space, group)):
                in_stack = True
                if not sbox:
                    sbox = Gtk.HBox(spacing=3)
                sbox.pack_start(gbox, expand=True, fill=True, padding=0)
            else:
                if not in_stack:
                    obox = gbox
                else:
                    sbox.pack_start(gbox, expand=True, fill=True, padding=0)
                    obox = Gtk.VBox()
                    obox.add(sbox)
                    in_stack = False
            if not in_stack:
                label = Gtk.Label(label=title)
                container.append_page(self._scrolled(obox), tab_label=label)
                sbox = None
                title = ""
        if obox and title:
            label = Gtk.Label(label=title)
            container.append_page(self._scrolled(obox), tab_label=label)
        return container

    def _scrolled(self, widget):
        scroll = Gtk.ScrolledWindow(hexpand=False, vexpand=True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        viewport = Gtk.Viewport()
        viewport.add(widget)
        scroll.add(viewport)
        return scroll

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
