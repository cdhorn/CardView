#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2015-2016  Nick Hall
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
Status indicator utility functions
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Event, EventType, Family, Person

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import get_confidence

_ = glocale.translation.sgettext


def get_status_ranking(
    db,
    obj,
    rank_list=None,
    alert_list=None,
    alert_minimum=0,
    required_list=None,
):
    """
    Evaluate object attributes to collect data for confidence ranking.
    """
    rank_list = rank_list or []
    alert_list = alert_list or []
    required_list = required_list or []

    found_list = []
    missing_alerts = []
    confidence_alerts = []

    total_rank_items = 0
    total_rank_confidence = 0

    vital_count = 2
    object_bucket, events_bucket = collect_primary_object_data(
        db, obj, rank_list
    )
    for event_data in events_bucket:
        (
            event,
            event_type,
            primary,
            total_count,
            dummy_total_confidence,
            highest_confidence,
        ) = event_data
        if event_type in [EventType.BIRTH, EventType.DEATH]:
            vital_count = vital_count - 1
        event_name = event_type.xml_str()
        if primary and event_name in alert_list:
            if total_count == 0:
                confidence_alerts.append(
                    (event, "".join((str(event_type), ": ", _("Missing"))))
                )
            elif highest_confidence < alert_minimum:
                confidence_alerts.append(
                    (
                        event,
                        "".join(
                            (
                                str(event_type),
                                ": ",
                                get_confidence(highest_confidence),
                            )
                        ),
                    )
                )
        if (
            primary
            and event_name in required_list
            and event_name not in found_list
        ):
            found_list.append(event_name)

        if primary and event_name in rank_list or "events" in rank_list:
            total_rank_items = total_rank_items + 1
            total_rank_confidence = total_rank_confidence + highest_confidence

    if vital_count > 0:
        total_rank_items = total_rank_items + vital_count

    for item in required_list:
        if item not in found_list:
            missing_alerts.append(item)

    for object_data in object_bucket:
        total_rank_items = total_rank_items + 1
        total_rank_confidence = total_rank_confidence + object_data[5]

    return (
        total_rank_items,
        total_rank_confidence,
        missing_alerts,
        confidence_alerts,
    )


def collect_primary_object_data(db, obj, rank_list):
    """
    Collect all object and event data for a primary object.
    """
    buckets = ([], [])
    if isinstance(obj, Person):
        collect_person_data(db, obj, rank_list, buckets)
    elif isinstance(obj, Family):
        collect_family_data(db, obj, rank_list, buckets)
    return buckets[0], buckets[1]


def collect_person_data(db, person, rank_list, buckets, include_family=True):
    """
    Collect all citation metrics associated with a person.
    """
    (object_bucket, events_bucket) = buckets
    person_handle = person.get_handle()

    collect_object_data(db, person, rank_list, object_bucket)
    collect_event_data(db, person, events_bucket)
    if include_family:
        if "object" in rank_list:
            for handle in person.get_parent_family_handle_list():
                family = db.get_family_from_handle(handle)
                for child_ref in family.get_child_ref_list():
                    if child_ref.ref == person_handle:
                        collect_child_object_data(
                            db, family, _("Child"), [child_ref], object_bucket
                        )
                        break

        for handle in person.get_family_handle_list():
            family = db.get_family_from_handle(handle)
            collect_object_data(db, family, rank_list, object_bucket)
            collect_event_data(db, family, events_bucket)


