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
        tooltip=_(
            "Enabling this option will show the year of the event and the "
            "age of the active person at that time if it can be calculated."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated media items"),
        7,
        "{}.include-media".format(space),
        tooltip=_(
            "Enabling this option will include media items if they have a "
            "valid date set."
        ),
    )
    if "person" in space:
        configdialog.add_checkbox(
            grid1,
            _("Include dated names"),
            8,
            "{}.include-names".format(space),
            tooltip=_(
                "Enabling this option will include names if they have a "
                "valid date set."
            ),
        )
        configdialog.add_checkbox(
            grid1,
            _("Include dated addresses"),
            9,
            "{}.include-addresses".format(space),
            tooltip=_(
                "Enabling this option will include addresses if they have a "
                "valid date set."
            ),
        )
    if "person" in space or "family" in space:
        configdialog.add_checkbox(
            grid1,
            _("Include dated ordinances"),
            10,
            "{}.include-ldsords".format(space),
            tooltip=_(
                "Enabling this option will include LDS ordinances if they have "
                "a valid date."
            ),
        )
    configdialog.add_checkbox(
        grid1,
        _("Include dated citations"),
        11,
        "{}.include-citations".format(space),
        tooltip=_(
            "Enabling this option will include citations if they have a "
            "valid date."
        ),
    )
    configdialog.add_text(grid1, _("Display Attributes"), 12, bold=True)
    configdialog.add_checkbox(
        grid1,
        _("Show role always not just secondary events"),
        13,
        "{}.show-role-always".format(space),
        tooltip=_(
            "Enabling this option will always show the role of the active "
            "person in the event. This is normally implicit if they had none "
            "or they were the primary participant. Note their role is always "
            "displayed for secondary events."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show description"),
        14,
        "{}.show-description".format(space),
        tooltip=_(
            "Enabling this option will show the event description if one is "
            "available."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show registered participants if more than one person"),
        15,
        "{}.show-participants".format(space),
        tooltip=_(
            "Enabling this option will show the other participants in shared "
            "events."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show source count"),
        16,
        "{}.show-source-count".format(space),
        tooltip=_(
            "Enabling this option will include a count of the number of unique "
            "sources cited from in support of the information about the event."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show citation count"),
        17,
        "{}.show-citation-count".format(space),
        tooltip=_(
            "Enabling this option will include a count of the number of "
            "citations in support of the information about the event."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show best confidence rating"),
        18,
        "{}.show-best-confidence".format(space),
        tooltip=_(
            "Enabling this option will show the highest user defined "
            "confidence rating found among all the citations in support "
            "of the information about the event."
        ),
    )
    configdialog.add_text(grid1, _("Attributes Group"), 19, start=1, bold=True)
    context = space.split(".")[2]
    config_facts_fields(
        configdialog,
        grstate,
        "options.timeline",
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
        tooltip=_(
            "Enabling this option will show all vital events for the person "
            "on the timeline. In the event editor these are identfied as "
            "birth, baptism, death, burial, cremation and adopted. Note if "
            "this is disabled that birth and death events or their "
            "equivalents will always included regardless, so disabling it "
            "only filters out the others."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show family"),
        2,
        "{}.show-class-family".format(space),
        tooltip=_(
            "Enabling this option will show all family related events for "
            "the active person on the timeline. The list of family events "
            "is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show religious"),
        3,
        "{}.show-class-religious".format(space),
        tooltip=_(
            "Enabling this option will show all religious events for the "
            "active person on the timeline. The list of religious events "
            "is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show vocational"),
        4,
        "{}.show-class-vocational".format(space),
        tooltip=_(
            "Enabling this option will show all vocational events for the "
            "active person on the timeline. The list of vocational events is "
            "the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show academic"),
        5,
        "{}.show-class-academic".format(space),
        tooltip=_(
            "Enabling this option will show all academic events for the "
            "active person on the timeline. The list of academic events is "
            "the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show travel"),
        6,
        "{}.show-class-travel".format(space),
        tooltip=_(
            "Enabling this option will show all travel events for the active "
            "person on the timeline. The list of travel events is the same as "
            "in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show legal"),
        7,
        "{}.show-class-legal".format(space),
        tooltip=_(
            "Enabling this option will show all legal events for the active "
            "person on the timeline. The list of legal events is the same as "
            "in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show residence"),
        8,
        "{}.show-class-residence".format(space),
        tooltip=_(
            "Enabling this option will show all residence events for the "
            "active person on the timeline. The list of residence events is "
            "the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show other"),
        9,
        "{}.show-class-other".format(space),
        tooltip=_(
            "Enabling this option will show all other events for the active "
            "person on the timeline except custom user defined ones. The list "
            "of other events is the same as in the event type selector in the "
            "event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show custom"),
        10,
        "{}.show-class-custom".format(space),
        tooltip=_(
            "Enabling this option will show all user defined custom events "
            "for the active person on the timeline. The list of custom events "
            "is the same as in the event type selector in the event editor."
        ),
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
            tooltip=_(
                "Enabling this option will include events for fathers, "
                "stepfathers, and grandfathers of the active person in the "
                "timeline if they occurred during the life of the active person. "
                "Note if no relationship category filters are enabled that the "
                "birth and death events of these relations are always evaluated "
                "for inclusion."
            ),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for mother and grandmothers"),
            4,
            "{}.show-family-mother".format(space),
            tooltip=_(
                "Enabling this option will include events for mothers, "
                "stepmothers, and grandmothers of the active person in the "
                "timeline if they occurred during the life of the active person. "
                "Note if no relationship category filters are enabled that the "
                "birth and death events of these relations are always evaluated "
                "for inclusion."
            ),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for brothers and stepbrothers"),
            5,
            "{}.show-family-brother".format(space),
            tooltip=_(
                "Enabling this option will include events for brothers and "
                "stepbrothers of the active person in the timeline if they "
                "occurred during the life of the active person. Note if no "
                "relationship category filters are enabled that the birth and "
                "death events of these relations are always evaluated for "
                "inclusion."
            ),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for sisters and stepsisters"),
            6,
            "{}.show-family-sister".format(space),
            tooltip=_(
                "Enabling this option will include events for sisters and "
                "stepsisters of the active person in the timeline if they "
                "occurred during the life of the active person. Note if no "
                "relationship category filters are enabled that the birth "
                "and death events of these relations are always evaluated "
                "for inclusion."
            ),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for wives"),
            7,
            "{}.show-family-wife".format(space),
            tooltip=_(
                "Enabling this option will include events for the wives of "
                "the active person in the timeline if they occurred during "
                "the life of the active person. Note if no relationship category "
                "filters are enabled that the birth and death events of these "
                "relations are always evaluated for inclusion."
            ),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for husbands"),
            8,
            "{}.show-family-husband".format(space),
            tooltip=_(
                "Enabling this option will include events for the husbands of "
                "the active person in the timeline if they occurred during the "
                "life of the active person. Note if no relationship category "
                "filters are enabled that the birth and death events of these "
                "relations are always evaluated for inclusion."
            ),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for sons and grandsons"),
            9,
            "{}.show-family-son".format(space),
            tooltip=_(
                "Enabling this option will include events for the sons and "
                "grandsons of the active person in the timeline if they occurred "
                "during the life of the active person. Note if no relationship "
                "category filters are enabled that the birth and death events of "
                "these relations are always evaluated for inclusion."
            ),
        )
        configdialog.add_checkbox(
            grid3,
            _("Include events for daughters and granddaughters"),
            10,
            "{}.show-family-daughter".format(space),
            tooltip=_(
                "Enabling this option will include events for the daughters and "
                "granddaughters of the active person in the timeline if they "
                "occurred during the life of the active person. Note if no "
                "relationship category filters are enabled that the birth and "
                "death events of these relations are always evaluated for "
                "inclusion."
            ),
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
            tooltip=_(
                "Enabling this option will show all vital events for the eligible "
                "relations of the active person on the timeline. In the event "
                "editor these are identfied as birth, baptism, death, burial, "
                "cremation and adopted. Note if this is disabled that birth and "
                "death events or their equivalents will always be included "
                "regardless, so disabling it only filters out the others."
            ),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show family"),
            2,
            "{}.show-family-class-family".format(space),
            tooltip=_(
                "Enabling this option will show all family related events for "
                "the eligible relations of the active person on the timeline. "
                "The list of family events is the same as in the event type "
                "selector in the event editor."
            ),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show religious"),
            3,
            "{}.show-family-class-religious".format(space),
            tooltip=_(
                "Enabling this option will show all religious related events "
                "for the eligible relations of the active person on the timeline. "
                "The list of religious events is the same as in the event type "
                "selector in the event editor."
            ),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show vocational"),
            4,
            "{}.show-family-class-vocational".format(space),
            tooltip=_(
                "Enabling this option will show all vocational related events "
                "for the eligible relations of the active person on the timeline. "
                "The list of vocational events is the same as in the event type "
                "selector in the event editor."
            ),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show academic"),
            5,
            "{}.show-family-class-academic".format(space),
            tooltip=_(
                "Enabling this option will show all academic related events for "
                "the eligible relations of the active person on the timeline. "
                "The list of academic events is the same as in the event type "
                "selector in the event editor."
            ),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show travel"),
            6,
            "{}.show-family-class-travel".format(space),
            tooltip=_(
                "Enabling this option will show all travel related events for "
                "the eligible relations of the active person on the timeline. "
                "The list of travel events is the same as in the event type "
                "selector in the event editor."
            ),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show legal"),
            7,
            "{}.show-family-class-legal".format(space),
            tooltip=_(
                "Enabling this option will show all legal related events for "
                "the eligible relations of the active person on the timeline. "
                "The list of legal events is the same as in the event type "
                "selector in the event editor."
            ),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show residence"),
            8,
            "{}.show-family-class-residence".format(space),
            tooltip=_(
                "Enabling this option will show all residence related events for "
                "the eligible relations of the active person on the timeline. "
                "The list of residence events is the same as in the event type "
                "selector in the event editor."
            ),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show other"),
            9,
            "{}.show-family-class-other".format(space),
            tooltip=_(
                "Enabling this option will show all other events for the eligible "
                "relations of the active person on the timeline except custom "
                "user defined ones. The list of other events is the same as in "
                "the event type selector in the event editor."
            ),
        )
        configdialog.add_checkbox(
            grid4,
            _("Show custom"),
            10,
            "{}.show-family-class-custom".format(space),
            tooltip=_(
                "Enabling this option will show all user defined custom events "
                "for the eligible relations of the active person on the timeline. "
                "The list of custom events is the same as in the event type "
                "selector in the event editor."
            ),
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
    return build_timeline_grid(
        configdialog, grstate, "options.timeline.person"
    )


def build_family_timeline_grid(configdialog, grstate, *_dummy_args):
    """
    Build family timeline configuration grid.
    """
    return build_timeline_grid(
        configdialog, grstate, "options.timeline.family"
    )


def build_place_timeline_grid(configdialog, grstate, *_dummy_args):
    """
    Build place timeline configuration grid.
    """
    return build_timeline_grid(configdialog, grstate, "options.timeline.place")
