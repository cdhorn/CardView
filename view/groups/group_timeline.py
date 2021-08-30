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
TimelineGrampsFrameGroup
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
from ..frames.frame_address import AddressGrampsFrame
from ..frames.frame_citation import CitationGrampsFrame
from ..frames.frame_event import EventGrampsFrame
from ..frames.frame_image import ImageGrampsFrame
from ..frames.frame_name import NameGrampsFrame
from ..frames.frame_utils import get_gramps_object_type, get_key_person_events
from .group_list import GrampsFrameGroupList
from ..timeline import EVENT_CATEGORIES, RELATIVES, Timeline

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TimelineGrampsFrameGroup
#
# ------------------------------------------------------------------------
class TimelineGrampsFrameGroup(GrampsFrameGroupList):
    """
    The TimelineGrampsFrameGroup generates an event timeline for a person
    that may also optionally include events for close family if choosen.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(
            self, grstate, groptions, enable_drop=False
        )
        self.obj = obj
        self.obj_type = get_gramps_object_type(obj)
        self.categories = []
        self.relations = []
        self.relation_categories = []
        self.ancestors = 1
        self.offspring = 1
        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        self.prepare_timeline_filters()
        self.timeline = Timeline(
            grstate.dbstate.db,
            events=self.categories,
            relatives=self.relations,
            relative_events=self.relation_categories,
        )
        if self.obj_type == "Person":
            self.timeline.set_person(
                obj.get_handle(),
                ancestors=self.ancestors,
                offspring=self.offspring,
            )
        elif self.obj_type == "Family":
            self.timeline.set_family(
                obj.get_handle(),
                ancestors=self.ancestors,
                offspring=self.offspring,
            )

        timeline = []
        for (sortval, item) in self.timeline.events(raw=True):
            timeline.append((sortval, "event", None, item))

        person = None
        if self.obj_type == "Person" and self.get_option("show-age"):
            person = self.obj
            key_events = get_key_person_events(
                grstate.dbstate.db, self.obj, birth_only=True
            )
            if key_events["birth"] and key_events["birth"].date:
                self.groptions.set_age_base(key_events["birth"].date)

        if self.get_option("include-addresses"):
            timeline = timeline + self.extract_objects("addresses")
        if self.get_option("include-names"):
            timeline = timeline + self.extract_objects("names")
        if self.get_option("include-media"):
            timeline = timeline + self.extract_objects("media")
        if self.get_option("include-citations"):
            timeline = timeline + self.extract_objects("citations")

        timeline.sort(key=lambda x: x[0])
        for (sortval, obj_type, obj, item) in timeline:
            if obj_type == "event":
                (
                    event,
                    event_ref,
                    event_person,
                    event_family,
                    relation,
                    category,
                ) = item
                frame = EventGrampsFrame(
                    grstate,
                    groptions,
                    person,
                    event,
                    event_ref,
                    event_person,
                    event_family,
                    relation,
                    category,
                )
            elif obj_type == "media":
                (media, media_ref) = item
                frame = ImageGrampsFrame(
                    grstate, groptions, media, media_ref=media_ref
                )
            elif obj_type == "address":
                frame = AddressGrampsFrame(
                    grstate,
                    groptions,
                    obj,
                    item,
                )
            elif obj_type == "name":
                frame = NameGrampsFrame(
                    grstate,
                    groptions,
                    obj,
                    item,
                )
            elif obj_type == "citation":
                frame = CitationGrampsFrame(
                    grstate,
                    groptions,
                    item,
                )
            self.add_frame(frame)
        self.show_all()

    def prepare_timeline_filters(self):
        """
        Parse and prepare filter groups.
        """
        for category in EVENT_CATEGORIES:
            if self.get_option("show-class-{}".format(category)):
                self.categories.append(category)
            if self.obj_type == "Person":
                if self.get_option("show-family-class-{}".format(category)):
                    self.relation_categories.append(category)

        if self.obj_type == "Person":
            for relation in RELATIVES:
                if self.get_option("show-family-{}".format(relation)):
                    self.relations.append(relation)

        self.ancestors = self.get_option("generations-ancestors")
        self.offspring = self.get_option("generations-offspring")

    def extract_objects(self, extract_type):
        """
        Extract objects if they have an associated date.
        """
        if extract_type == "names":
            extract = extract_names
        elif extract_type == "addresses":
            extract = extract_addresses
        elif extract_type == "media":
            extract = self.extract_media
        elif extract_type == "citations":
            extract = self.extract_citations

        obj_list = []
        if self.obj_type == "Person":
            obj_list = extract(self.grstate.dbstate.db, self.obj)
        elif self.obj_type == "Family":
            if self.obj.get_mother_handle():
                mother = self.fetch("Person", self.obj.get_mother_handle())
                obj_list = obj_list + extract(self.grstate.dbstate.db, mother)
            if self.obj.get_father_handle():
                father = self.fetch("Person", self.obj.get_father_handle())
                obj_list = obj_list + extract(self.grstate.dbstate.db, father)
            if self.obj.get_child_ref_list():
                for child_ref in self.obj.get_child_ref_list():
                    child = self.fetch("Person", child_ref.ref)
                    obj_list = obj_list + extract(
                        self.grstate.dbstate.db, child
                    )
        return obj_list

    def extract_media(self, _dummy_arg, obj):
        """
        Return list of media items with a date value.
        """
        media = []
        for media_ref in obj.get_media_list():
            item = self.fetch("Media", media_ref.ref)
            date = item.get_date_object()
            if date and date.is_valid() and date.get_sort_value():
                media.append(
                    (date.get_sort_value(), "media", obj, (item, media_ref))
                )
        return media

    def extract_citations(self, _dummy_arg, obj):
        """
        Return list of citations with a date value.
        """
        citations = []
        for handle in obj.get_citation_list():
            citation = self.fetch("Citation", handle)
            date = citation.get_date_object()
            if date and date.is_valid() and date.get_sort_value():
                citations.append(
                    (date.get_sort_value(), "citation", obj, citation)
                )
        return citations


def extract_addresses(db, obj):
    """
    Return list of addresses with a date value.
    """
    addresses = []
    for address in obj.get_address_list():
        date = address.get_date_object()
        if date and date.is_valid() and date.get_sort_value():
            addresses.append((date.get_sort_value(), "address", obj, address))
    return addresses


def extract_names(db, obj):
    """
    Return list of names with a date value.
    """
    names = []
    for name in obj.get_alternate_names():
        date = name.get_date_object()
        if date and date.is_valid() and date.get_sort_value():
            names.append((date.get_sort_value(), "name", obj, name))
    return names
