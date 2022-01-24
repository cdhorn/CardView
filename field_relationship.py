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
Couple relationship field calculator.
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Family

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------

_ = glocale.translation.sgettext


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
            "get_config_grids": build_relationship_grid,
            "get_field": get_relationship_field,
        }
    ]


supported_types = {"Family": [("Relationship", _("Relationship"))]}


def build_relationship_grid(_dummy_configdialog, _dummy_grstate):
    """
    Build the couple relationship option grid. As we have none return None.
    """
    return None


def get_relationship_field(grstate, obj, field_value, args):
    """
    Calculate potential ancestral relationship between a couple.
    """
    if not isinstance(obj, Family) or not field_value == "Relationship":
        return []

    get_label = args.get("get_label")

    father_handle = obj.get_father_handle()
    if not father_handle:
        return []
    mother_handle = obj.get_mother_handle()
    if not mother_handle:
        return []

    father = grstate.fetch("Person", father_handle)
    mother = grstate.fetch("Person", mother_handle)

    relations = grstate.uistate.relationship.get_all_relationships(
        grstate.dbstate.db, father, mother
    )
    for relation in relations[0]:
        if _("husband") not in relation and _("wife") not in relation:
            text = relation
            if "(" in text:
                text = text.split("(")[0].strip()
            return [
                (
                    get_label(_("Relationship")),
                    get_label(text.capitalize()),
                )
            ]
    return []
