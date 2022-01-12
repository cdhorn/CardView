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
    CONFIDENCE_LEVEL,
    MEDIA_DISPLAY_MODES,
    MEDIA_POSITION_MODES,
    PRIVACY_DISPLAY_MODES,
)
from .config_utils import add_config_reset, config_event_fields, create_grid

_ = glocale.translation.sgettext


def build_display_grid(configdialog, grstate, *_dummy_args):
    """
    Build display option configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Window Options"), 0, bold=True)
    configdialog.add_spinner(
        grid,
        _("Maximum number of open page copy windows to allow"),
        1,
        "display.max-page-windows",
        (1, 12),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum number of open object group windows to allow"),
        2,
        "display.max-group-windows",
        (1, 12),
    )
    configdialog.add_text(grid, _("Display Options"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Pin active header so it does not scroll"),
        11,
        "display.pin-header",
    )
    configdialog.add_checkbox(
        grid,
        _("Highlight the page focal object in header"),
        12,
        "display.focal-object-highlight",
    )
    add_color(
        grstate.config,
        grid,
        _("Focal object light themed highlight color"),
        "display.focal-object-color",
        (13, 1),
        0,
    )
    add_color(
        grstate.config,
        grid,
        _("Focal object dark themed highlight color"),
        "display.focal-object-color",
        (14, 1),
        1,
    )
    add_color(
        grstate.config,
        grid,
        _("Default frame light themed background color"),
        "display.default-background-color",
        (15, 1),
        0,
    )
    add_color(
        grstate.config,
        grid,
        _("Default frame dark themed background color"),
        "display.default-background-color",
        (16, 1),
        1,
    )
    configdialog.add_checkbox(
        grid,
        _("Enable coloring schemes"),
        17,
        "display.use-color-scheme",
    )
    configdialog.add_checkbox(
        grid,
        _("Use a smaller font for titles"),
        18,
        "display.use-smaller-title-font",
    )
    configdialog.add_checkbox(
        grid,
        _("Use a smaller font for details"),
        19,
        "display.use-smaller-detail-font",
    )
    configdialog.add_spinner(
        grid,
        _("Desired border width"),
        20,
        "display.border-width",
        (0, 5),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum icons to show per line in header frames."),
        21,
        "display.icons-active-width",
        (1, 40),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum icons to show per line in group frames."),
        22,
        "display.icons-group-width",
        (1, 40),
    )
    return add_config_reset(configdialog, grstate, "display", grid)


def build_general_grid(configdialog, grstate, *_dummy_args):
    """
    Build general option configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Behaviour Options"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Link images to the media page and not the image viewer"),
        11,
        "general.image-page-link",
    )
    configdialog.add_checkbox(
        grid,
        _("Link citation title to the source page and not citation page"),
        12,
        "general.link-citation-title-to-source",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Enable Zotero citation picking support with Better BibTex "
            "extension"
        ),
        13,
        "general.zotero-enabled",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable experimental Zotero source note imports"),
        14,
        "general.zotero-enabled-notes",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Open second instance of association editor to add a "
            "reciprocal association"
        ),
        15,
        "general.create-reciprocal-associations",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include notes found on child objects in the context menu "
            "note items"
        ),
        16,
        "general.include-child-notes",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Parse and include urls found in notes in the url group "
            "when possible"
        ),
        17,
        "general.include-note-urls",
    )
    configdialog.add_spinner(
        grid,
        _(
            "Maximum number of referencing objects to show in a "
            "references group"
        ),
        19,
        "general.references-max-per-group",
        (1, 5000),
    )
    configdialog.add_checkbox(
        grid,
        _("Enable warning dialogs when detaching or deleting objects"),
        20,
        "general.enable-warnings",
    )
    return add_config_reset(configdialog, grstate, "general", grid)


