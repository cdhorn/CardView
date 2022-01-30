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
Occupations field calculator.
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------

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
            "get_config_grids": build_occupations_grid,
            "get_field": get_occupations_field,
        }
    ]


supported_types = {"Person": [("Occupations", _("Occupations"))]}


def build_occupations_grid(_dummy_configdialog, _dummy_grstate):
    """
    Build the occupations option grid. As we have none return None.
    """
    return None


def get_occupations_field(_dummy_grstate, obj, _dummy_event_type, args):
    """
    Calculate a list of occupations.
    """
    args = args or {}
    get_label = args.get("get_label")

    occupations = []
    event_cache = args.get("event_cache") or {}
    for event in event_cache:
        if (
            event.get_type().xml_str() == "Occupation"
            and event.get_description() not in occupations
        ):
            occupations.append(event.get_description())

    for attribute in obj.get_attribute_list():
        if (
            attribute.get_type().xml_str() == "Occupation"
            and attribute.get_value() not in occupations
        ):
            occupations.append(attribute.get_value())

    if occupations:
        return [
            (
                get_label(_("Occupations")),
                get_label(", ".join(tuple(occupations))),
            )
        ]
    return []
