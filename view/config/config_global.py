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
from .config_utils import add_config_reset, create_grid

_ = glocale.translation.sgettext


def build_display_grid(configdialog, grstate, *_dummy_args):
    """
    Build global display option configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Window Options"), 0, bold=True)
    configdialog.add_spinner(
        grid,
        _("Maximum number of open page copy windows to allow"),
        1,
        "options.global.display.max-page-windows",
        (1, 12),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum number of open object group windows to allow"),
        2,
        "options.global.display.max-group-windows",
        (1, 12),
    )
    configdialog.add_text(grid, _("Display Options"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Pin active header so it does not scroll"),
        11,
        "options.global.display.pin-header",
    )
    configdialog.add_checkbox(
        grid,
        _("Highlight the page focal object in header"),
        12,
        "options.global.display.focal-object-highlight",
    )
    add_color(
        grstate.config,
        grid,
        _("Focal object light themed highlight color"),
        "options.global.display.focal-object-color",
        (13, 1),
        0,
    )
    add_color(
        grstate.config,
        grid,
        _("Focal object dark themed highlight color"),
        "options.global.display.focal-object-color",
        (14, 1),
        1,
    )
    add_color(
        grstate.config,
        grid,
        _("Default frame light themed background color"),
        "options.global.display.default-background-color",
        (15, 1),
        0,
    )
    add_color(
        grstate.config,
        grid,
        _("Default frame dark themed background color"),
        "options.global.display.default-background-color",
        (16, 1),
        1,
    )
    configdialog.add_checkbox(
        grid,
        _("Enable coloring schemes"),
        17,
        "options.global.display.use-color-scheme",
    )
    configdialog.add_checkbox(
        grid,
        _("Use a smaller font for titles"),
        18,
        "options.global.display.use-smaller-title-font",
    )
    configdialog.add_checkbox(
        grid,
        _("Use a smaller font for details"),
        19,
        "options.global.display.use-smaller-detail-font",
    )
    configdialog.add_spinner(
        grid,
        _("Desired border width"),
        20,
        "options.global.display.border-width",
        (0, 5),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum icons to show per line in header frames."),
        21,
        "options.global.display.icons-active-width",
        (1, 40),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum icons to show per line in group frames."),
        22,
        "options.global.display.icons-group-width",
        (1, 40),
    )
    return add_config_reset(
        configdialog, grstate, "options.global.display", grid
    )


def build_maximums_grid(configdialog, grstate, *_dummy_args):
    """
    Build global group maximum option configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Group Maximums"), 0, bold=True)
    configdialog.add_spinner(
        grid,
        _("Maximum number of events to show in an events or timeline group"),
        1,
        "options.global.max.events-per-group",
        (1, 5000),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum number of places to show in a places group"),
        2,
        "options.global.max.places-per-group",
        (1, 5000),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum number of sources to show in a sources group"),
        3,
        "options.global.max.sources-per-group",
        (1, 5000),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum number of citations to show in a citations group"),
        4,
        "options.global.max.citations-per-group",
        (1, 5000),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum number of media items to show in a media group"),
        5,
        "options.global.max.media-per-group",
        (1, 5000),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum number of notes to show in a notes group"),
        6,
        "options.global.max.notes-per-group",
        (1, 5000),
    )
    configdialog.add_spinner(
        grid,
        _(
            "Maximum number of referencing objects to show in a references group"
        ),
        7,
        "options.global.max.references-per-group",
        (1, 5000),
    )
    return add_config_reset(configdialog, grstate, "options.global.max", grid)


def build_general_grid(configdialog, grstate, *_dummy_args):
    """
    Build global general option configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Behaviour Options"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Link images to the media page and not the image viewer"),
        11,
        "options.global.general.image-page-link",
    )
    configdialog.add_checkbox(
        grid,
        _("Link citation title to the source page and not citation page"),
        12,
        "options.global.general.link-citation-title-to-source",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Open second instance of association editor to add a reciprocal association"
        ),
        13,
        "options.global.general.create-reciprocal-associations",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include notes found on child objects in the context menu note items"
        ),
        14,
        "options.global.general.include-child-notes",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Parse and include urls found in notes in the url group when possible"
        ),
        15,
        "options.global.general.include-note-urls",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable warning dialogs when detaching or deleting objects"),
        16,
        "options.global.general.enable-warnings",
    )
    return add_config_reset(
        configdialog, grstate, "options.global.general", grid
    )


def build_indicator_grid(configdialog, grstate, *_dummy_args):
    """
    Build indicator configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Metadata Indicators"), 0, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable the display of Gramps ids"),
        1,
        "options.global.indicator.gramps-ids",
    )
    configdialog.add_combo(
        grid,
        _("Privacy indicator display mode"),
        2,
        "options.global.indicator.privacy",
        PRIVACY_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid,
        _("Enable bookmark indicator display and context menu support"),
        3,
        "options.global.indicator.bookmarks",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable home person indicator"),
        4,
        "options.global.indicator.home-person",
    )
    configdialog.add_text(grid, _("Tag Indicators"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable tag icons"),
        11,
        "options.global.indicator.tags",
    )
    configdialog.add_checkbox(
        grid,
        _("Sort tag icons based on tag name and not priority"),
        12,
        "options.global.indicator.tags-sort-by-name",
    )
    configdialog.add_text(grid, _("Child Object Indicators"), 20, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable associated child object indicator icons"),
        21,
        "options.global.indicator.child-objects",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable display of object counts with the indicator icons"),
        22,
        "options.global.indicator.child-objects-counts",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable alternate names indicator icon"),
        23,
        "options.global.indicator.names",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable parents indicator icon"),
        24,
        "options.global.indicator.parents",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable spouses indicator icon"),
        25,
        "options.global.indicator.spouses",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable children indicator icon"),
        26,
        "options.global.indicator.children",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable associations indicator icon"),
        27,
        "options.global.indicator.associations",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable events indicator icon"),
        28,
        "options.global.indicator.events",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable ordinances indicator icon"),
        29,
        "options.global.indicator.ordinances",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable media indicator icon"),
        30,
        "options.global.indicator.media",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable attributes indicator icon"),
        31,
        "options.global.indicator.attributes",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable addresses indicator icon"),
        32,
        "options.global.indicator.addresses",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable citations indicator icon"),
        33,
        "options.global.indicator.citations",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable notes indicator icon"),
        34,
        "options.global.indicator.notes",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable urls indicator icon"),
        35,
        "options.global.indicator.urls",
    )
    return add_config_reset(
        configdialog, grstate, "options.global.indicator", grid
    )


def build_media_bar_grid(configdialog, grstate, *_dummy_args):
    """
    Build media bar configuration section.
    """
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
    return add_config_reset(
        configdialog, grstate, "options.global.media-bar", grid
    )
