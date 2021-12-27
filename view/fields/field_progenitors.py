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
        paternal = "Paternal" in field_value
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
            label = get_label(_("Paternal Progenitors"))
        else:
            label = get_label(_("Maternal Progenitors"))
        return [
            (
                label,
                get_link(name, "Family", family.get_handle(), title=False),
            )
        ]
    return []


def extract_progenitor_family(db, family, generation=1, paternal=True):
    """
    Recursively extract progenitors.
    """
    if paternal:
        parent_handle = family.get_father_handle()
    else:
        parent_handle = family.get_mother_handle()
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