def collect_family_data(db, obj, rank_list, buckets, skip_handle=None):
    """
    Collect most citation metrics associated with a family.
    If requested this can include spouses and children.
    """
    (object_bucket, events_bucket) = buckets

    collect_object_data(db, obj, rank_list, object_bucket)
    collect_event_data(db, obj, events_bucket)

    if "spouses" in rank_list:
        father_handle = obj.get_father_handle()
        if father_handle and father_handle != skip_handle:
            father = db.get_person_from_handle(father_handle)
            collect_person_data(
                db, father, rank_list, buckets, include_family=False
            )
        mother_handle = obj.get_mother_handle()
        if mother_handle and mother_handle != skip_handle:
            mother = db.get_person_from_handle(mother_handle)
            collect_person_data(
                db, mother, rank_list, buckets, include_family=False
            )

    if "children" in rank_list:
        for child_ref in obj.get_child_ref_list():
            if child_ref != skip_handle:
                child = db.get_person_from_handle(child_ref.ref)
                collect_person_data(
                    db, child, rank_list, buckets, include_family=False
                )


def collect_object_data(db, obj, rank_list, bucket):
    """
    Collect object citation metrics excluding their events.
    """
    person = False
    if "object" in rank_list:
        if isinstance(obj, Person):
            description = _("Person")
            person = True
        elif isinstance(obj, Family):
            description = _("Family")
        elif isinstance(obj, Event):
            description = _("Event")
        collect_child_object_data(db, obj, description, [obj], bucket)
    if person and "names" in rank_list:
        names = [obj.get_primary_name()] + obj.get_alternate_names()
        collect_child_object_data(db, obj, _("Name"), names, bucket)
    if "ordinances" in rank_list:
        collect_child_object_data(
            db, obj, _("Ordinance"), obj.get_lds_ord_list(), bucket
        )
    if "attributes" in rank_list:
        collect_child_object_data(
            db, obj, _("Attribute"), obj.get_attribute_list(), bucket
        )
    if person and "associations" in rank_list:
        collect_child_object_data(
            db, obj, _("Association"), obj.get_person_ref_list(), bucket
        )
    if person and "addresses" in rank_list:
        collect_child_object_data(
            db, obj, _("Address"), obj.get_address_list(), bucket
        )
    if "media" in rank_list:
        collect_child_object_data(
            db, obj, _("Media"), obj.get_media_list(), bucket
        )


def collect_child_object_data(db, obj, description, child_list, bucket):
    """
    Collect child object citation metrics.
    """
    for child_obj in child_list:
        (
            total_count,
            total_confidence,
            highest_confidence,
        ) = get_citation_metrics(db, child_obj)
        bucket.append(
            (
                obj,
                child_obj,
                description,
                total_count,
                total_confidence,
                highest_confidence,
            )
        )


def collect_event_data(db, obj, bucket):
    """
    Collect event citation metrics.
    """
    vital_handles = get_preferred_vital_handles(obj)
    seen_list = []
    for event_ref in obj.get_event_ref_list():
        event = db.get_event_from_handle(event_ref.ref)
        event_type = event.get_type()
        event_name = event_type.xml_str()
        (
            total_count,
            total_confidence,
            highest_confidence,
        ) = get_citation_metrics(db, event)
        primary = False
        if event_name not in seen_list:
            if event_type in [EventType.BIRTH, EventType.DEATH]:
                if event_ref.ref in vital_handles:
                    primary = True
            else:
                primary = True
            seen_list.append(event_name)
        bucket.append(
            (
                event,
                event_type,
                primary,
                total_count,
                total_confidence,
                highest_confidence,
            )
        )


def get_preferred_vital_handles(obj):
    """
    Return list of preferred birth and death event handles.
    """
    vital_handles = []
    if isinstance(obj, Person):
        birth_ref = obj.get_birth_ref()
        if birth_ref:
            vital_handles.append(birth_ref.ref)
        death_ref = obj.get_death_ref()
        if death_ref:
            vital_handles.append(death_ref.ref)
    return vital_handles


def get_citation_metrics(db, obj):
    """
    Examine citations for an object and return what metrics are available.
    """
    total_confidence = 0
    highest_confidence = 0
    citations = obj.get_citation_list()
    for handle in citations:
        citation = db.get_citation_from_handle(handle)
        total_confidence = total_confidence + citation.confidence
        if citation.confidence > highest_confidence:
            highest_confidence = citation.confidence
    return len(citations), total_confidence, highest_confidence
