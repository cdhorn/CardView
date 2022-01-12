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
Timeline configuration panels
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
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
from .config_const import (
    IMAGE_DISPLAY_MODES,
    REF_DISPLAY_MODES,
    TIMELINE_COLOR_MODES,
)
from .config_utils import add_config_reset, config_facts_fields, create_grid

_ = glocale.translation.sgettext


def build_timeline_grid(configdialog, grstate, space, *_dummy_args):
    """
    Builds person timeline options section for the configuration dialog.
    """
    grid1 = create_grid()
    configdialog.add_text(grid1, _("Display Options"), 0, bold=True)
    configdialog.add_combo(
        grid1,
        _("Timeline color scheme"),
        2,
        "{}.color-scheme".format(space),
        TIMELINE_COLOR_MODES,
    )
    configdialog.add_combo(
        grid1,
        _("Image display mode"),
        4,
        "{}.image-mode".format(space),
        IMAGE_DISPLAY_MODES,
    )
    configdialog.add_combo(
        grid1,
        _("Reference display mode"),
        5,
        "{}.reference-mode".format(space),
        REF_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid1,
        _("Show year and age"),
        6,
        "{}.show-age".format(space),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated media items"),
        7,
        "{}.include-media".format(space),
    )
    if "person" in space:
        configdialog.add_checkbox(
            grid1,
            _("Include dated names"),
            8,
            "{}.include-names".format(space),
        )
        configdialog.add_checkbox(
            grid1,
            _("Include dated addresses"),
            9,
            "{}.include-addresses".format(space),
        )
    if "person" in space or "family" in space:
        configdialog.add_checkbox(
            grid1,
            _("Include dated ordinances"),
            10,
            "{}.include-ldsords".format(space),
        )
    configdialog.add_checkbox(
        grid1,
        _("Include dated citations"),
        11,
        "{}.include-citations".format(space),
    )
    configdialog.add_text(grid1, _("Display Attributes"), 12, bold=True)
    configdialog.add_checkbox(
        grid1,
        _("Show role always not just secondary events"),
        13,
        "{}.show-role-always".format(space),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show description"),
        14,
        "{}.show-description".format(space),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show registered participants if more than one person"),
        15,
        "{}.show-participants".format(space),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show source count"),
        16,
        "{}.show-source-count".format(space),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show citation count"),
        17,
        "{}.show-citation-count".format(space),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show best confidence rating"),
        18,
        "{}.show-best-confidence".format(space),
    )
    configdialog.add_text(grid1, _("Attributes Group"), 19, start=1, bold=True)
    context = space.split(".")[1]
    config_facts_fields(
        configdialog,
        grstate,
        "timeline",
        context,
        grid1,
        20,
        start_col=1,
        number=5,
        mode="fact",
        key="rfield",
        obj_type="Event",
    )
    grid2 = create_grid()
    configdialog.add_text(grid2, _("Category Filters"), 0, bold=True)
    configdialog.add_checkbox(
        grid2,
        _("Show vital"),
        1,
        "{}.show-class-vital".format(space),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show family"),
        2,
        "{}.show-class-family".format(space),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show religious"),
        3,
        "{}.show-class-religious".format(space),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show vocational"),
        4,
        "{}.show-class-vocational".format(space),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show academic"),
        5,
        "{}.show-class-academic".format(space),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show travel"),
        6,
        "{}.show-class-travel".format(space),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show legal"),
        7,
        "{}.show-class-legal".format(space),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show residence"),
        8,
        "{}.show-class-residence".format(space),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show other"),
        9,
        "{}.show-class-other".format(space),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show custom"),
        10,
        "{}.show-class-custom".format(space),
    )

    if "person" in space:
        grid3 = create_grid()
        configdialog.add_text(grid3, _("Relationship Filters"), 0, bold=True)
        configdialog.add_spinner(
            grid3,
            _("Generations of ancestors to examine"),
            1,
            "{}.generations-ancestors".format(space),
            (1, 3),
        )
        configdialog.add_spinner(
            grid3,
            _("Generations of offspring to examine"),
            2,
            "{}.generations-offspring".format(space),
            (1, 3),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for father and grandfathers"),
            3,
            "{}.show-family-father".format(space),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for mother and grandmothers"),
            4,
            "{}.show-family-mother".format(space),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for brothers and stepbrothers"),
            5,
            "{}.show-family-brother".format(space),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for sisters and stepsisters"),
            6,
            "{}.show-family-sister".format(space),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for wives"),
            7,
            "{}.show-family-wife".format(space),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for husbands"),
            8,
            "{}.show-family-husband".format(space),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for sons and grandsons"),
            9,
            "{}.show-family-son".format(space),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for daughters and granddaughters"),
            10,
            "{}.show-family-daughter".format(space),
        )

        grid4 = create_grid()
        configdialog.add_text(
            grid4, _("Relationship Category Filters"), 0, bold=True
        )
        configdialog.add_checkbox(
            grid4,
            _("Show vital"),
            1,
            "{}.show-family-class-vital".format(space),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show family"),
            2,
            "{}.show-family-class-family".format(space),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show religious"),
            3,
            "{}.show-family-class-religious".format(space),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show vocational"),
            4,
            "{}.show-family-class-vocational".format(space),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show academic"),
            5,
            "{}.show-family-class-academic".format(space),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show travel"),
            6,
            "{}.show-family-class-travel".format(space),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show legal"),
            7,
            "{}.show-family-class-legal".format(space),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show residence"),
            8,
            "{}.show-family-class-residence".format(space),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show other"),
            9,
            "{}.show-family-class-other".format(space),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show custom"),
            10,
            "{}.show-family-class-custom".format(space),
        )
    grid = Gtk.Grid()
    grid.attach(grid1, 0, 0, 1, 2)
    grid.attach(grid2, 1, 0, 1, 1)
    if "person" in space:
        grid.attach(grid3, 1, 1, 1, 1)
        grid.attach(grid4, 1, 2, 1, 1)
    return add_config_reset(configdialog, grstate, space, grid)


def build_person_timeline_grid(configdialog, grstate, *_dummy_args):
    """
    Build person timeline configuration grid.
    """
    return build_timeline_grid(configdialog, grstate, "timeline.person")


def build_family_timeline_grid(configdialog, grstate, *_dummy_args):
    """
    Build family timeline configuration grid.
    """
    return build_timeline_grid(configdialog, grstate, "timeline.family")


def build_place_timeline_grid(configdialog, grstate, *_dummy_args):
    """
    Build place timeline configuration grid.
    """
    return build_timeline_grid(configdialog, grstate, "timeline.place")