def build_menu_grid(configdialog, grstate, *_dummy_args):
    """
    Build global context menu option configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Context Menu Options"), 10, bold=True)
    configdialog.add_checkbox(
        grid, _("Enable delete option for primary objects"), 11, "menu.delete"
    )
    configdialog.add_checkbox(
        grid,
        _("If enabled append delete option at bottom of menu"),
        12,
        "menu.delete-bottom",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable delete option for primary objects in submenus"),
        13,
        "menu.delete-submenus",
    )
    configdialog.add_checkbox(
        grid, _("Enable set home option"), 14, "menu.set-home"
    )
    configdialog.add_checkbox(
        grid,
        _("Enable parents submenu"),
        15,
        "menu.parents",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable spouses submenu"),
        16,
        "menu.spouses",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable associations submenu"),
        17,
        "menu.associations",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable names submenu"),
        18,
        "menu.names",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable ordinances submenu"),
        19,
        "menu.ordinances",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable attributes submenu"),
        20,
        "menu.attributes",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable participants submenu"),
        21,
        "menu.participants",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable urls submenu"),
        22,
        "menu.urls",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable bookmarks option"),
        23,
        "menu.bookmarks",
    )
    configdialog.add_checkbox(
        grid, _("Enable privacy option"), 24, "menu.privacy"
    )
    return add_config_reset(configdialog, grstate, "menu", grid)


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
        "indicator.gramps-ids",
    )
    configdialog.add_combo(
        grid,
        _("Privacy indicator display mode"),
        2,
        "indicator.privacy",
        PRIVACY_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid,
        _("Enable bookmark indicator display and context menu support"),
        3,
        "indicator.bookmarks",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable home person indicator"),
        4,
        "indicator.home-person",
    )
    configdialog.add_text(grid, _("Tag Indicators"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable tag icons"),
        11,
        "indicator.tags",
    )
    configdialog.add_checkbox(
        grid,
        _("Sort tag icons based on tag name and not priority"),
        12,
        "indicator.tags-sort-by-name",
    )
    configdialog.add_text(grid, _("Child Object Indicators"), 20, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable associated child object indicator icons"),
        21,
        "indicator.child-objects",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable display of object counts with the indicator icons"),
        22,
        "indicator.child-objects-counts",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable alternate names indicator icon"),
        23,
        "indicator.names",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable parents indicator icon"),
        24,
        "indicator.parents",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable spouses indicator icon"),
        25,
        "indicator.spouses",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable children indicator icon"),
        26,
        "indicator.children",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable associations indicator icon"),
        27,
        "indicator.associations",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable events indicator icon"),
        28,
        "indicator.events",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable ordinances indicator icon"),
        29,
        "indicator.ordinances",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable media indicator icon"),
        30,
        "indicator.media",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable attributes indicator icon"),
        31,
        "indicator.attributes",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable addresses indicator icon"),
        32,
        "indicator.addresses",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable citations indicator icon"),
        33,
        "indicator.citations",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable notes indicator icon"),
        34,
        "indicator.notes",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable urls indicator icon"),
        35,
        "indicator.urls",
    )
    return add_config_reset(configdialog, grstate, "indicator", grid)


def build_status_grid(configdialog, grstate, *_dummy_args):
    """
    Build status indicator configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("To Do Indicator"), 0, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable to do indicator icon"),
        1,
        "status.todo",
    )
    configdialog.add_checkbox(
        grid,
        _("Open note in editor instead of navigating to note page"),
        2,
        "status.todo-edit",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable full person to do evaluation"),
        3,
        "status.todo-person",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable full family to do evaluation"),
        4,
        "status.todo-family",
    )
    configdialog.add_text(
        grid, _("Confidence Ranking Indicator"), 20, bold=True
    )
    configdialog.add_checkbox(
        grid,
        _("Enable confidence ranking"),
        21,
        "status.confidence-ranking",
    )
    configdialog.add_checkbox(
        grid,
        _("Include base object"),
        22,
        "status.rank-object",
    )
    grid1 = create_grid()
    configdialog.add_checkbox(
        grid1,
        _("Include all names"),
        23,
        "status.rank-names",
    )
    configdialog.add_checkbox(
        grid1,
        _("Include all events"),
        24,
        "status.rank-events",
    )
    configdialog.add_checkbox(
        grid1,
        _("Include all ordinances"),
        25,
        "status.rank-ordinances",
    )
    configdialog.add_checkbox(
        grid1,
        _("Include spouses for family"),
        26,
        "status.rank-spouses",
    )
    grid2 = create_grid()
    configdialog.add_checkbox(
        grid2,
        _("Include all attributes"),
        23,
        "status.rank-attributes",
        start=3,
    )
    configdialog.add_checkbox(
        grid2,
        _("Include all associations"),
        24,
        "status.rank-associations",
        start=3,
    )
    configdialog.add_checkbox(
        grid2,
        _("Include all addresses"),
        25,
        "status.rank-addresses",
        start=3,
    )
    configdialog.add_checkbox(
        grid2,
        _("Include children for family"),
        26,
        "status.rank-children",
        start=3,
    )
    grid.attach(grid1, 1, 24, 2, 1)
    grid.attach(grid2, 2, 24, 2, 1)
    configdialog.add_text(
        grid,
        "".join(
            (
                _(
                    "Additional Individual Events To Include "
                    "(Birth and Death Implicit)"
                ),
                ":",
            )
        ),
        25,
    )
    grid3 = config_event_fields(grstate, "rank")
    grid.attach(grid3, 1, 26, 2, 1)
    configdialog.add_text(grid, _("Citation Alert Indicator"), 50, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable citation alerts"),
        51,
        "status.citation-alert",
    )
    configdialog.add_combo(
        grid,
        _("Minimum confidence level required"),
        52,
        "status.citation-alert-minimum",
        CONFIDENCE_LEVEL,
    )
    configdialog.add_checkbox(
        grid,
        _("Open event in editor instead of navigating to event page"),
        53,
        "status.citation-alert-edit",
    )
    configdialog.add_text(
        grid, "".join((_("Events Checked For Citations"), ":")), 54
    )
    grid1 = config_event_fields(grstate, "alert")
    grid.attach(grid1, 1, 55, 2, 2)
    configdialog.add_text(grid, _("Missing Event Indicator"), 60, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable missing event alerts"),
        61,
        "status.missing-alert",
    )
    configdialog.add_text(grid, "".join((_("Required Events"), ":")), 62)
    grid1 = config_event_fields(grstate, "missing", count=6)
    grid.attach(grid1, 1, 63, 2, 1)
    return add_config_reset(configdialog, grstate, "status", grid)


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
        "media-bar.enabled",
    )
    configdialog.add_combo(
        grid,
        _("Media bar position"),
        2,
        "media-bar.position",
        MEDIA_POSITION_MODES,
    )
    configdialog.add_combo(
        grid,
        _("Media display mode"),
        3,
        "media-bar.display-mode",
        MEDIA_DISPLAY_MODES,
    )
    configdialog.add_spinner(
        grid,
        _(
            "Minimum number of media items required for the bar to be displayed"
        ),
        4,
        "media-bar.minimum-required",
        (1, 12),
    )
    configdialog.add_text(grid, _("Behaviour Options"), 10, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Sort the displayed media items by date"),
        11,
        "media-bar.sort-by-date",
    )
    configdialog.add_checkbox(
        grid,
        _("Group media by type, requires the Media-Type attribute be set"),
        12,
        "media-bar.group-by-type",
    )
    configdialog.add_checkbox(
        grid,
        _("Filter out non-photos, requires the Media-Type attribute be set"),
        13,
        "media-bar.filter-non-photos",
    )
    configdialog.add_checkbox(
        grid,
        _("Link images to the media page and not the image viewer"),
        14,
        "media-bar.page-link",
    )
    return add_config_reset(configdialog, grstate, "media-bar", grid)
