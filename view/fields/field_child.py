# Gramps - a GTK+/GNOME based genealogy program
#
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
Child number and parent information calculator.
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Family, FamilyRelType, Person

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_vitals import (
    get_key_family_events,
    get_key_person_events,
    get_span,
)

_ = glocale.translation.sgettext


def get_child_field(grstate, obj, field_value, args):
    """
    Calculate child and parent infomation.
    """
    get_label = args.get("get_label")

    if isinstance(obj, Person):
        person_events = get_key_person_events(grstate.dbstate.db, obj)
        if person_events["birth"]:
            person_birth = person_events["birth"].get_date_object()
        else:
            person_birth = None

        parent_family_handle = obj.get_main_parents_family_handle()
        if not parent_family_handle:
            return [(get_label(_("Child")), get_label(_("Unknown Parents")))]

        parent_family = grstate.dbstate.db.get_family_from_handle(
            parent_family_handle
        )

        total = 0
        number = 0
        for child_ref in parent_family.get_child_ref_list():
            total = total + 1
            if child_ref.ref == obj.get_handle():
                number = total
        data = [" ".join((str(number), _("of"), str(total)))]

        if person_birth:
            mother_text, dummy_text = get_parent_text(
                grstate.dbstate.db, parent_family, person_birth, "Mother"
            )
            if mother_text:
                data.append(mother_text)
            father_text, death_text = get_parent_text(
                grstate.dbstate.db, parent_family, person_birth, "Father"
            )
            if father_text:
                data.append(father_text)
            family_text = get_family_text(
                grstate.dbstate.db, parent_family, person_birth, death_text
            )
            if family_text:
                data.append(family_text)

        label = " ".join((_("Child"), _("Number")))
        return [(get_label(label), get_label("; ".join(tuple(data))))]


def get_parent_text(db, family, birth_date, parent_type):
    """
    Return parent age at time child born.
    """
    death_text = ""
    parent_text = ""
    if parent_type == "Mother":
        parent_handle = family.get_mother_handle()
    else:
        parent_handle = family.get_father_handle()
    if not parent_handle:
        return "", ""

    parent = db.get_person_from_handle(parent_handle)
    parent_events = get_key_person_events(db, parent)
    if birth_date and parent_events["birth"]:
        span = get_span(parent_events["birth"].get_date_object(), birth_date)
        if span:
            if parent_type == "Mother":
                parent_text = " ".join((_("Mother"), _("age"), span))
            else:
                parent_text = " ".join((_("Father"), _("age"), span))

    if parent_type == "Father":
        if parent_events["death"]:
            death_date = parent_events["death"].get_date_object()
            if death_date.sortval < birth_date.sortval:
                death_text = " ".join(
                    (_("Father"), _("deceased"), _("at"), _("birth"))
                )
    return parent_text, death_text


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
        status = _("married")
        if marriage and birth_date:
            if marriage.get_date_object().sortval > birth_date.sortval:
                status = " ".join((_("umarried"), _("at time of"), _("birth")))
            else:
                base_date = marriage.get_date_object()
    elif family_type == FamilyRelType.UNMARRIED:
        status = _("unmarried")

    if divorce and birth_date:
        divorce_date = divorce.get_date_object()
        if divorce_date.sortval < birth_date.sortval:
            base_date = divorce_date
            status = _("divorced")

    if status:
        family_text = " ".join((_("Parents"), status))

    if death_text:
        family_text = "; ".join((family_text, death_text))
    elif birth_date and base_date:
        span = get_span(base_date, birth_date)
        if span:
            family_text = " ".join((family_text, span))
    return family_text
