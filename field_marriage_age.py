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
Marriage age field calculator.
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
from view.common.common_vitals import get_marriage_ages

_ = glocale.translation.sgettext

AGES = "Ages"
AGES_LANG = _("Ages")
BRIDE_AGE = "Bride Age"
BRIDE_AGE_LANG = _("Bride Age")
GROOM_AGE = "Groom Age"
GROOM_AGE_LANG = _("Groom Age")


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
            "get_config_grids": build_marriage_age_grid,
            "get_field": get_marriage_age_field,
        }
    ]


supported_types = {
    "Family": [
        (AGES, AGES_LANG),
        (BRIDE_AGE, BRIDE_AGE_LANG),
        (GROOM_AGE, GROOM_AGE_LANG),
    ]
}


def build_marriage_age_grid(_dummy_configdialog, _dummy_grstate):
    """
    Build the marriage age option grid. As we have none return None.
    """
    return None


def get_marriage_age_field(grstate, obj, field_value, args):
    """
    Calculate ages of couple.
    """
    if not isinstance(obj, Family):
        return []
    get_label = args.get("get_label")

    groom_age, bride_age = get_marriage_ages(grstate.dbstate.db, obj)
    if bride_age:
        bride_text = bride_age
    else:
        bride_text = _("Unknown")

    if field_value == BRIDE_AGE:
        return [(get_label(BRIDE_AGE_LANG), get_label(bride_text))]

    if groom_age:
        groom_text = groom_age
    else:
        groom_text = _("Unknown")

    if field_value == GROOM_AGE:
        return [(get_label(GROOM_AGE_LANG), get_label(groom_text))]

    bride_text = " ".join((_("Bride age"), bride_text.lower()))
    groom_text = " ".join((_("Groom age"), groom_text.lower()))
    text = "; ".join((bride_text, groom_text))
    return [(get_label(AGES_LANG), get_label(text))]
