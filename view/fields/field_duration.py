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
from gramps.gen.lib import EventType, Family, Person
from gramps.gen.lib.date import Today
from gramps.gen.utils.alive import probably_alive, probably_alive_range


# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_vitals import get_marriage_duration, get_span

_ = glocale.translation.sgettext


def get_duration_field(grstate, obj, field_value, args):
    """
    Calculate a duration related value.
    """
    get_label = args.get("get_label")
    event_cache = args.get("event_cache") or {}

    if isinstance(obj, Family):
        if field_value == "Duration":
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

        if field_value in ["Lifespan", "Duration"]:
            if birth_date and death_date:
                span = get_span(birth_date, death_date)
                if span:
                    return [
                        (
                            get_label(_("Lifespan")),
                            get_label(
                                span, italic=not accurate_lifespan(event_cache)
                            ),
                        )
                    ]

        if field_value in ["Living", "Duration"]:
            if birth_date and not death_date:
                if field_value != "Living":
                    span = get_span(birth_date, Today())
                    if span:
                        return [(get_label(_("Living")), get_label(span))]
                return [(get_label(_("Living")), get_label(""))]
        return []


def accurate_lifespan(event_cache):
    """
    Return true if have actual birth and death record.
    """
    hits = []
    for event in event_cache:
        if event.get_type() in [EventType.BIRTH, EventType.DEATH]:
            if event.get_type() not in hits:
                hits.append(event.get_type())
    return len(hits) == 2
