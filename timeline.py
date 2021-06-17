#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
Timeline
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from typing import Dict, List, Tuple, Union


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db.base import DbReadBase
from gramps.gen.display.place import PlaceDisplay
from gramps.gen.errors import HandleError
from gramps.gen.lib import Date, Event, EventType, Person, Span
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.alive import probably_alive_range
from gramps.gen.utils.db import (
    get_birth_or_fallback,
    get_death_or_fallback,
    get_divorce_or_fallback,
    get_marriage_or_fallback,
)
from gramps.gen.utils.grampslocale import GrampsLocale

pd = PlaceDisplay()
default_locale = GrampsLocale(lang="en")
event_type = EventType()

DEATH_INDICATORS = [
    event_type.DEATH,
    event_type.BURIAL,
    event_type.CREMATION,
    event_type.CAUSE_DEATH,
    event_type.PROBATE,
]

RELATIVES = [
    "father",
    "mother",
    "brother",
    "sister",
    "wife",
    "husband",
    "son",
    "daughter",
]

EVENT_CATEGORIES = [
    "vital",
    "family",
    "religious",
    "vocational",
    "academic",
    "travel",
    "legal",
    "residence",
    "other",
    "custom",
]


# A timeline item is a tuple of following format:
#
# (Event, Person, relationship)
#
# A timeline may or may not have a anchor person. If it does relationships
# are calculated with respect to them.


