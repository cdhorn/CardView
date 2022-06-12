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
TimelineCardGroup
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
from ..common.timeline import EVENT_CATEGORIES, RELATIVES, GrampsTimeline
from ..cards import (
    AddressCard,
    CitationCard,
    EventRefCard,
    LDSOrdinanceCard,
    MediaCard,
    NameCard,
)
from .group_list import CardGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TimelineCardGroup Class
#
# ------------------------------------------------------------------------
class TimelineCardGroup(CardGroupList):
    """
    The TimelineCardGroup generates an event timeline for a person
    that may also optionally include events for close family if choosen.
    """

    def __init__(self, grstate, groptions, obj):
        CardGroupList.__init__(
            self, grstate, groptions, obj, enable_drop=False
        )
        self.options = {
            "categories": [],
            "relations": [],
            "relation_categories": [],
            "ancestors": 1,
            "offspring": 1,
        }
        self.prepare_options()

        self.timeline = GrampsTimeline(
            grstate.dbstate.db,
            events=self.options["categories"],
            relatives=self.options["relations"],
            relative_events=self.options["relation_categories"],
        )
        if self.group_base.obj_type == "Person":
            self.timeline.set_person(
                obj.handle,
                ancestors=self.options["ancestors"],
                offspring=self.options["offspring"],
            )
        elif self.group_base.obj_type == "Family":
            self.timeline.set_family(
                obj.handle,
                ancestors=self.options["ancestors"],
                offspring=self.options["offspring"],
            )
        elif self.group_base.obj_type == "Place":
            self.timeline.set_place(obj.handle)

        timeline = self.prepare_timeline(obj)
        for (dummy_sortval, timeline_obj_type, timeline_obj, item) in timeline:
            if timeline_obj_type == "event":
                (
                    dummy_event,
                    event_ref,
                    event_person,
                    event_family,
                    dummy_relation,
                    dummy_category,
                ) = item
                obj = event_person
                if event_family:
                    obj = event_family
                self.add_card(
                    EventRefCard(
                        grstate,
                        groptions,
                        obj,
                        event_ref,
                    )
                )
            elif timeline_obj_type == "media":
                (media, dummy_media_ref) = item
                self.add_card(MediaCard(grstate, groptions, media))
            elif timeline_obj_type == "address":
                self.add_card(
                    AddressCard(
                        grstate,
                        groptions,
                        timeline_obj,
                        item,
                    )
                )
            elif timeline_obj_type == "name":
                self.add_card(
                    NameCard(
                        grstate,
                        groptions,
                        timeline_obj,
                        item,
                    )
                )
            elif timeline_obj_type == "citation":
                self.add_card(
                    CitationCard(
                        grstate,
                        groptions,
                        item,
                    )
                )
            elif timeline_obj_type == "ldsord":
                self.add_card(
                    LDSOrdinanceCard(
                        grstate,
                        groptions,
                        timeline_obj,
                        item,
                    )
                )
        self.show_all()

    def prepare_options(self):
        """
        Parse and prepare filter groups and options.
        """
        for category in EVENT_CATEGORIES:
            if self.get_option("show-class-%s" % category):
                self.options["categories"].append(category)
            if self.group_base.obj_type == "Person" and self.get_option(
                "show-family-class-%s" % category
            ):
                self.options["relation_categories"].append(category)

        if self.group_base.obj_type == "Person":
            for relation in RELATIVES:
                if self.get_option("show-family-%s" % relation):
                    self.options["relations"].append(relation)

        self.options["ancestors"] = self.get_option("generations-ancestors")
        self.options["offspring"] = self.get_option("generations-offspring")

    def prepare_timeline(self, obj):
        """
        Prepare timeline of sorted events.
        """
        timeline = []
        for (sortval, item) in self.timeline.events(raw=True):
            timeline.append((sortval, "event", None, item))

        if (
            not self.groptions.age_base
            and self.group_base.obj_type == "Person"
            and self.get_option("show-age")
        ):
            birth_ref = obj.get_birth_ref()
            if birth_ref:
                event = self.grstate.dbstate.db.get_event_from_handle(
                    birth_ref.ref
                )
                if event:
                    self.groptions.set_age_base(event.get_date_object())

        timeline = self.extract_objects(timeline)
        try:
            self.groptions.set_ref_mode(
                self.grstate.config.get(
                    "timeline.%s.reference-mode"
                    % self.group_base.obj_type.lower()
                )
            )
        except AttributeError:
            self.groptions.set_ref_mode(0)

        if self.group_base.obj_type == "Person":
            self.groptions.set_relation(obj)

        timeline.sort(key=lambda x: x[0])
        maximum = self.grstate.config.get("group.event.max-per-group")
        timeline = timeline[:maximum]
        return timeline

    def extract_objects(self, timeline):
        """
        Examine and extract other objects to add to timeline if needed.
        """
        if self.get_option("include-addresses"):
            timeline = timeline + self.extract_object_type("addresses")
        if self.get_option("include-citations"):
            timeline = timeline + self.extract_object_type("citations")
        if self.get_option("include-media"):
            timeline = timeline + self.extract_object_type("media")
        if self.get_option("include-names"):
            timeline = timeline + self.extract_object_type("names")
        if self.get_option("include-ldsords"):
            timeline = timeline + self.extract_object_type("ldsords")
        return timeline

    def extract_object_type(self, extract_type):
        """
        Extract objects if they have an associated date.
        """
        extractors = {
            "names": extract_names,
            "addresses": extract_addresses,
            "media": self.extract_media,
            "citations": self.extract_citations,
            "ldsords": extract_ordinances,
        }
        extract = extractors.get(extract_type)

        obj_list = []
        if self.group_base.obj_type in ["Person", "Place"]:
            obj_list = extract(self.group_base.obj)
        elif self.group_base.obj_type == "Family":
            if self.group_base.obj.mother_handle:
                mother = self.fetch(
                    "Person", self.group_base.obj.mother_handle
                )
                obj_list = obj_list + extract(mother)
            if self.group_base.obj.father_handle:
                father = self.fetch(
                    "Person", self.group_base.obj.father_handle
                )
                obj_list = obj_list + extract(father)
            if self.group_base.obj.child_ref_list:
                for child_ref in self.group_base.obj.child_ref_list:
                    child = self.fetch("Person", child_ref.ref)
                    obj_list = obj_list + extract(child)
        return obj_list

    def extract_citations(self, obj):
        """
        Return list of citations with a date value.
        """
        citations = []
        for handle in obj.citation_list:
            citation = self.fetch("Citation", handle)
            date = citation.get_date_object()
            if date and date.is_valid() and date.sortval:
                citations.append((date.sortval, "citation", obj, citation))
        return citations

    def extract_media(self, obj):
        """
        Return list of media items with a date value.
        """
        media = []
        for media_ref in obj.media_list:
            item = self.fetch("Media", media_ref.ref)
            date = item.get_date_object()
            if date and date.is_valid() and date.sortval:
                media.append((date.sortval, "media", obj, (item, media_ref)))
        return media


def extract_addresses(obj):
    """
    Return list of addresses with a date value.
    """
    addresses = []
    for address in obj.address_list:
        date = address.get_date_object()
        if date and date.is_valid() and date.sortval:
            addresses.append((date.sortval, "address", obj, address))
    return addresses


def extract_names(obj):
    """
    Return list of names with a date value.
    """
    names = []
    for name in obj.alternate_names:
        date = name.get_date_object()
        if date and date.is_valid() and date.sortval:
            names.append((date.sortval, "name", obj, name))
    return names


def extract_ordinances(obj):
    """
    Return list of ordinance items with a date value.
    """
    ordinances = []
    for ordinance in obj.lds_ord_list:
        date = ordinance.get_date_object()
        if date and date.is_valid() and date.sortval:
            ordinances.append((date.sortval, "ldsord", obj, ordinance))
    return ordinances
