#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
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
from ..common.common_utils import make_scrollable
from ..services.service_fields import FieldCalculatorService
from ..services.service_status import StatusIndicatorService
from .config_colors import add_color
from .config_const import (
    HELP_CONFIG_DISPLAY,
    HELP_CONFIG_GENERAL,
    HELP_CONFIG_MENU,
    HELP_CONFIG_INDICATORS_BASIC,
    HELP_CONFIG_INDICATORS_STATUS,
    HELP_CONFIG_CALCULATED_FIELDS,
    HELP_CONFIG_MEDIA_BAR,
    MEDIA_DISPLAY_MODES,
    MEDIA_POSITION_MODES,
    PRIVACY_DISPLAY_MODES,
    GROUP_WRAPPER_MODES,
)
from .config_utils import (
    add_config_buttons,
    create_grid,
    HelpButton,
    TemplateCommentsEntry,
)

_ = glocale.translation.sgettext


def build_template_grid(configdialog, grstate, *_dummy_args):
    """
    Build template option configuration section.
    """
    comments_widget = TemplateCommentsEntry(grstate, "template.comments")
    grid = create_grid()
    configdialog.add_text(grid, _("Template Options"), 0, start=0, bold=True)
    configdialog.add_entry(grid, _("Description"), 1, "template.description")
    configdialog.add_text(grid, _("Comments:"), 2, start=0)
    grid.attach(comments_widget, 1, 2, 2, 1)
    return add_config_buttons(
        configdialog, grstate, "template", grid, HELP_CONFIG_DISPLAY
    )


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
        _("Focal object highlight color light scheme"),
        "display.focal-object-color",
        (13, 1),
        0,
    )
    add_color(
        grstate.config,
        grid,
        _("Focal object highlight color dark scheme"),
        "display.focal-object-color",
        (14, 1),
        1,
    )
    add_color(
        grstate.config,
        grid,
        _("Default card background color light scheme"),
        "display.default-background-color",
        (15, 1),
        0,
    )
    add_color(
        grstate.config,
        grid,
        _("Default card background color dark scheme"),
        "display.default-background-color",
        (16, 1),
        1,
    )
    add_color(
        grstate.config,
        grid,
        _("Default card foreground color light scheme"),
        "display.default-foreground-color",
        (17, 1),
        0,
    )
    add_color(
        grstate.config,
        grid,
        _("Default card foreground color dark scheme"),
        "display.default-foreground-color",
        (18, 1),
        1,
    )
    configdialog.add_checkbox(
        grid,
        _("Enable coloring schemes"),
        19,
        "display.use-color-scheme",
    )
    configdialog.add_checkbox(
        grid,
        _("Use a smaller font for titles"),
        20,
        "display.use-smaller-title-font",
    )
    configdialog.add_checkbox(
        grid,
        _("Use a smaller font for details"),
        21,
        "display.use-smaller-detail-font",
    )
    configdialog.add_checkbox(
        grid,
        _("Use smaller icons"),
        22,
        "display.use-smaller-icons",
    )
    configdialog.add_spinner(
        grid,
        _("Desired border width"),
        23,
        "display.border-width",
        (0, 3),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum icons to show per line in header cards."),
        24,
        "display.icons-active-width",
        (1, 40),
    )
    configdialog.add_spinner(
        grid,
        _("Maximum icons to show per line in group cards."),
        25,
        "display.icons-group-width",
        (1, 40),
    )
    configdialog.add_combo(
        grid,
        _("Group wrapper display mode"),
        26,
        "display.group-mode",
        GROUP_WRAPPER_MODES,
    )
    return add_config_buttons(
        configdialog, grstate, "display", grid, HELP_CONFIG_DISPLAY
    )


