#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022       Christopher Horn
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
StatisticsCardGroup
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import (
    ChildRefType,
    EventType,
    EventRoleType,
    FamilyRelType,
    NoteType,
    PlaceType,
    RepositoryType,
    SourceMediaType,
)

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..cards.card_text import TextCard
from ..common.common_strings import UNKNOWN
from .group_list import CardGroupList
from ..services.service_statistics import StatisticsService
from ..services.statistics_labels import (
    PERSON_LABELS,
    PARTICIPANT_LABELS,
    ASSOCIATION_LABELS,
    FAMILY_LABELS,
    CHILD_LABELS,
    EVENT_LABELS,
    LDSORD_PERSON_LABELS,
    LDSORD_FAMILY_LABELS,
    PLACE_LABELS,
    UNCITED_LABELS,
    CITATION_LABELS,
    SOURCE_LABELS,
    REPOSITORY_LABELS,
    MEDIA_LABELS,
    NOTE_LABELS,
    PRIVATE_LABELS,
    TAG_LABELS,
    BOOKMARK_LABELS,
)

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# Helper functions to prepare statistics for rendering
#
# ------------------------------------------------------------------------
def get_person_statistics(data):
    """
    Return person statistics for rendering.
    """
    people = data.get("person")
    return prepare_statistics(
        [
            "incomplete_names",
            "alternate_names",
            "no_family_connection",
            "male_total",
            "male_living",
            "male_births_missing",
            "male_births_missing_date",
            "male_births_missing_place",
            "male_deaths_missing",
            "male_deaths_missing_date",
            "male_deaths_missing_place",
            "female_total",
            "female_living",
            "female_births_missing",
            "female_births_missing_date",
            "female_births_missing_place",
            "female_deaths_missing",
            "female_deaths_missing_date",
            "female_deaths_missing_place",
            "unknown_total",
            "unknown_living",
            "unknown_births_missing",
            "unknown_births_missing_date",
            "unknown_births_missing_place",
            "unknown_deaths_missing",
            "unknown_deaths_missing_date",
            "unknown_deaths_missing_place",
        ],
        people,
        PERSON_LABELS,
        total_key="total",
    )


def get_family_statistics(data):
    """
    Return family statistics for rendering.
    """
    families = data.get("family")
    result = prepare_statistics(
        [
            "surname_total",
            "missing_one",
            "missing_both",
            "no_events",
            "no_child",
        ],
        families,
        FAMILY_LABELS,
        total_key="total",
    )
    return prepare_type_statistics(
        result, families, FamilyRelType, FAMILY_LABELS, type_key="relations"
    )


def get_child_statistics(data):
    """
    Return child statistics for rendering.
    """
    children = data.get("children")
    result = prepare_statistics(["refs"], children, CHILD_LABELS)
    result = prepare_type_statistics(
        result,
        children,
        ChildRefType,
        CHILD_LABELS,
        type_key="father_relations",
    )
    return prepare_type_statistics(
        result,
        children,
        ChildRefType,
        CHILD_LABELS,
        type_key="mother_relations",
    )


def get_event_statistics(data):
    """
    Return event statistics for rendering.
    """
    events = data.get("event")
    result = prepare_statistics(
        ["no_date", "no_place", "no_description"],
        events,
        EVENT_LABELS,
        total_key="total",
    )
    return prepare_type_statistics(result, events, EventType, EVENT_LABELS)


def get_ldsord_person_statistics(data):
    """
    Return LDS person ordinance statistics for rendering.
    """
    ldsord = data.get("ldsord_person")
    return prepare_statistics(
        [
            "ldsord",
            "ldsord_refs",
            "no_date",
            "no_place",
            "no_temple",
            "no_status",
            "no_family",
        ],
        ldsord,
        LDSORD_PERSON_LABELS,
    )


def get_ldsord_family_statistics(data):
    """
    Return LDS family ordinance statistics for rendering.
    """
    ldsord = data.get("ldsord_family")
    return prepare_statistics(
        [
            "ldsord",
            "ldsord_refs",
            "no_date",
            "no_place",
            "no_temple",
            "no_status",
        ],
        ldsord,
        LDSORD_FAMILY_LABELS,
    )


