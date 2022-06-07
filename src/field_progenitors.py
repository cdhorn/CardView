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
Progenitors field calculator.
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Person
from gramps.gen.utils.db import family_name

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------

_ = glocale.translation.sgettext

MATERNAL_PROGENITORS = "Maternal Progenitors"
MATERNAL_PROGENITORS_LANG = _("Maternal Progenitors")
PATERNAL_PROGENITORS = "Paternal Progenitors"
PATERNAL_PROGENITORS_LANG = _("Paternal Progenitors")


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
            "default_options": [],
            "get_config_grids": build_progenitors_grid,
            "get_field": get_progenitors_field,
        }
    ]


supported_types = {
    "Person": [
        (MATERNAL_PROGENITORS, MATERNAL_PROGENITORS_LANG),
        (PATERNAL_PROGENITORS, PATERNAL_PROGENITORS_LANG),
    ]
}


def build_progenitors_grid(_dummy_configdialog, _dummy_grstate):
    """
    Build the progenitors option grid. As we have none return None.
    """
    return None


def get_progenitors_field(grstate, obj, field_value, args):
    """
    Calculate paternal or maternal progenitors.
    """
    get_label = args.get("get_label")
    get_link = args.get("get_link")
    if isinstance(obj, Person):
        parent_family_handle = obj.get_main_parents_family_handle()
        if not parent_family_handle:
            return []
        parent_family = grstate.dbstate.db.get_family_from_handle(
            parent_family_handle
        )
        if not parent_family:
            return []
        paternal = PATERNAL_PROGENITORS in field_value
        family, generations = extract_progenitor_family(
            grstate.dbstate.db, parent_family, paternal=paternal
        )
        name = family_name(family, grstate.dbstate.db)
        if not name:
            return []
        if generations > 1:
            name = "".join(
                (
                    name,
                    " (",
                    str(generations),
                    " ",
                    _("Generations"),
                    ")",
                )
            )
        elif generations == 1:
            name = "".join((name, " (1 ", _("Generation"), ")"))
        if paternal:
            label = get_label(PATERNAL_PROGENITORS_LANG)
        else:
            label = get_label(MATERNAL_PROGENITORS_LANG)
        return [
            (
                label,
                get_link(name, "Family", family.handle, title=False),
            )
        ]
    return []


def extract_progenitor_family(db, family, generation=1, paternal=True):
    """
    Recursively extract progenitors.
    """
    if paternal:
        parent_handle = family.father_handle
    else:
        parent_handle = family.mother_handle
    if parent_handle:
        parent = db.get_person_from_handle(parent_handle)
        if parent:
            parent_family_handle = parent.get_main_parents_family_handle()
            if parent_family_handle:
                parent_family = db.get_family_from_handle(parent_family_handle)
                if parent_family:
                    generation = generation + 1
                    return extract_progenitor_family(
                        db,
                        parent_family,
                        generation=generation,
                        paternal=paternal,
                    )
    return family, generation