class Timeline:
    """Timeline class."""

    def __init__(
        self,
        db_handle: DbReadBase,
        dates: Union[str, None] = None,
        events: Union[List, None] = None,
        ratings: bool = False,
        relatives: Union[List, None] = None,
        relative_events: Union[List, None] = None,
        discard_empty: bool = True,
        omit_anchor: bool = True,
        precision: int = 1,
        locale: GrampsLocale = glocale,
    ):
        """Initialize timeline."""
        self.db_handle = db_handle
        self.timeline = []
        self.dates = dates
        self.start_date = None
        self.end_date = None
        self.ratings = ratings
        self.discard_empty = discard_empty
        self.precision = precision
        self.locale = locale
        self.anchor_person = None
        self.omit_anchor = omit_anchor
        self.depth = 1
        self.eligible_events = set([])
        self.event_filters = events or []
        self.eligible_relative_events = set([])
        self.relative_event_filters = relative_events or []
        self.relative_filters = relatives or []
        self.set_event_filters(self.event_filters)
        self.set_relative_event_filters(self.relative_event_filters)
        self.birth_dates = {}

        if dates and "-" in dates:
            start, end = dates.split("-")
            if "/" in start:
                year, month, day = start.split("/")
                self.start_date = Date((int(year), int(month), int(day)))
            else:
                self.start_date = None
            if "/" in end:
                year, month, day = end.split("/")
                self.end_date = Date((int(year), int(month), int(day)))
            else:
                self.end_date = None

    def set_start_date(self, date: Union[Date, str]):
        """Set optional timeline start date."""
        if isinstance(date, str):
            year, month, day = date.split("/")
            self.start_date = Date((int(year), int(month), int(day)))
        else:
            self.start_date = date

    def set_end_date(self, date: Union[Date, str]):
        """Set optional timeline end date."""
        if isinstance(date, str):
            year, month, day = date.split("/")
            self.end_date = Date((int(year), int(month), int(day)))
        else:
            self.end_date = date

    def set_discard_empty(self, discard_empty: bool):
        """Set discard empty identifier."""
        self.discard_empty = discard_empty

    def set_precision(self, precision: int):
        """Set optional precision for span."""
        self.precision = precision

    def set_locale(self, locale: str):
        """Set optional locale for span."""
        self.locale = get_locale_for_language(locale, default=True)

    def set_event_filters(self, filters: Union[List, None] = None):
        """Prepare the event filter table."""
        self.event_filters = filters or []
        self.eligible_events = self._prepare_eligible_events(self.event_filters)

    def set_relative_event_filters(self, filters: Union[List, None] = None):
        """Prepare the relative event filter table."""
        self.relative_event_filters = filters or []
        self.eligible_relative_events = self._prepare_eligible_events(
            self.relative_event_filters
        )

    def _prepare_eligible_events(self, event_filters: List):
        """Prepare an event filter list."""
        eligible_events = {"Birth", "Death"}
        event_type = EventType()
        default_event_types = event_type.get_standard_xml()
        default_event_map = event_type.get_map()
        custom_event_types = self.db_handle.get_event_types()
        for key in event_filters:
            if key in default_event_types:
                eligible_events.add(key)
                continue
            if key in custom_event_types:
                eligible_events.add(key)
                continue
            if key not in EVENT_CATEGORIES:
                raise ValueError(
                    "{} is not a valid event or event category".format(key)
                )
        for entry in event_type.get_menu_standard_xml():
            event_key = entry[0].lower().replace("life events", "vital")
            if event_key in event_filters:
                for event_id in entry[1]:
                    if event_id in default_event_map:
                        eligible_events.add(default_event_map[event_id])
                break
        if "custom" in event_filters:
            for event_name in custom_event_types:
                eligible_events.add(event_name)
        return eligible_events

    def get_age(self, start_date, date):
        """Return calculated age or empty string otherwise."""
        age = ""
        if start_date:
            span = Span(start_date, date)
            if span.is_valid():
                age = str(
                    span.format(precision=self.precision, dlocale=self.locale).strip(
                        "()"
                    )
                )
        return age

    def is_death_indicator(self, event: Event) -> bool:
        """Check if an event indicates death timeframe."""
        if event.type in DEATH_INDICATORS:
            return True
        for event_name in [
            "Funeral",
            "Interment",
            "Reinterment",
            "Inurnment",
            "Memorial",
            "Visitation",
            "Wake",
            "Shiva",
        ]:
            if self.locale.translation.sgettext(event_name) == str(event.type):
                return True
        return False

    def is_eligible(self, event: Event, relative: bool):
        """Check if an event is eligible for the timeline."""
        if relative:
            if self.relative_event_filters == []:
                return True
            return str(event.get_type()) in self.eligible_relative_events
        if self.event_filters == []:
            return True
        return str(event.get_type()) in self.eligible_events

    def add_event(self, event: Tuple, relative=False):
        """Add event to timeline if needed."""
        if self.discard_empty:
            if event[0].date.sortval == 0:
                return
        if self.end_date:
            if self.end_date.match(event[0].date, comparison="<"):
                return
        if self.start_date:
            if self.start_date.match(event[0].date, comparison=">"):
                return
        for item in self.timeline:
            if item[0].handle == event[0].handle:
                return
        if self.is_eligible(event[0], relative):
            if self.ratings:
                count, confidence = get_rating(self.db_handle, event[0])
                event[0].citations = count
                event[0].confidence = confidence
            self.timeline.append(event)

    def add_person(
        self,
        handle: str,
        anchor: bool = False,
        start: bool = True,
        end: bool = True,
        ancestors: int = 1,
        offspring: int = 1,
    ):
        """Add events for a person to the timeline."""
        if self.anchor_person and handle == self.anchor_person.handle:
            return
        person = self.db_handle.get_person_from_handle(handle)
        if person.handle not in self.birth_dates:
            event = get_birth_or_fallback(self.db_handle, person)
            if event:
                self.birth_dates.update({person.handle: event.date})
        for event_ref in person.event_ref_list:
            event = self.db_handle.get_event_from_handle(event_ref.ref)
            self.add_event((event, person, "self"))
        if anchor and not self.anchor_person:
            self.anchor_person = person
            self.depth = max(ancestors, offspring) + 1
            if self.start_date is None and self.end_date is None:
                if len(self.timeline) > 0:
                    if start or end:
                        self.timeline.sort(
                            key=lambda x: x[0].get_date_object().get_sort_value()
                        )
                        if start:
                            self.start_date = self.timeline[0][0].date
                        if end:
                            if self.is_death_indicator(self.timeline[-1][0]):
                                self.end_date = self.timeline[-1][0].date
                            else:
                                data = probably_alive_range(person, self.db_handle)
                                self.end_date = data[1]

            for family in person.parent_family_list:
                self.add_family(family, ancestors=ancestors)

            for family in person.family_list:
                self.add_family(
                    family, anchor=person, ancestors=ancestors, offspring=offspring
                )
        else:
            for family in person.family_list:
                self.add_family(family, anchor=person, events_only=True)

    def add_relative(self, handle: str, ancestors: int = 1, offspring: int = 1):
        """Add events for a relative of the anchor person."""
        person = self.db_handle.get_person_from_handle(handle)
        calculator = get_relationship_calculator(reinit=True, clocale=self.locale)
        calculator.set_depth(self.depth)
        relationship = calculator.get_one_relationship(
            self.db_handle, self.anchor_person, person
        )
        found = False
        if self.relative_filters:
            for relative in self.relative_filters:
                if relative in relationship:
                    found = True
                    break
        if not found:
            return

        if self.relative_event_filters:
            for event_ref in person.event_ref_list:
                event = self.db_handle.get_event_from_handle(event_ref.ref)
                self.add_event((event, person, relationship), relative=True)

        event = get_birth_or_fallback(self.db_handle, person)
        if event:
            self.add_event((event, person, relationship), relative=True)
            if person.handle not in self.birth_dates:
                self.birth_dates.update({person.handle: event.date})

        event = get_death_or_fallback(self.db_handle, person)
        if event:
            self.add_event((event, person, relationship), relative=True)

        for family_handle in person.family_list:
            family = self.db_handle.get_family_from_handle(family_handle)

            event = get_marriage_or_fallback(self.db_handle, family)
            if event:
                self.add_event((event, person, relationship), relative=True)

            event = get_divorce_or_fallback(self.db_handle, family)
            if event:
                self.add_event((event, person, relationship), relative=True)

            if offspring > 1:
                for child_ref in family.child_ref_list:
                    self.add_relative(child_ref.ref, offspring=offspring - 1)

        if ancestors > 1:
            if "father" in relationship or "mother" in relationship:
                for family_handle in person.parent_family_list:
                    self.add_family(
                        family_handle, include_children=False, ancestors=ancestors - 1
                    )

    def add_family(
        self,
        handle: str,
        anchor: Union[Person, None] = None,
        include_children: bool = True,
        ancestors: int = 1,
        offspring: int = 1,
        events_only: bool = False,
    ):
        """Add events for all family members to the timeline."""
        family = self.db_handle.get_family_from_handle(handle)
        if anchor:
            for event_ref in family.event_ref_list:
                event = self.db_handle.get_event_from_handle(event_ref.ref)
                self.add_event((event, anchor, "self"))
            if events_only:
                return
        if self.anchor_person:
            if (
                family.father_handle
                and family.father_handle != self.anchor_person.handle
            ):
                self.add_relative(family.father_handle, ancestors=ancestors)
            if (
                family.mother_handle
                and family.mother_handle != self.anchor_person.handle
            ):
                self.add_relative(family.mother_handle, ancestors=ancestors)
            if include_children:
                for child in family.child_ref_list:
                    if child.ref != self.anchor_person.handle:
                        self.add_relative(child.ref, offspring=offspring)
        else:
            if family.father_handle:
                self.add_person(family.father_handle)
            if family.mother_handle:
                self.add_person(family.mother_handle)
            for child in family.child_ref_list:
                self.add_person(child.ref)

    def sort_events(self):
        """Sort events in the timeline."""
        self.timeline.sort(key=lambda x: x[0].get_date_object().get_sort_value())

    def events(self):
        """Return events from the timeline."""
        self.timeline.sort(key=lambda x: x[0].get_date_object().get_sort_value())
        return self.timeline
