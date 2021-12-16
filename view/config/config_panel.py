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
from gramps.gen.const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from .config_colors import (
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
from .config_global import (
    build_display_grid,
    build_general_grid,
    build_indicator_grid,
    build_media_bar_grid,
)
from .config_objects import (
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
from .config_timeline import (
    build_family_timeline_grid,
    build_person_timeline_grid,
)
from .config_utils import create_grid

_ = glocale.translation.sgettext


def build_global_panel(configdialog, grstate, *_dummy_args):
    """
    Build timeline options panel for the configuration dialog.
    """
    grid = create_grid()
    notebook = ConfigNotebook(vexpand=True, hexpand=True)
    page = build_display_grid(configdialog, grstate)
    notebook.append_page(page, tab_label=Gtk.Label(label=_("Display")))
    render_page = lambda: build_general_grid(configdialog, grstate)
    notebook.append_deferred_page(Gtk.Label(label=_("General")), render_page)
    render_page = lambda: build_indicator_grid(configdialog, grstate)
    notebook.append_deferred_page(
        Gtk.Label(label=_("Indicators")), render_page
    )
    render_page = lambda: build_media_bar_grid(configdialog, grstate)
    notebook.append_deferred_page(Gtk.Label(label=_("Media Bar")), render_page)
    grid.attach(notebook, 1, 0, 1, 1)
    return grid


def build_object_panel(configdialog, grstate, space):
    """
    Build an object options panel.
    """
    grid = create_grid()
    notebook = ConfigNotebook(vexpand=True, hexpand=True)
    page = build_person_grid(configdialog, grstate, space, "person")
    notebook.append_page(page, tab_label=Gtk.Label(label=_("Person")))
    render_page = lambda: build_person_grid(
        configdialog, grstate, space, "parent"
    )
    notebook.append_deferred_page(Gtk.Label(label=_("Parent")), render_page)
    if "group" in space:
        render_page = lambda: build_person_grid(
            configdialog, grstate, space, "sibling"
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Sibling")), render_page
        )
    render_page = lambda: build_person_grid(
        configdialog, grstate, space, "spouse"
    )
    notebook.append_deferred_page(Gtk.Label(label=_("Spouse")), render_page)
    if "group" in space:
        render_page = lambda: build_person_grid(
            configdialog, grstate, space, "child"
        )
        notebook.append_deferred_page(Gtk.Label(label=_("Child")), render_page)
    render_page = lambda: build_person_grid(
        configdialog, grstate, space, "association"
    )
    notebook.append_deferred_page(
        Gtk.Label(label=_("Association")), render_page
    )
    render_page = lambda: build_family_grid(configdialog, grstate, space)
    notebook.append_deferred_page(Gtk.Label(label=_("Family")), render_page)
    render_page = lambda: build_event_grid(configdialog, grstate, space)
    notebook.append_deferred_page(Gtk.Label(label=_("Event")), render_page)
    render_page = lambda: build_place_grid(configdialog, grstate, space)
    if "group" in space:
        render_page = lambda: build_ldsord_grid(
            configdialog, grstate, space, "ldsord"
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("LdsOrd")), render_page
        )
    notebook.append_deferred_page(Gtk.Label(label=_("Place")), render_page)
    render_page = lambda: build_citation_grid(configdialog, grstate, space)
    notebook.append_deferred_page(Gtk.Label(label=_("Citation")), render_page)
    render_page = lambda: build_source_grid(configdialog, grstate, space)
    notebook.append_deferred_page(Gtk.Label(label=_("Source")), render_page)
    render_page = lambda: build_repository_grid(configdialog, grstate, space)
    notebook.append_deferred_page(
        Gtk.Label(label=_("Repository")), render_page
    )
    render_page = lambda: build_media_grid(configdialog, grstate, space)
    notebook.append_deferred_page(Gtk.Label(label=_("Media")), render_page)
    render_page = lambda: build_note_grid(configdialog, grstate, space)
    notebook.append_deferred_page(Gtk.Label(label=_("Note")), render_page)
    if "group" in space:
        render_page = lambda: build_name_grid(
            configdialog, grstate, space, "name"
        )
        notebook.append_deferred_page(Gtk.Label(label=_("Name")), render_page)
        render_page = lambda: build_address_grid(
            configdialog, grstate, space, "address"
        )
        notebook.append_deferred_page(
            Gtk.Label(label=_("Address")), render_page
        )
    grid.attach(notebook, 1, 0, 1, 1)
    return grid


def build_timeline_panel(configdialog, grstate):
    """
    Build timeline options panel for the configuration dialog.
    """
    grid = create_grid()
    notebook = ConfigNotebook(vexpand=True, hexpand=True)
    page = build_person_timeline_grid(configdialog, grstate)
    notebook.append_page(page, tab_label=Gtk.Label(label=_("Person")))
    render_page = lambda: build_family_timeline_grid(configdialog, grstate)
    notebook.append_deferred_page(Gtk.Label(label=_("Family")), render_page)
    grid.attach(notebook, 1, 0, 1, 1)
    return grid


def build_color_panel(configdialog, grstate):
    """
    Build color scheme options panel for the configuration dialog.
    """
    grid = create_grid()
    notebook = ConfigNotebook(vexpand=True, hexpand=True)
    page = build_color_grid(
        configdialog, grstate, CONFIDENCE_TYPE, CONFIDENCE_OPTIONS
    )
    notebook.append_page(page, tab_label=Gtk.Label(label=_("Confidence")))
    render_page = lambda: build_color_grid(
        configdialog, grstate, EVENT_TYPE, EVENT_OPTIONS
    )
    notebook.append_deferred_page(Gtk.Label(label=_("Event")), render_page)
    render_page = lambda: build_color_grid(
        configdialog, grstate, ROLE_TYPE, ROLE_OPTIONS
    )
    notebook.append_deferred_page(Gtk.Label(label=_("Role")), render_page)
    render_page = lambda: build_color_grid(
        configdialog, grstate, RELATION_TYPE, RELATION_OPTIONS
    )
    notebook.append_deferred_page(
        Gtk.Label(label=_("Relationship")), render_page
    )
    grid.attach(notebook, 1, 0, 1, 1)
    return grid
