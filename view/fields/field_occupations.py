#
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
Occupations field calculator.
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------

_ = glocale.translation.sgettext


def get_occupations_field(grstate, obj, event_type, args):
    """
    Calculate a list of occupations.
    """
    args = args or {}
    get_label = args.get("get_label")

    occupations = []
    event_cache = args.get("event_cache") or {}
    for event in event_cache:
        if event.get_type().xml_str() == "Occupation":
            if event.get_description() not in occupations:
                occupations.append(event.get_description())

    for attribute in obj.get_attribute_list():
        if attribute.get_type().xml_str() == "Occupation":
            if attribute.get_value() not in occupations:
                occupations.append(attribute.get_value())

    if occupations:
        return [
            (
                get_label(_("Occupations")),
                get_label(", ".join(tuple(occupations))),
            )
        ]
    return []
