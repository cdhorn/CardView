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
from ..common.common_vitals import get_marriage_ages

_ = glocale.translation.sgettext


def get_marriage_age_field(grstate, obj, _dummy_field_value, args):
    """
    Calculate ages of couple.
    """
    get_label = args.get("get_label")

    if isinstance(obj, Family):
        ages = ""
        husband_age, wife_age = get_marriage_ages(grstate.dbstate.db, obj)
        if husband_age:
            ages = " ".join((_("Husband"), _("age"), husband_age))
        else:
            ages = " ".join((_("Husband"), _("age"), _("unknown")))
        if wife_age:
            ages = " ".join((ages, ";", _("Wife"), _("age"), wife_age))
        else:
            ages = " ".join((ages, ";", _("Wife"), _("age"), _("unknown")))
        if ages:
            return [(get_label(_("Ages")), get_label(ages))]
        return []