def get_participant_statistics(data):
    """
    Return participant statistics for rendering.
    """
    participants = data.get("participant")
    result = prepare_statistics(
        ["refs"], participants, PARTICIPANT_LABELS, total_key="total"
    )
    result = prepare_type_statistics(
        result,
        participants,
        EventRoleType,
        PARTICIPANT_LABELS,
        type_key="person_roles",
    )
    return prepare_type_statistics(
        result,
        participants,
        EventRoleType,
        PARTICIPANT_LABELS,
        type_key="family_roles",
    )


def get_association_statistics(data):
    """
    Return association statistics for rendering.
    """
    associations = data.get("association")
    result = prepare_statistics(
        ["refs"], associations, ASSOCIATION_LABELS, total_key="total"
    )
    types = associations.get("types")
    if types:
        result.append((ASSOCIATION_LABELS["types"], "", None))
        for (key, value) in types.items():
            if not key:
                key = UNKNOWN
            result.append(("> %s" % key, value, None))
    return result


def get_place_statistics(data):
    """
    Return place statistics for rendering.
    """
    places = data.get("place")
    result = prepare_statistics(
        ["no_name", "no_latitude", "no_longitude", "no_code"],
        places,
        PLACE_LABELS,
        total_key="total",
    )
    return prepare_type_statistics(result, places, PlaceType, PLACE_LABELS)


def get_media_statistics(data):
    """
    Return media statistics for rendering.
    """
    media = data.get("media")
    return prepare_statistics(
        [
            "size",
            "no_path",
            "no_file",
            "no_description",
            "no_date",
            "no_mime",
            "person",
            "person_refs",
            "person_missing_region",
            "family",
            "family_refs",
            "event",
            "event_refs",
            "place",
            "place_refs",
            "source",
            "source_refs",
            "citation",
            "citation_refs",
        ],
        media,
        MEDIA_LABELS,
        total_key="total",
    )


def get_uncited_statistics(data):
    """
    Return uncited statistics for rendering.
    """
    uncited = data.get("uncited")
    return prepare_statistics(
        [
            "names",
            "male",
            "male_births",
            "male_deaths",
            "female",
            "female_births",
            "female_deaths",
            "unknown",
            "unknown_births",
            "unknown_deaths",
            "family",
            "child",
            "association",
            "event",
            "ldsord_person",
            "ldsord_family",
            "place",
            "media",
        ],
        uncited,
        UNCITED_LABELS,
    )


def get_citation_statistics(data):
    """
    Return citation statistics for rendering.
    """
    citations = data.get("citation")
    result = prepare_statistics(
        [
            "no_source",
            "no_page",
            "no_date",
        ],
        citations,
        CITATION_LABELS,
        total_key="total",
    )
    types = citations.get("confidence")
    if types:
        total = citations.get("total")
        result.append((CITATION_LABELS["confidence"], "", None))
        for (key, value) in types.items():
            result.append(
                ("> %s" % CITATION_LABELS[key], value, value * 100 / total)
            )
    return result


def get_source_statistics(data):
    """
    Return source statistics for rendering.
    """
    sources = data.get("source")
    result = prepare_statistics(
        [
            "no_title",
            "no_author",
            "no_pubinfo",
            "no_abbrev",
            "no_repository",
            "repository_refs",
            "no_call_number",
        ],
        sources,
        SOURCE_LABELS,
        total_key="total",
    )
    return prepare_type_statistics(
        result, sources, SourceMediaType, SOURCE_LABELS
    )


def get_repository_statistics(data):
    """
    Return repository statistics for rendering.
    """
    repositories = data.get("repository")
    result = prepare_statistics(
        ["no_name", "no_address"],
        repositories,
        REPOSITORY_LABELS,
        total_key="total",
    )
    return prepare_type_statistics(
        result, repositories, RepositoryType, REPOSITORY_LABELS
    )


def get_note_statistics(data):
    """
    Return note statistics for rendering.
    """
    notes = data.get("note")
    result = prepare_statistics(
        ["no_text"], notes, NOTE_LABELS, total_key="total"
    )
    return prepare_type_statistics(result, notes, NoteType, NOTE_LABELS)


