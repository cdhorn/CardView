#
# Gramps - a GTK+/GNOME based genealogy program
#
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
Child number and parent information calculator.
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import FamilyRelType, Person

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from view.common.common_vitals import (
    get_date_sortval,
    get_key_family_events,
    get_person_birth_or_death,
    get_span,
)
from view.config.config_utils import create_grid

_ = glocale.translation.sgettext

CHILD_NUMBER_LANG = _("Child Number")

OPTION_SHOW_MOTHER = "field.child.show-mother"
OPTION_SHOW_FATHER = "field.child.show-father"
OPTION_SHOW_DURATION = "field.child.show-marriage-duration"


# ------------------------------------------------------------------------
#
# Calculated field plugin API consists of a dictionary with the supported
# object types and keyword values, default options, callable to build
# configuration grids for the options, and callable to generate the field
# labels.
#
# ------------------------------------------------------------------------
def load_on_reg(_dummy_dbstate, _dummy_uistate, _dummy_plugin):
    """
    Return calculated field plugin attributes.
    """
    return [
        {
            "supported_types": supported_types,
            "default_options": default_options,
            "get_config_grids": build_child_grid,
            "get_field": get_child_field,
        }
    ]


supported_types = {"Person": [("Child Number", CHILD_NUMBER_LANG)]}


default_options = [
    (OPTION_SHOW_MOTHER, True),
    (OPTION_SHOW_FATHER, True),
    (OPTION_SHOW_DURATION, True),
]


def build_child_grid(configdialog, _dummy_grstate):
    """
    Build the child option grid.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Child Number Field"), 0, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Show age of mother at birth of child"),
        1,
        OPTION_SHOW_MOTHER,
    )
    configdialog.add_checkbox(
        grid,
        _("Show age of father at birth of child"),
        2,
        OPTION_SHOW_FATHER,
    )
    configdialog.add_checkbox(
        grid,
        _("Show duration of marriage at birth of child"),
        3,
        OPTION_SHOW_DURATION,
    )
    return grid


def get_child_field(grstate, obj, _dummy_field_value, args):
    """
    Calculate child and parent infomation.
    """
    if not isinstance(obj, Person):
        return []
    get_label = args.get("get_label")

    person_birth = None
    birth_ref = obj.get_birth_ref()
    if birth_ref:
        event = grstate.dbstate.db.get_event_from_handle(birth_ref.ref)
        if event:
            person_birth = event.get_date_object()

    parent_family_handle = obj.get_main_parents_family_handle()
    if not parent_family_handle:
        return [(get_label(_("Child")), get_label(_("Unknown Parents")))]

    parent_family = grstate.dbstate.db.get_family_from_handle(
        parent_family_handle
    )

    total = 0
    number = 0
    for child_ref in parent_family.child_ref_list:
        total = total + 1
        if child_ref.ref == obj.handle:
            number = total
    data = ["%s %s %s" % (str(number), _("of"), str(total))]

    if person_birth:
        data = data + get_optional_fields(grstate, parent_family, person_birth)
    return [(get_label(CHILD_NUMBER_LANG), get_label("; ".join(tuple(data))))]


def get_optional_fields(grstate, parent_family, person_birth):
    """
    Return additional options data field text.
    """
    data = []
    if grstate.config.get(OPTION_SHOW_MOTHER):
        mother_text, dummy_text = get_parent_text(
            grstate.dbstate.db, parent_family, person_birth, "Mother"
        )
        if mother_text:
            data.append(mother_text)
    if grstate.config.get(OPTION_SHOW_FATHER):
        father_text, death_text = get_parent_text(
            grstate.dbstate.db, parent_family, person_birth, "Father"
        )
        if father_text:
            data.append(father_text)
    else:
        death_text = ""
    if grstate.config.get(OPTION_SHOW_DURATION):
        family_text = get_family_text(
            grstate.dbstate.db, parent_family, person_birth, death_text
        )
        if family_text:
            data.append(family_text)
    return data


def get_parent_text(db, family, birth_date, parent_type):
    """
    Return parent age at time child born.
    """
    death_text = ""
    parent_text = ""
    if parent_type == "Mother":
        parent_handle = family.mother_handle
    else:
        parent_handle = family.father_handle
    if not parent_handle:
        return "", ""

    dummy_parent, birth = get_person_birth_or_death(db, parent_handle)
    if birth:
        parent_text = get_parent_age_text(
            birth.get_date_object(), birth_date, parent_type
        )

    if parent_type == "Father":
        dummy_parent, death = get_person_birth_or_death(
            db, parent_handle, birth=False
        )
        if death:
            death_sortval = get_date_sortval(death)
            if death_sortval < birth_date.sortval:
                death_text = _("Father deceased at birth")
    return parent_text, death_text


def get_parent_age_text(parent_birth_date, event_date, parent_type):
    """
    Return parent age text.
    """
    parent_text = ""
    span = get_span(parent_birth_date, event_date)
    if span:
        if parent_type == "Mother":
            parent_text = "%s %s" % (_("Mother age"), span)
        else:
            parent_text = "%s %s" % (_("Father age"), span)
    return parent_text


def get_family_text(db, family, birth_date, death_text):
    """
    Return marriage type and length at time child born.
    """
    family_text = ""
    family_type = family.get_relationship()
    marriage, divorce = get_key_family_events(db, family)

    status = ""
    base_date = None
    if family_type == FamilyRelType.MARRIED:
        base_date, status = check_unmarried_at_birth(birth_date, marriage)
    elif family_type == FamilyRelType.UNMARRIED:
        status = _("unmarried")

    if divorce and birth_date:
        divorce_date = divorce.get_date_object()
        if divorce_date.sortval < birth_date.sortval:
            base_date = divorce_date
            status = _("divorced")

    if status:
        family_text = "%s %s" % (_("Parents"), status)

    if death_text:
        family_text = "%s; %s" % (family_text, death_text)
    elif birth_date and base_date:
        span = get_span(base_date, birth_date)
        if span:
            family_text = "%s %s" % (family_text, span)
    return family_text


def check_unmarried_at_birth(birth_date, marriage):
    """
    Return status of marriage at time of a child's birth.
    """
    status = _("married")
    base_date = None
    if marriage and birth_date:
        marriage_sortval = get_date_sortval(marriage)
        if marriage_sortval and marriage_sortval > birth_date.sortval:
            status = _("umarried at time of birth")
        else:
            base_date = marriage.get_date_object()
    return base_date, status
