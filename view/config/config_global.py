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
Global configuration dialog functions
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
from .config_colors import add_color
from .config_const import (
    MEDIA_DISPLAY_MODES,
    MEDIA_POSITION_MODES,
    PRIVACY_DISPLAY_MODES,
)
from .config_objects import ConfigNotebook
from .config_utils import add_config_reset, create_grid

_ = glocale.translation.sgettext


def build_global_grid(configdialog, grstate, *_dummy_args):
    """
    Build global option configuration section.
    """
    notebook = ConfigNotebook(vexpand=True, hexpand=True)

    grid = create_grid()
    configdialog.add_text(grid, _("Window Options"), 0, bold=True)
    configdialog.add_spinner(
        grid,
        _("Maximum number of open page copy windows to allow"),
        1,
        "options.global.max-page-windows",
        (1, 12),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum number of open object group windows to allow"),
        2,
        "options.global.max-group-windows",
        (1, 12),
    )
    configdialog.add_text(grid, _("Display Options"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Pin active header so it does not scroll"),
        11,
        "options.global.pin-header",
        tooltip=_(
            "Enabling this option pins the page header so it will not scroll "
            "with the rest of the view."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Highlight the page focal object in header"),
        12,
        "options.global.focal-object-highlight",
    )
    add_color(
        grstate.config,
        grid,
        _("Focal object highlight color"),
        "options.global.focal-object-color",
        (13, 1),
    )
    add_color(
        grstate.config,
        grid,
        _("Default frame background color"),
        "options.global.default-background-color",
        (14, 1),
    )
    configdialog.add_checkbox(
        grid,
        _("Enable coloring schemes"),
        15,
        "options.global.use-color-scheme",
        tooltip=_(
            "Enabling this option enables coloring schemes for the rendered "
            "frames. People and families currently use the default Gramps "
            "color scheme defined in the global preferences. This view also "
            "supports other user customizable color schemes to choose from "
            "for some of the object groups such as the timeline and citations."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Use a smaller font for titles"),
        16,
        "options.global.use-smaller-title-font",
        tooltip=_(
            "Indicates whether to use a smaller font for the titles than "
            "the Gramps default."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Use a smaller font for details"),
        17,
        "options.global.use-smaller-detail-font",
        tooltip=_(
            "Indicates whether to use a smaller font for the details than "
            "the Gramps default."
        ),
    )
    configdialog.add_spinner(
        grid,
        _("The desired border width"),
        18,
        "options.global.border-width",
        (0, 5),
    )
    configdialog.add_text(grid, _("Limit Options"), 20, bold=True)
    configdialog.add_spinner(
        grid,
        _("Maximum number of citations to show in a citations group"),
        21,
        "options.global.max-citations-per-group",
        (1, 500),
    )
    configdialog.add_spinner(
        grid,
        _(
            "Maximum number of referencing objects to show in a references group"
        ),
        22,
        "options.global.max-references-per-group",
        (1, 500),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum icons to show per line in header frames."),
        23,
        "options.global.icons-active-width",
        (1, 40),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum icons to show per line in group frames."),
        24,
        "options.global.icons-group-width",
        (1, 40),
    )
    configdialog.add_text(grid, _("Behaviour Options"), 30, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Link images to the media page and not the image viewer"),
        31,
        "options.global.image-page-link",
    )
    configdialog.add_checkbox(
        grid,
        _("Link citation title to the source page and not citation page"),
        32,
        "options.global.link-citation-title-to-source",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Open second instance of association editor to add a reciprocal association"
        ),
        33,
        "options.global.create-reciprocal-associations",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include notes found on child objects in the context menu note items"
        ),
        34,
        "options.global.include-child-notes",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Parse and include urls found in notes in the url group when possible"
        ),
        35,
        "options.global.include-note-urls",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable warning dialogs when detaching or deleting objects"),
        36,
        "options.global.enable-warnings",
    )
    #    add_config_reset(configdialog, grstate, "options.global", grid)
    notebook.append_page(grid, tab_label=Gtk.Label(label=_("Defaults")))

    grid = create_grid()
    configdialog.add_text(grid, _("Metadata Indicators"), 0, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable the display of Gramps ids"),
        1,
        "options.global.enable-gramps-ids",
    )
    configdialog.add_combo(
        grid,
        _("Privacy indicator display mode"),
        2,
        "options.global.privacy-mode",
        PRIVACY_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid,
        _("Enable bookmark indicator display and context menu support"),
        3,
        "options.global.enable-bookmarks",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable home person indicator"),
        4,
        "options.global.enable-home",
    )
    configdialog.add_text(grid, _("Tag Indicators"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable tag icons"),
        11,
        "options.global.icons-enable-tags",
    )
    configdialog.add_checkbox(
        grid,
        _("Sort tag icons based on tag name and not priority"),
        12,
        "options.global.sort-tags-by-name",
    )
    configdialog.add_text(grid, _("Child Object Indicators"), 20, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable associated child object indicator icons"),
        21,
        "options.global.icons-enable-indicators",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable display of object counts with the indicator icons"),
        22,
        "options.global.enable-indicator-counts",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable alternate names indicator icon"),
        23,
        "options.global.indicate-names",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable parents indicator icon"),
        24,
        "options.global.indicate-parents",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable spouses indicator icon"),
        25,
        "options.global.indicate-spouses",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable children indicator icon"),
        26,
        "options.global.indicate-children",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable associations indicator icon"),
        27,
        "options.global.indicate-associations",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable events indicator icon"),
        28,
        "options.global.indicate-events",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable ordinances indicator icon"),
        29,
        "options.global.indicate-ordinances",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable media indicator icon"),
        30,
        "options.global.indicate-media",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable attributes indicator icon"),
        31,
        "options.global.indicate-attributes",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable addresses indicator icon"),
        32,
        "options.global.indicate-addresses",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable citations indicator icon"),
        33,
        "options.global.indicate-citations",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable notes indicator icon"),
        34,
        "options.global.indicate-notes",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable urls indicator icon"),
        35,
        "options.global.indicate-urls",
    )
    #    add_config_reset(configdialog, grstate, "options.global", grid)
    notebook.append_page(grid, tab_label=Gtk.Label(label=_("Indicators")))

    grid = create_grid()
    configdialog.add_text(grid, _("Display Options"), 0, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable the compact media bar"),
        1,
        "options.global.media-bar.enabled",
    )
    configdialog.add_combo(
        grid,
        _("Media bar position"),
        2,
        "options.global.media-bar.position",
        MEDIA_POSITION_MODES,
    )
    configdialog.add_combo(
        grid,
        _("Media display mode"),
        3,
        "options.global.media-bar.display-mode",
        MEDIA_DISPLAY_MODES,
    )
    configdialog.add_spinner(
        grid,
        _(
            "Minimum number of media items required for the bar to be displayed"
        ),
        4,
        "options.global.media-bar.minimum-required",
        (1, 12),
    )
    configdialog.add_text(grid, _("Behaviour Options"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Sort the displayed media items by date"),
        11,
        "options.global.media-bar.sort-by-date",
    )
    configdialog.add_checkbox(
        grid,
        _("Group media by type, requires the Media-Type attribute be set"),
        12,
        "options.global.media-bar.group-by-type",
    )
    configdialog.add_checkbox(
        grid,
        _("Filter out non-photos, requires the Media-Type attribute be set"),
        13,
        "options.global.media-bar.filter-non-photos",
    )
    configdialog.add_checkbox(
        grid,
        _("Link images to the media page and not the image viewer"),
        14,
        "options.global.media-bar.page-link",
    )
    #    add_config_reset(configdialog, grstate, "options.global.media-bar", grid)
    notebook.append_page(grid, tab_label=Gtk.Label(label=_("Media Bar")))

    grid = create_grid()
    grid.attach(notebook, 1, 0, 1, 1)
    return grid