def build_general_grid(configdialog, grstate, *_dummy_args):
    """
    Build general option configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Behaviour Options"), 10, bold=True)
    configdialog.add_spinner(
        grid,
        _("Concurrent data collection threshold (requires restart)"),
        11,
        "general.concurrent-threshold",
        (1, 1000000),
    )
    configdialog.add_checkbox(
        grid,
        _("Link people to relationships instead of people category"),
        12,
        "general.link-people-to-relationships-view",
    )
    configdialog.add_checkbox(
        grid,
        _("Link images to the media page and not the image viewer"),
        13,
        "general.image-page-link",
    )
    configdialog.add_checkbox(
        grid,
        _("Link citation title to the source page and not citation page"),
        14,
        "general.link-citation-title-to-source",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Enable Zotero citation picking support with Better BibTex "
            "extension"
        ),
        15,
        "general.zotero-enabled",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable experimental Zotero source note imports"),
        16,
        "general.zotero-enabled-notes",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Open second instance of association editor to add a "
            "reciprocal association"
        ),
        17,
        "general.create-reciprocal-associations",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include notes found on child objects in the context menu "
            "note items"
        ),
        18,
        "general.include-child-notes",
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Parse and include urls found in notes in the url group "
            "when possible"
        ),
        19,
        "general.include-note-urls",
    )
    configdialog.add_spinner(
        grid,
        _(
            "Maximum number of referencing objects to show in a "
            "references group"
        ),
        20,
        "general.references-max-per-group",
        (1, 5000),
    )
    configdialog.add_checkbox(
        grid,
        _("Enable warning dialogs when detaching or deleting objects"),
        21,
        "general.enable-warnings",
    )
    return add_config_buttons(
        configdialog, grstate, "general", grid, HELP_CONFIG_GENERAL
    )


def build_menu_grid(configdialog, grstate, *_dummy_args):
    """
    Build global context menu option configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Context Menu Options"), 10, bold=True)
    configdialog.add_checkbox(
        grid, _("Enable delete option for selected object"), 11, "menu.delete"
    )
    configdialog.add_checkbox(
        grid,
        _("If delete enabled append delete to bottom of menu"),
        12,
        "menu.delete-bottom",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable delete option for objects in submenus"),
        13,
        "menu.delete-submenus",
    )
    configdialog.add_checkbox(
        grid, _("Enable set home person option"), 14, "menu.set-home-person"
    )
    configdialog.add_checkbox(
        grid, _("Enable go to person options"), 15, "menu.go-to-person"
    )
    configdialog.add_checkbox(
        grid,
        _("Enable parents submenu"),
        16,
        "menu.parents",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable spouses submenu"),
        17,
        "menu.spouses",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable associations submenu"),
        18,
        "menu.associations",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable participants submenu"),
        19,
        "menu.participants",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable names submenu"),
        20,
        "menu.names",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable attributes submenu"),
        21,
        "menu.attributes",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable ordinances submenu"),
        22,
        "menu.ordinances",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable enclosed places submenu"),
        23,
        "menu.enclosed-places",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable citations submenu"),
        24,
        "menu.citations",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable repositories submenu"),
        25,
        "menu.repositories",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable media submenu"),
        26,
        "menu.media",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable notes submenu"),
        27,
        "menu.notes",
    )
    configdialog.add_checkbox(
        grid,
        _("If notes enabled include child object notes"),
        28,
        "menu.notes-children",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable urls submenu"),
        29,
        "menu.urls",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable tags submenu"),
        30,
        "menu.tags",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable clipboard copy option"),
        31,
        "menu.clipboard",
    )
    configdialog.add_checkbox(
        grid,
        _("Enable bookmarks option"),
        32,
        "menu.bookmarks",
    )
    configdialog.add_checkbox(
        grid, _("Enable privacy option"), 33, "menu.privacy"
    )
    return add_config_buttons(
        configdialog, grstate, "menu", grid, HELP_CONFIG_MENU
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
        _("Enable bookmark indicator"),
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
    configdialog.add_spinner(
        grid,
        _("Maximum tag icons to display"),
        13,
        "indicator.tags-max-displayed",
        (1, 100),
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
    return add_config_buttons(
        configdialog, grstate, "indicator", grid, HELP_CONFIG_INDICATORS_BASIC
    )


def build_status_grid(configdialog, grstate, *_dummy_args):
    """
    Build status indicator configuration section.
    """
    grid = create_grid()
    status_indicator_service = StatusIndicatorService()
    status_grids = status_indicator_service.get_config_grids(
        configdialog, grstate
    )
    row = 1
    for status_grid in status_grids:
        grid.attach(status_grid, 1, row, 2, 1)
        row = row + 1
    vbox = Gtk.VBox(margin=12)
    vbox.pack_start(grid, True, True, 0)
    hbox = Gtk.HBox()
    hbox.pack_start(HelpButton(HELP_CONFIG_INDICATORS_STATUS), False, False, 0)
    vbox.pack_start(hbox, False, False, 0)
    return make_scrollable(vbox, hexpand=True)


def build_field_grid(configdialog, grstate, *_dummy_args):
    """
    Build calculated field configuration section.
    """
    grid = create_grid()
    field_calculator_service = FieldCalculatorService()
    field_grids = field_calculator_service.get_config_grids(
        configdialog, grstate
    )
    row = 1
    for field_grid in field_grids:
        if field_grid:
            grid.attach(field_grid, 1, row, 2, 1)
            row = row + 1
    if row == 1:
        return None
    vbox = Gtk.VBox(margin=12)
    vbox.pack_start(grid, True, True, 0)
    hbox = Gtk.HBox()
    hbox.pack_start(HelpButton(HELP_CONFIG_CALCULATED_FIELDS), False, False, 0)
    vbox.pack_start(hbox, False, False, 0)
    return make_scrollable(vbox, hexpand=True)


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
    return add_config_buttons(
        configdialog, grstate, "media-bar", grid, HELP_CONFIG_MEDIA_BAR
    )
