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
Duration field calculator.
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Family, Person
from gramps.gen.lib.date import Today
from gramps.gen.utils.alive import probably_alive_range

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from view.common.common_vitals import get_marriage_duration, get_span

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
            "get_config_grids": build_duration_grid,
            "get_field": get_duration_field,
        }
    ]


supported_types = {
    "Person": [
        ("Duration", _("Duration")),
        ("Lifespan", _("Lifespan")),
        ("Living", _("Living")),
    ],
    "Family": [("Duration", _("Duration"))],
}


def build_duration_grid(_dummy_configuration, _dummy_grstate):
    """
    Build the duration option grid. As we have none return None.
    """
    return None


def get_duration_field(grstate, obj, field_value, args):
    """
    Calculate a duration related value.
    """
    get_label = args.get("get_label")

    if isinstance(obj, Family) and field_value == "Duration":
        duration = get_marriage_duration(grstate.dbstate.db, obj)
        if duration:
            return [(get_label(_("Duration")), get_label(duration))]
        return []

    if isinstance(obj, Person):
        (
            birth_date,
            death_date,
            dummy_explain_text,
            dummy_related_person,
        ) = probably_alive_range(obj, grstate.dbstate.db)
        today = Today()
        if death_date and death_date > today:
            return currently_living(field_value, get_label, birth_date)
        if (
            field_value in ["Lifespan", "Duration"]
            and birth_date
            and death_date
        ):
            span = get_span(birth_date, death_date)
            if span:
                return [
                    (
                        get_label(_("Lifespan")),
                        get_label(span, italic=not accurate_lifespan(obj)),
                    )
                ]
    return []


def currently_living(key, get_label, birth_date):
    """
    Return living status and duration if requested.
    """
    if key in ["Living", "Duration"]:
        if key != "Living":
            span = get_span(birth_date, Today())
            if span:
                return [(get_label(_("Living")), get_label(span))]
        return [(get_label(_("Living")), get_label(""))]
    return []


def accurate_lifespan(obj):
    """
    Return true if have actual birth and death record.
    """
    if obj.get_birth_ref() and obj.get_death_ref():
        return True
    return False
