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
from .page_const import (
    IMAGE_DISPLAY_MODES,
    REF_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
    TIMELINE_COLOR_MODES,
)
from .page_utils import add_config_reset, config_facts_fields, create_grid

_ = glocale.translation.sgettext


def build_person_timeline_grid(configdialog, grstate):
    """
    Builds person timeline options section for the configuration dialog.
    """
    grid1 = create_grid()
    configdialog.add_text(grid1, _("Display Options"), 0, bold=True)
    configdialog.add_combo(
        grid1,
        _("Timeline color scheme"),
        1,
        "options.timeline.person.color-scheme",
        TIMELINE_COLOR_MODES,
    )
    configdialog.add_combo(
        grid1,
        _("Image display mode"),
        4,
        "options.timeline.person.image-mode",
        IMAGE_DISPLAY_MODES,
    )
    configdialog.add_combo(
        grid1,
        _("Reference display mode"),
        5,
        "options.timeline.person.reference-mode",
        REF_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid1,
        _("Show year and age"),
        6,
        "options.timeline.person.show-age",
        tooltip=_(
            "Enabling this option will show the year of the event and the age of the active person at that time if it can be calculated."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated media items"),
        7,
        "options.timeline.person.include-media",
        tooltip=_(
            "Enabling this option will include media items if they have a valid date set."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated names"),
        8,
        "options.timeline.person.include-names",
        tooltip=_(
            "Enabling this option will include names if they have a valid date set."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated addresses"),
        9,
        "options.timeline.person.include-addresses",
        tooltip=_(
            "Enabling this option will include addresses if they have a valid date."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated ordinances"),
        10,
        "options.timeline.person.include-ldsords",
        tooltip=_(
            "Enabling this option will include LDS ordinances if they have a valid date."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated citations"),
        11,
        "options.timeline.person.include-citations",
        tooltip=_(
            "Enabling this option will include citations if they have a valid date."
        ),
    )
    configdialog.add_text(grid1, _("Display Attributes"), 12, bold=True)
    configdialog.add_checkbox(
        grid1,
        _("Show role always not just secondary events"),
        13,
        "options.timeline.person.show-role-always",
        tooltip=_(
            "Enabling this option will always show the role of the active person in the event. This is normally implicit if they had none or they were the primary participant. Note their role is always displayed for secondary events."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show description"),
        14,
        "options.timeline.person.show-description",
        tooltip=_(
            "Enabling this option will show the event description if one is available."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show registered participants if more than one person"),
        15,
        "options.timeline.person.show-participants",
        tooltip=_(
            "Enabling this option will show the other participants in shared events."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show source count"),
        16,
        "options.timeline.person.show-source-count",
        tooltip=_(
            "Enabling this option will include a count of the number of unique sources cited from in support of the information about the event."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show citation count"),
        17,
        "options.timeline.person.show-citation-count",
        tooltip=_(
            "Enabling this option will include a count of the number of citations in support of the information about the event."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show best confidence rating"),
        18,
        "options.timeline.person.show-best-confidence",
        tooltip=_(
            "Enabling this option will show the highest user defined confidence rating found among all the citations in support of the information about the event."
        ),
    )
    configdialog.add_text(grid1, _("Attributes Group"), 19, start=1, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        "options.timeline",
        "person",
        grid1,
        20,
        start_col=1,
        number=4,
        mode="fact",
        key="attributes-field",
        obj_type="Event",
    )
    grid2 = create_grid()
    configdialog.add_text(grid2, _("Category Filters"), 0, bold=True)
    configdialog.add_checkbox(
        grid2,
        _("Show vital"),
        1,
        "options.timeline.person.show-class-vital",
        tooltip=_(
            "Enabling this option will show all vital events for the person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show family"),
        2,
        "options.timeline.person.show-class-family",
        tooltip=_(
            "Enabling this option will show all family related events for the active person on the timeline. The list of family events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show religious"),
        3,
        "options.timeline.person.show-class-religious",
        tooltip=_(
            "Enabling this option will show all religious events for the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show vocational"),
        4,
        "options.timeline.person.show-class-vocational",
        tooltip=_(
            "Enabling this option will show all vocational events for the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show academic"),
        5,
        "options.timeline.person.show-class-academic",
        tooltip=_(
            "Enabling this option will show all academic events for the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show travel"),
        6,
        "options.timeline.person.show-class-travel",
        tooltip=_(
            "Enabling this option will show all travel events for the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show legal"),
        7,
        "options.timeline.person.show-class-legal",
        tooltip=_(
            "Enabling this option will show all legal events for the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show residence"),
        8,
        "options.timeline.person.show-class-residence",
        tooltip=_(
            "Enabling this option will show all residence events for the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show other"),
        9,
        "options.timeline.person.show-class-other",
        tooltip=_(
            "Enabling this option will show all other events for the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show custom"),
        10,
        "options.timeline.person.show-class-custom",
        tooltip=_(
            "Enabling this option will show all user defined custom events for the active person on the timeline. The list of custom events is the same as in the event type selector in the event editor."
        ),
    )
    grid3 = create_grid()
    configdialog.add_text(grid3, _("Relationship Filters"), 0, bold=True)
    configdialog.add_spinner(
        grid3,
        _("Generations of ancestors to examine"),
        1,
        "options.timeline.person.generations-ancestors",
        (1, 3),
    )
    configdialog.add_spinner(
        grid3,
        _("Generations of offspring to examine"),
        2,
        "options.timeline.person.generations-offspring",
        (1, 3),
    )
    configdialog.add_checkbox(
        grid3,
        _("Include events for father and grandfathers"),
        3,
        "options.timeline.person.show-family-father",
        tooltip=_(
            "Enabling this option will include events for fathers, stepfathers, and grandfathers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Include events for mother and grandmothers"),
        4,
        "options.timeline.person.show-family-mother",
        tooltip=_(
            "Enabling this option will include events for mothers, stepmothers, and grandmothers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Include events for brothers and stepbrothers"),
        5,
        "options.timeline.person.show-family-brother",
        tooltip=_(
            "Enabling this option will include events for brothers and stepbrothers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Include events for sisters and stepsisters"),
        6,
        "options.timeline.person.show-family-sister",
        tooltip=_(
            "Enabling this option will include events for sisters and stepsisters of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Include events for wives"),
        7,
        "options.timeline.person.show-family-wife",
        tooltip=_(
            "Enabling this option will include events for the wives of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Include events for husbands"),
        8,
        "options.timeline.person.show-family-husband",
        tooltip=_(
            "Enabling this option will include events for the husbands of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Include events for sons and grandsons"),
        9,
        "options.timeline.person.show-family-son",
        tooltip=_(
            "Enabling this option will include events for the sons and grandsons of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion."
        ),
    )
    configdialog.add_checkbox(
        grid3,
        _("Include events for daughters and granddaughters"),
        10,
        "options.timeline.person.show-family-daughter",
        tooltip=_(
            "Enabling this option will include events for the daughters and granddaughters of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion."
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
        "options.timeline.person.show-family-class-vital",
        tooltip=_(
            "Enabling this option will show all vital events for the eligible relations of the active person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others."
        ),
    )
    configdialog.add_checkbox(
        grid4,
        _("Show family"),
        2,
        "options.timeline.person.show-family-class-family",
        tooltip=_(
            "Enabling this option will show all family related events for the eligible relations of the active person on the timeline. The list of family events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid4,
        _("Show religious"),
        3,
        "options.timeline.person.show-family-class-religious",
        tooltip=_(
            "Enabling this option will show all religious related events for the eligible relations of the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid4,
        _("Show vocational"),
        4,
        "options.timeline.person.show-family-class-vocational",
        tooltip=_(
            "Enabling this option will show all vocational related events for the eligible relations of the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid4,
        _("Show academic"),
        5,
        "options.timeline.person.show-family-class-academic",
        tooltip=_(
            "Enabling this option will show all academic related events for the eligible relations of the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid4,
        _("Show travel"),
        6,
        "options.timeline.person.show-family-class-travel",
        tooltip=_(
            "Enabling this option will show all travel related events for the eligible relations of the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid4,
        _("Show legal"),
        7,
        "options.timeline.person.show-family-class-legal",
        tooltip=_(
            "Enabling this option will show all legal related events for the eligible relations of the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid4,
        _("Show residence"),
        8,
        "options.timeline.person.show-family-class-residence",
        tooltip=_(
            "Enabling this option will show all residence related events for the eligible relations of the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid4,
        _("Show other"),
        9,
        "options.timeline.person.show-family-class-other",
        tooltip=_(
            "Enabling this option will show all other events for the eligible relations of the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid4,
        _("Show custom"),
        10,
        "options.timeline.person.show-family-class-custom",
        tooltip=_(
            "Enabling this option will show all user defined custom events for the eligible relations of the active person on the timeline. The list of custom events is the same as in the event type selector in the event editor."
        ),
    )
    grid = Gtk.Grid()
    grid.attach(grid1, 0, 0, 1, 2)
    grid.attach(grid2, 1, 0, 1, 1)
    grid.attach(grid3, 1, 1, 1, 1)
    grid.attach(grid4, 1, 2, 1, 1)
    return add_config_reset(
        configdialog, grstate, "options.timeline.person", grid
    )


def build_family_timeline_grid(configdialog, grstate):
    """
    Builds active family timeline options section for the configuration dialog
    """
    grid1 = create_grid()
    configdialog.add_text(grid1, _("Display Options"), 0, bold=True)
    configdialog.add_combo(
        grid1,
        _("Timeline color scheme"),
        1,
        "options.timeline.family.color-scheme",
        TIMELINE_COLOR_MODES,
    )
    configdialog.add_combo(
        grid1,
        _("Image display mode"),
        4,
        "options.timeline.family.image-mode",
        IMAGE_DISPLAY_MODES,
    )
    configdialog.add_combo(
        grid1,
        _("Reference display mode"),
        5,
        "options.timeline.family.reference-mode",
        REF_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid1,
        _("Show year and age"),
        6,
        "options.timeline.family.show-age",
        tooltip=_(
            "Enabling this option will show the year of the event and the age of the active person at that time if it can be calculated."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated media items"),
        7,
        "options.timeline.family.include-media",
        tooltip=_(
            "Enabling this option will include media items if they have a valid date set."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated names"),
        8,
        "options.timeline.family.include-names",
        tooltip=_(
            "Enabling this option will include names if they have a valid date set."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated addresses"),
        9,
        "options.timeline.family.include-addresses",
        tooltip=_(
            "Enabling this option will include addresses if they have a valid date."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated ordinances"),
        10,
        "options.timeline.family.include-ldsords",
        tooltip=_(
            "Enabling this option will include LDS ordinances if they have a valid date."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Include dated citations"),
        11,
        "options.timeline.family.include-citations",
        tooltip=_(
            "Enabling this option will include citations if they have a valid date."
        ),
    )
    configdialog.add_text(grid1, _("Display Attributes"), 12, bold=True)
    configdialog.add_checkbox(
        grid1,
        _("Show role always not just secondary events"),
        13,
        "options.timeline.family.show-role-always",
        tooltip=_(
            "Enabling this option will always show the role of the active person in the event. This is normally implicit if they had none or they were the primary participant. Note their role is always displayed for secondary events."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show description"),
        14,
        "options.timeline.family.show-description",
        tooltip=_(
            "Enabling this option will show the event description if one is available."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show registered participants if more than one person"),
        15,
        "options.timeline.family.show-participants",
        tooltip=_(
            "Enabling this option will show the other participants in shared events."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show source count"),
        16,
        "options.timeline.family.show-source-count",
        tooltip=_(
            "Enabling this option will include a count of the number of unique sources cited from in support of the information about the event."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show citation count"),
        17,
        "options.timeline.family.show-citation-count",
        tooltip=_(
            "Enabling this option will include a count of the number of citations in support of the information about the event."
        ),
    )
    configdialog.add_checkbox(
        grid1,
        _("Show best confidence rating"),
        18,
        "options.timeline.family.show-best-confidence",
        tooltip=_(
            "Enabling this option will show the highest user defined confidence rating found among all the citations in support of the information about the event."
        ),
    )
    configdialog.add_text(grid1, _("Attributes Group"), 19, start=1, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        "options.timeline",
        "family",
        grid1,
        20,
        start_col=1,
        number=4,
        mode="fact",
        key="attributes-field",
        obj_type="Event",
    )
    grid2 = create_grid()
    configdialog.add_text(grid2, _("Category Filters"), 0, bold=True)
    configdialog.add_checkbox(
        grid2,
        _("Show vital"),
        1,
        "options.timeline.family.show-class-vital",
        tooltip=_(
            "Enabling this option will show all vital events for the person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show family"),
        2,
        "options.timeline.family.show-class-family",
        tooltip=_(
            "Enabling this option will show all family related events for the active person on the timeline. The list of family events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show religious"),
        3,
        "options.timeline.family.show-class-religious",
        tooltip=_(
            "Enabling this option will show all religious events for the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show vocational"),
        4,
        "options.timeline.family.show-class-vocational",
        tooltip=_(
            "Enabling this option will show all vocational events for the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show academic"),
        5,
        "options.timeline.family.show-class-academic",
        tooltip=_(
            "Enabling this option will show all academic events for the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show travel"),
        6,
        "options.timeline.family.show-class-travel",
        tooltip=_(
            "Enabling this option will show all travel events for the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show legal"),
        7,
        "options.timeline.family.show-class-legal",
        tooltip=_(
            "Enabling this option will show all legal events for the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show residence"),
        8,
        "options.timeline.family.show-class-residence",
        tooltip=_(
            "Enabling this option will show all residence events for the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show other"),
        9,
        "options.timeline.family.show-class-other",
        tooltip=_(
            "Enabling this option will show all other events for the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor."
        ),
    )
    configdialog.add_checkbox(
        grid2,
        _("Show custom"),
        10,
        "options.timeline.family.show-class-custom",
        tooltip=_(
            "Enabling this option will show all user defined custom events for the active person on the timeline. The list of custom events is the same as in the event type selector in the event editor."
        ),
    )
    grid = Gtk.Grid()
    grid.attach(grid1, 0, 0, 1, 1)
    grid.attach(grid2, 1, 0, 1, 1)
    return add_config_reset(
        configdialog, grstate, "options.timeline.family", grid
    )