def get_tag_statistics(data):
    """
    Return tag statistics for rendering.
    """
    tags = data.get("tag")
    return prepare_statistics(
        [
            "male",
            "female",
            "unknown",
            "family",
            "event",
            "place",
            "media",
            "source",
            "citation",
            "repository",
            "note",
        ],
        tags,
        TAG_LABELS,
        total_key="total",
    )


def get_bookmark_statistics(data):
    """
    Return bookmark statistics for rendering.
    """
    bookmarks = data.get("bookmark")
    return prepare_statistics(
        [
            "person",
            "family",
            "event",
            "place",
            "media",
            "source",
            "citation",
            "repository",
            "note",
        ],
        bookmarks,
        BOOKMARK_LABELS,
        total_key="total",
    )


def get_private_statistics(data):
    """
    Return privacy statistics for rendering.
    """
    private = data.get("privacy")
    return prepare_statistics(
        [
            "names",
            "male",
            "male_living_not",
            "male_births",
            "male_deaths",
            "female",
            "female_living_not",
            "female_births",
            "female_deaths",
            "unknown",
            "unknown_living_not",
            "unknown_births",
            "unknown_deaths",
            "family",
            "child",
            "association",
            "event",
            "ldsord_person",
            "ldsord_family",
            "participant",
            "family_participant",
            "place",
            "media",
            "citation",
            "source",
            "repository",
            "note",
        ],
        private,
        PRIVATE_LABELS,
    )


def prepare_statistics(keys, data, labels, total_key=None):
    """
    Prepare statistics data for rendering.
    """
    if total_key:
        total = data.get(total_key) or 0
        result = [(labels["total"], total, None)]
    else:
        total = 0
        result = []
    for key in keys:
        item = data.get(key) or 0
        if total > 0 and str(item).isnumeric() and "size" not in key:
            result.append((labels[key], item, item * 100 / total))
        else:
            result.append((labels[key], item, None))
    return result


def prepare_type_statistics(
    result, data, object_class, labels, type_key="types"
):
    """
    Prepare types or roles for rendering.
    """
    if data.get(type_key):
        output = []
        statistics = data.get(type_key)
        for key in statistics:
            object_type = object_class().unserialize(key)
            output.append(("> %s" % object_type, statistics[key], None))
        if output:
            output.sort(key=lambda x: x[1], reverse=True)
            result.append((labels[type_key], "", None))
            result = result + output
    return result


PREPARE_GROUP = {
    "person": get_person_statistics,
    "family": get_family_statistics,
    "child": get_child_statistics,
    "association": get_association_statistics,
    "event": get_event_statistics,
    "ldsordperson": get_ldsord_person_statistics,
    "ldsordfamily": get_ldsord_family_statistics,
    "participant": get_participant_statistics,
    "place": get_place_statistics,
    "media": get_media_statistics,
    "note": get_note_statistics,
    "bookmark": get_bookmark_statistics,
    "tag": get_tag_statistics,
    "repository": get_repository_statistics,
    "source": get_source_statistics,
    "citation": get_citation_statistics,
    "uncited": get_uncited_statistics,
    "privacy": get_private_statistics,
}


# ------------------------------------------------------------------------
#
# StatisticsCardGroup
#
# ------------------------------------------------------------------------
class StatisticsCardGroup(CardGroupList):
    """
    The StatisticsCardGroup class provides a container for managing
    statistical information about the database.
    """

    def __init__(self, grstate, groptions, group, title):
        CardGroupList.__init__(
            self, grstate, groptions, None, enable_drop=False
        )
        statistics_service = StatisticsService(grstate.dbstate)
        data = statistics_service.get_data()
        key = group.split("-")[1]
        result = PREPARE_GROUP[key](data)

        output = []
        for (label, value, bonus) in result:
            if bonus:
                output.append((label, "{0}   ({1:.2f}%)".format(value, bonus)))
            else:
                output.append((label, value))

        card = TextCard(grstate, groptions, title=title, data=output)
        self.add_card(card)
