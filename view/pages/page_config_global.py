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
from .page_config_colors import add_color, update_color
from .page_const import (
    MEDIA_DISPLAY_MODES,
    MEDIA_POSITION_MODES,
    PRIVACY_DISPLAY_MODES,
)
from .page_utils import add_config_reset, create_grid

_ = glocale.translation.sgettext


def build_global_grid(configdialog, grstate):
    """
    Build global option configuration section.
    """
    grid = create_grid()
    grid1 = create_grid()
    configdialog.add_text(grid1, _("Global Options"), 0, bold=True)
    configdialog.add_spinner(
        grid1,
        _("Maximum number of page copy windows"),
        1,
        "options.global.max-page-windows",
        (1, 12),
    )
    configdialog.add_checkbox(
        grid1,
        _("Pin active header so it does not scroll"),
        2,
        "options.global.pin-header",
        tooltip=_(
            "Enabling this option pins the page header so it will not scroll "
            "with the rest of the view."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Enable coloring schemes"),
        3,
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
        grid1,
        _("Use smaller font for details"),
        4,
        "options.global.use-smaller-detail-font",
        tooltip=_(
            "Indicates whether to use a smaller font for the details than "
            "used for the title."
        ),
    )
    configdialog.add_spinner(
        grid1,
        _("Desired border width"),
        5,
        "options.global.border-width",
        (0, 5),
    )
    configdialog.add_checkbox(
        grid1,
        _("Highlight focal object"),
        6,
        "options.global.focal-object-highlight",
        tooltip=_(
            "Indicates whether to highlight the focal object frame in the "
            "page header or not."
        ),
    )
    add_color(
        grstate.config,
        grid1,
        _("Focal object highlight color"),
        "options.global.focal-object-color",
        (7, 1),
    )
    add_color(
        grstate.config,
        grid1,
        _("Default frame background color"),
        "options.global.default-background-color",
        (8, 1),
    )
    configdialog.add_checkbox(
        grid1,
        _("Enable gramps ids"),
        10,
        "options.global.enable-gramps-ids",
        tooltip=_(
            "Indicates whether to show the Gramps id for primary objects "
            "or not."
        ),
    )
    configdialog.add_combo(
        grid1,
        _("Privacy display mode"),
        11,
        "options.global.privacy-mode",
        PRIVACY_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid1,
        _("Enable bookmark support"),
        12,
        "options.global.enable-bookmarks",
        tooltip=_("Indicates whether to enable bookmark support or not."),
    )
    configdialog.add_checkbox(
        grid1,
        _("Enable home indicator"),
        13,
        "options.global.enable-home",
        tooltip=_(
            "Indicates whether to enable default person indicator or not."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Link image to media page"),
        14,
        "options.global.image-page-link",
        tooltip=_(
            "Indicates left click on an image should open the media page "
            "instead of the media viewer. Note this only applies to the "
            "images in object groups and not in the page header."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Link citation title to source page"),
        15,
        "options.global.link-citation-title-to-source",
        tooltip=_(
            "Indicates whether the source title link in a citation record "
            "links to the source page instead of the citation page."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Compact family mode"),
        16,
        "options.global.compact-family-mode",
        tooltip=_(
            "Indicates whether to use the compact family frame without the"
            "embedded person frames of the partners."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Create reciprocal associations"),
        17,
        "options.global.create-reciprocal-associations",
        tooltip=_(
            "When this option is enabled and a person reference, also known"
            "as an association, is being added then after the association is"
            "added in one direction the editor will reopen so you can add"
            "a reciprocal one from the associated person back to the current"
            "one."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include notes on child objects"),
        18,
        "options.global.include-child-notes",
        tooltip=_(
            "Enabling this option will include notes on children of the "
            "primary object in the Notes edit selection section of the "
            "action menu if any are present."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include urls from notes"),
        19,
        "options.global.include-note-urls",
        tooltip=_(
            "Enabling this option will parse the notes for the primary "
            "object and extract any identifiable urls for inclusion in "
            "the url group list."
        ),
    )
    configdialog.add_spinner(
        grid1,
        _("Maximum citations per group"),
        20,
        "options.global.max-citations-per-group",
        (1, 500),
    )
    configdialog.add_spinner(
        grid1,
        _("Maximum references per group"),
        21,
        "options.global.max-references-per-group",
        (1, 500),
    )
    configdialog.add_checkbox(
        grid1,
        _("Enable warnings"),
        22,
        "options.global.enable-warnings",
        tooltip=_(
            "Indicates to show a warning dialog asking for confirmation "
            "before performing an action that removes or deletes data as "
            "a safeguard."
        ),
    )

    grid2 = create_grid()
    configdialog.add_text(grid2, _("Media Bar Options"), 0, bold=True)
    configdialog.add_combo(
        grid2,
        _("Media bar position"),
        1,
        "options.global.media-bar-position-mode",
        MEDIA_POSITION_MODES,
    )
    configdialog.add_combo(
        grid2,
        _("Media bar display mode"),
        2,
        "options.global.media-bar-display-mode",
        MEDIA_DISPLAY_MODES,
    )
    configdialog.add_spinner(
        grid2,
        _("Minimum media items required to display"),
        3,
        "options.global.media-bar-minimum-required",
        (1, 12),
    )
    configdialog.add_checkbox(
        grid2,
        _("Sort media by date"),
        4,
        "options.global.media-bar-sort-by-date",
        tooltip=_("Indicates whether to sort media items by date."),
    )
    configdialog.add_checkbox(
        grid2,
        _("Group media by type"),
        5,
        "options.global.media-bar-group-by-type",
        tooltip=_(
            "Indicates whether to group like media, based on Media-Type."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Filter out non-photos"),
        6,
        "options.global.media-bar-filter-non-photos",
        tooltip=_(
            "Indicates only photos should be displayed, based on Media-Type."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Link image to media page"),
        7,
        "options.global.media-bar-page-link",
        tooltip=_(
            "Indicates left click should open the media page instead of the "
            "media viewer. Applies only to the media bar, see the global "
            "option with the same description for everything else."
        ),
    )

    grid3 = create_grid()
    configdialog.add_text(
        grid3, _("Group Window and Icon Options"), 0, bold=True
    )
    configdialog.add_spinner(
        grid3,
        _("Maximum number of object group windows"),
        1,
        "options.global.max-group-windows",
        (1, 12),
    )
    configdialog.add_spinner(
        grid3,
        _("Maximum icons per line in header frames."),
        2,
        "options.global.icons-active-width",
        (1, 40),
    )
    configdialog.add_spinner(
        grid3,
        _("Maximum icons per line in group frames."),
        3,
        "options.global.icons-group-width",
        (1, 40),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable tag icons"),
        4,
        "options.global.icons-enable-tags",
        tooltip=_(
            "Enables display of icons for each tag associated with an object."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Sort tags by name not priority"),
        5,
        "options.global.sort-tags-by-name",
        tooltip=_(
            "Indicates if tags should be sorted by name and not priority. "
            "By default they sort by the priority in which they are "
            "organized in the tag organization tool."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable associated object indicator icons"),
        6,
        "options.global.icons-enable-indicators",
        tooltip=_(
            "Enables display of icons to indicate presence of notes, "
            "citations, and so forth. Options to selectively control "
            "which are shown follow below."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable names icon"),
        7,
        "options.global.indicate-names",
        tooltip=_("Enables display of alternate names icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable parents icon"),
        8,
        "options.global.indicate-parents",
        tooltip=_("Enables display of parents icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable spouses icon"),
        9,
        "options.global.indicate-spouses",
        tooltip=_("Enables display of spouses icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable children icon"),
        10,
        "options.global.indicate-children",
        tooltip=_("Enables display of children icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable associations icon"),
        11,
        "options.global.indicate-associations",
        tooltip=_("Enables display of associations icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable events icon"),
        12,
        "options.global.indicate-events",
        tooltip=_("Enables display of events icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable ordinances icon"),
        13,
        "options.global.indicate-ordinances",
        tooltip=_("Enables display of ordinances icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable media icon"),
        14,
        "options.global.indicate-media",
        tooltip=_("Enables display of media icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable attributes icon"),
        15,
        "options.global.indicate-attributes",
        tooltip=_("Enables display of attributes icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable addresses icon"),
        16,
        "options.global.indicate-addresses",
        tooltip=_("Enables display of addresses icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable citations icon"),
        17,
        "options.global.indicate-citations",
        tooltip=_("Enables display of citations icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable notes icon"),
        18,
        "options.global.indicate-notes",
        tooltip=_("Enables display of notes icon."),
    )
    configdialog.add_checkbox(
        grid3,
        _("Enable urls icon"),
        19,
        "options.global.indicate-urls",
        tooltip=_("Enables display of urls icon."),
    )

    grid.attach(grid1, 0, 0, 1, 2)
    grid.attach(grid2, 1, 1, 1, 1)
    grid.attach(grid3, 1, 0, 1, 1)
    return add_config_reset(configdialog, grstate, "options.global", grid)
