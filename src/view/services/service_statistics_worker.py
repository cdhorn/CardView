#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2010       Jakim Friant
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
Statistics service worker
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import io
import os
import sys
import time
import pickle
import argparse
from bisect import bisect
from multiprocessing import Process, Queue

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.datehandler import get_date
from gramps.gen.db import DBLOCKFN, DBMODE_R
from gramps.gen.db.utils import (
    lookup_family_tree,
    make_database,
    write_lock_file,
)
from gramps.gen.lib import Citation, Person, EventType
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.file import media_path_full


def examine_people(args, queue=None):
    """
    Parse and analyze people.
    """

    def get_gender_stats(gender_stats, gender):
        """
        Return gender statistics.
        """
        if gender not in gender_stats:
            gender_stats[gender] = {
                "total": 0,
                "private": 0,
                "tagged": 0,
                "uncited": 0,
                "living": 0,
                "living_not_private": 0,
            }
        return gender_stats[gender]

    gender_stats = {}
    media, media_refs, missing_region = 0, 0, 0
    incomplete_names, alternate_names, no_families, total_living = 0, 0, 0, 0
    names_private, names_uncited = 0, 0
    association_types = {}
    association, association_refs = 0, 0
    association_private, association_uncited = 0, 0
    participant_roles = {}
    participant, participant_refs, participant_private = 0, 0, 0
    ldsord_people, ldsord_refs, ldsord_private, ldsord_uncited = 0, 0, 0, 0
    no_temple, no_status, no_date, no_place, no_family = 0, 0, 0, 0, 0
    last_changed = []

    no_birth, no_birth_date, no_birth_place = 0, 0, 0
    births_uncited, births_private = 0, 0
    no_baptism, no_baptism_date, no_baptism_place = 0, 0, 0
    baptisms_private = 0
    no_death, no_death_date, no_death_place = 0, 0, 0
    deaths_uncited, deaths_private = 0, 0
    no_burial, no_burial_date, no_burial_place = 0, 0, 0
    burials_private = 0

    db = open_readonly_database(args.get("tree_name"))
    total_people = db.get_number_of_people()

    for person in db.iter_people():
        length = len(person.media_list)
        if length > 0:
            media += 1
            media_refs += length
            for media_ref in person.media_list:
                if not media_ref.rect:
                    missing_region += 1

        if person.alternate_names:
            alternate_names += 1
        for name in [person.primary_name] + person.alternate_names:
            if name.private:
                names_private += 1
            if not name.citation_list:
                names_uncited += 1
            if name.first_name.strip() == "":
                incomplete_names += 1
            else:
                if name.get_surname_list():
                    for surname in name.get_surname_list():
                        if surname.get_surname().strip() == "":
                            incomplete_names += 1
                else:
                    incomplete_names += 1

        if not person.parent_family_list and not person.family_list:
            no_families += 1

        gender = get_gender_stats(gender_stats, person.get_gender())
        gender["total"] += 1
        if person.private:
            gender["private"] += 1
        if person.tag_list:
            gender["tagged"] += 1
        if not person.citation_list:
            gender["uncited"] += 1

        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = db.get_event_from_handle(birth_ref.ref)
            if not get_date(birth):
                no_birth_date += 1
            if not birth.place:
                no_birth_place += 1
            if not birth.citation_list:
                births_uncited += 1
            if birth.private:
                births_private += 1
        else:
            no_birth += 1

        living = False
        death_ref = person.get_death_ref()
        if death_ref:
            death = db.get_event_from_handle(death_ref.ref)
            if not get_date(death):
                no_death_date += 1
            if not death.place:
                no_death_place += 1
            if not death.citation_list:
                deaths_uncited += 1
            if death.private:
                deaths_private += 1
        else:
            if probably_alive(person, db):
                living = True
                gender["living"] += 1
                if not person.private:
                    gender["living_not_private"] += 1
            else:
                no_death += 1

        if person.person_ref_list:
            association += 1
            for person_ref in person.person_ref_list:
                association_refs += 1
                if person_ref.private:
                    association_private += 1
                if not person_ref.citation_list:
                    association_uncited += 1
                if person_ref.rel not in association_types:
                    association_types[person_ref.rel] = 0
                association_types[person_ref.rel] += 1

        has_baptism, has_burial = False, False
        if person.event_ref_list:
            participant += 1
            for event_ref in person.event_ref_list:
                participant_refs += 1
                role = event_ref.get_role().serialize()
                if role not in participant_roles:
                    participant_roles[role] = 0
                participant_roles[role] += 1
                if event_ref.private:
                    participant_private += 1

                event = db.get_event_from_handle(event_ref.ref)
                event_type = event.get_type()
                if event_type in [EventType.BAPTISM, EventType.CHRISTEN]:
                    has_baptism = True
                    if not get_date(event):
                        no_baptism_date += 1
                    if not event.place:
                        no_baptism_place += 1
                    if event.private:
                        baptisms_private += 1

                if not living:
                    if event_type in [EventType.BURIAL, EventType.CREMATION]:
                        has_burial = True
                        if not get_date(event):
                            no_burial_date += 1
                        if not event.place:
                            no_burial_place += 1
                        if event.private:
                            burials_private += 1
        if not has_baptism:
            no_baptism += 1
        if living:
            total_living += 1
        elif not has_burial:
            no_burial += 1

        if person.lds_ord_list:
            ldsord_people += 1
            for ldsord in person.lds_ord_list:
                ldsord_refs += 1
                if ldsord.private:
                    ldsord_private += 1
                if not ldsord.citation_list:
                    ldsord_uncited += 1
                if not get_date(ldsord):
                    no_date += 1
                if not ldsord.place:
                    no_place += 1
                if not ldsord.famc:
                    no_family += 1
                if not ldsord.temple:
                    no_temple += 1
                if not ldsord.status:
                    no_status += 1
        analyze_change(last_changed, person.handle, person.change, 20)
    close_readonly_database(db)

    with_birth = total_people - no_birth
    with_baptism = total_people - no_baptism
    dead_people = total_people - total_living
    with_death = dead_people - no_death
    with_burial = dead_people - no_burial

    payload = {
        "changed": {"Person": last_changed},
        "person": {
            "total": (total_people, None),
            "incomplete_names": (incomplete_names, total_people),
            "alternate_names": (alternate_names, total_people),
            "no_family_connection": (no_families, total_people),
            "no_birth": (no_birth, total_people),
            "no_birth_date": (no_birth_date, with_birth),
            "no_birth_place": (no_birth_place, with_birth),
            "no_baptism": (no_baptism, total_people),
            "no_baptism_date": (no_baptism_date, with_baptism),
            "no_baptism_place": (no_baptism_place, with_baptism),
            "no_death": (no_death, dead_people),
            "no_death_date": (no_death_date, with_death),
            "no_death_place": (no_death_place, with_death),
            "no_burial": (no_burial, dead_people),
            "no_burial_date": (no_burial_date, with_burial),
            "no_burial_place": (no_burial_place, with_burial),
        },
        "media": {
            "person": (media, total_people),
            "person_refs": (media_refs, None),
            "person_missing_region": (missing_region, media_refs),
        },
        "ldsord_person": {
            "ldsord": (ldsord_people, total_people),
            "ldsord_refs": (ldsord_refs, None),
            "no_temple": (no_temple, ldsord_refs),
            "no_status": (no_status, ldsord_refs),
            "no_date": (no_date, ldsord_refs),
            "no_place": (no_place, ldsord_refs),
            "no_family": (no_family, ldsord_refs),
        },
        "association": {
            "total": (association, total_people),
            "refs": (association_refs, None),
            "types": association_types,
        },
        "participant": {
            "total": (participant, total_people),
            "refs": (participant_refs, None),
            "person_roles": participant_roles,
        },
        "uncited": {
            "association": (association_uncited, association_refs),
            "ldsord_person": (ldsord_uncited, ldsord_refs),
            "names": (names_uncited, None),
            "preferred_births": (births_uncited, with_birth),
            "preferred_deaths": (deaths_uncited, with_death),
        },
        "privacy": {
            "names": (names_private, None),
            "baptism": (baptisms_private, with_baptism),
            "preferred_births": (births_private, with_birth),
            "preferred_deaths": (deaths_private, with_death),
            "burial": (burials_private, with_burial),
            "ldsord_person": (ldsord_private, ldsord_refs),
            "association": (association_private, association_refs),
            "participant": (participant_private, participant_refs),
        },
        "tag": {},
    }

    #                "total": 0,
    #                "private": 0,
    #                "tagged": 0,
    #                "uncited": 0,
    #                "living": 0,
    #                "living_not_private": 0,

    for gender in gender_stats:
        if gender == Person.MALE:
            prefix = "male"
        elif gender == Person.FEMALE:
            prefix = "female"
        else:
            prefix = "unknown"
        data = gender_stats[gender]

        total_gender = data["total"]
        payload["person"].update(
            {
                "%s_total" % prefix: (total_gender, total_people),
                "%s_living" % prefix: (data["living"], total_gender),
            }
        )
        payload["tag"].update({prefix: (data["tagged"], total_gender)})
        payload["uncited"].update({prefix: (data["uncited"], total_gender)})
        payload["privacy"].update(
            {
                prefix: (data["private"], total_gender),
                "%s_living_not_private"
                % prefix: (data["living_not_private"], data["living"]),
            }
        )
    return post_processing(args, "People", total_people, queue, payload)


def examine_families(args, queue=None):
    """
    Parse and analyze families.
    """
    media, media_refs = 0, 0
    missing_one, missing_both = 0, 0
    family_relations = {}
    uncited, no_events, private, tagged = 0, 0, 0, 0
    child, no_child, child_private, child_uncited = 0, 0, 0, 0
    child_mother_relations, child_father_relations = {}, {}
    ldsord_families, ldsord_refs, ldsord_private, ldsord_uncited = 0, 0, 0, 0
    no_temple, no_status, no_date, no_place = 0, 0, 0, 0
    participant_roles = {}
    participant_private = 0
    last_changed = []

    db = open_readonly_database(args.get("tree_name"))
    total_families = db.get_number_of_families()
    total_surnames = len(set(db.surname_list))

    for family in db.iter_families():
        length = len(family.media_list)
        if length > 0:
            media += 1
            media_refs += length

        if not family.father_handle and not family.mother_handle:
            missing_both += 1
        elif not family.father_handle or not family.mother_handle:
            missing_one += 1

        family_type = family.type.serialize()
        if family_type not in family_relations:
            family_relations[family_type] = 0
        family_relations[family_type] += 1

        if not family.citation_list:
            uncited += 1
        if family.private:
            private += 1
        if family.tag_list:
            tagged += 1

        if not family.event_ref_list:
            no_events += 1
        else:
            for event_ref in family.event_ref_list:
                role = event_ref.get_role().serialize()
                if role not in participant_roles:
                    participant_roles[role] = 0
                participant_roles[role] += 1
                if event_ref.private:
                    participant_private += 1

        if not family.child_ref_list:
            no_child += 1
        else:
            for child_ref in family.child_ref_list:
                child += 1
                if child_ref.private:
                    child_private += 1
                if not child_ref.citation_list:
                    child_uncited += 1
                mother_relation = child_ref.mrel.serialize()
                if mother_relation not in child_mother_relations:
                    child_mother_relations[mother_relation] = 0
                child_mother_relations[mother_relation] += 1
                father_relation = child_ref.frel.serialize()
                if father_relation not in child_father_relations:
                    child_father_relations[father_relation] = 0
                child_father_relations[father_relation] += 1

        if family.lds_ord_list:
            ldsord_families += 1
            for ldsord in family.lds_ord_list:
                ldsord_refs += 1
                if ldsord.private:
                    ldsord_private += 1
                if not ldsord.citation_list:
                    ldsord_uncited += 1
                if not get_date(ldsord):
                    no_date += 1
                if not ldsord.place:
                    no_place += 1
                if not ldsord.temple:
                    no_temple += 1
                if not ldsord.status:
                    no_status += 1
        analyze_change(last_changed, family.handle, family.change, 20)
    close_readonly_database(db)

    payload = {
        "changed": {"Family": last_changed},
        "family": {
            "total": (total_families, None),
            "surname_total": (total_surnames, None),
            "missing_one": (missing_one, total_families),
            "missing_both": (missing_both, total_families),
            "no_child": (no_child, total_families),
            "no_events": (no_events, total_families),
            "relations": family_relations,
        },
        "ldsord_family": {
            "ldsord": (ldsord_families, total_families),
            "ldsord_refs": (ldsord_refs, None),
            "no_temple": (no_temple, ldsord_refs),
            "no_status": (no_status, ldsord_refs),
            "no_date": (no_date, ldsord_refs),
            "no_place": (no_place, ldsord_refs),
        },
        "uncited": {
            "family": (uncited, total_families),
            "child": (child_uncited, child),
            "ldsord_family": (ldsord_uncited, ldsord_refs),
        },
        "privacy": {
            "family": (private, total_families),
            "child": (child_private, child),
            "family_participant": (participant_private, None),
            "ldsord_family": (ldsord_private, ldsord_refs),
        },
        "tag": {
            "family": (tagged, total_families),
        },
        "children": {
            "refs": (child, None),
            "mother_relations": child_mother_relations,
            "father_relations": child_father_relations,
        },
        "participant": {
            "family_roles": participant_roles,
        },
        "media": {
            "family": (media, total_families),
            "family_refs": (media_refs, None),
        },
    }
    return post_processing(args, "Families", total_families, queue, payload)


def examine_events(args, queue=None):
    """
    Parse and analyze events.
    """
    media, media_refs = 0, 0
    no_date, no_place, no_description = 0, 0, 0
    uncited, private, tagged, marriages = 0, 0, 0, 0
    event_types = {}
    uncited_events = {}
    last_changed = []
    no_marriage_date, no_marriage_place, marriage_private = 0, 0, 0

    db = open_readonly_database(args.get("tree_name"))
    total_events = db.get_number_of_events()

    for event in db.iter_events():
        length = len(event.media_list)
        if length > 0:
            media += 1
            media_refs += length

        if not event.citation_list:
            uncited += 1
        if not event.place:
            no_place += 1
        if not get_date(event):
            no_date += 1
        if not event.get_description():
            no_description += 1
        if event.private:
            private += 1
        if event.tag_list:
            tagged += 1

        event_type = event.get_type()
        if event_type == EventType.MARRIAGE:
            marriages += 1
            if not event.place:
                no_marriage_place += 1
            if not get_date(event):
                no_marriage_date += 1
            if event.private:
                marriage_private += 1

        event_key = event_type.serialize()
        if event_key not in event_types:
            event_types[event_key] = 0
            uncited_events[event_key] = 0
        event_types[event_key] += 1
        if not event.citation_list:
            uncited_events[event_key] += 1
        analyze_change(last_changed, event.handle, event.change, 20)
    close_readonly_database(db)

    payload = {
        "changed": {"Event": last_changed},
        "event": {
            "total": (total_events, None),
            "no_place": (no_place, total_events),
            "no_date": (no_date, total_events),
            "no_description": (no_description, total_events),
            "types": event_types,
        },
        "family": {
            "no_marriage_date": (no_marriage_date, marriages),
            "no_marriage_place": (no_marriage_place, marriages),
        },
        "uncited": {
            "event": (uncited, total_events),
            "events": uncited_events,
        },
        "privacy": {
            "event": (private, total_events),
            "marriage": (marriage_private, marriages),
        },
        "tag": {
            "event": (tagged, total_events),
        },
        "media": {
            "event": (media, total_events),
            "event_refs": (media_refs, None),
        },
    }
    return post_processing(args, "Events", total_events, queue, payload)


def examine_places(args, queue=None):
    """
    Parse and analyze places.
    """
    media, media_refs = 0, 0
    no_name, no_latitude, no_longitude, no_code = 0, 0, 0, 0
    uncited, private, tagged = 0, 0, 0
    place_types = {}
    last_changed = []

    db = open_readonly_database(args.get("tree_name"))
    total_places = db.get_number_of_places()

    for place in db.iter_places():
        length = len(place.media_list)
        if length > 0:
            media += 1
            media_refs += length

        place_type = place.get_type().serialize()
        if place_type not in place_types:
            place_types[place_type] = 0
        place_types[place_type] += 1

        if not place.name:
            no_name += 1
        if not place.lat:
            no_latitude += 1
        if not place.long:
            no_longitude += 1
        if not place.code:
            no_code += 1
        if not place.citation_list:
            uncited += 1
        if place.private:
            private += 1
        if place.tag_list:
            tagged += 1
        analyze_change(last_changed, place.handle, place.change, 20)
    close_readonly_database(db)

    payload = {
        "changed": {"Place": last_changed},
        "place": {
            "total": (total_places, None),
            "no_name": (no_name, total_places),
            "no_latitude": (no_latitude, total_places),
            "no_longitude": (no_longitude, total_places),
            "no_code": (no_code, total_places),
            "types": place_types,
        },
        "uncited": {
            "place": (uncited, total_places),
        },
        "privacy": {
            "place": (private, total_places),
        },
        "tag": {
            "place": (tagged, total_places),
        },
        "media": {
            "place": (media, total_places),
            "place_refs": (media_refs, None),
        },
    }
    return post_processing(args, "Places", total_places, queue, payload)


def examine_media(args, queue=None):
    """
    Parse and analyze media objects.
    """
    no_desc, no_date, no_path, no_mime = 0, 0, 0, 0
    uncited, private, tagged, size_bytes = 0, 0, 0, 0
    not_found = []
    last_changed = []

    db = open_readonly_database(args.get("tree_name"))
    total_media = db.get_number_of_media()

    for media in db.iter_media():
        if not media.desc:
            no_desc += 1
        if not get_date(media):
            no_date += 1
        if not media.mime:
            no_mime += 1
        if media.private:
            private += 1
        if media.tag_list:
            tagged += 1
        if not media.path:
            no_path += 1
        else:
            fullname = media_path_full(db, media.path)
            try:
                size_bytes += os.path.getsize(fullname)
            except OSError:
                if media.path not in not_found:
                    not_found.append(media.path)
        analyze_change(last_changed, media.handle, media.change, 20)

    if not int(size_bytes / 1024):
        size_string = "%s bytes" % size_bytes
    elif size_bytes < 1048576:
        size_string = "%s KB" % int(size_bytes / 1024)
    else:
        size_string = "%s MB" % int(size_bytes / 1048576)

    payload = {
        "changed": {"Media": last_changed},
        "media": {
            "total": (total_media, None),
            "size": (size_string, None),
            "no_path": (no_path, total_media),
            "no_file": (len(not_found), total_media - no_path),
            "not_found": not_found,
            "no_description": (no_desc, total_media),
            "no_date": (no_date, total_media),
            "no_mime": (no_mime, total_media),
        },
        "uncited": {
            "media": (uncited, total_media),
        },
        "privacy": {
            "media": (private, total_media),
        },
        "tag": {
            "media": (tagged, total_media),
        },
    }
    return post_processing(args, "Media", total_media, queue, payload)


def examine_sources(args, queue=None):
    """
    Parse and analyze sources.
    """
    media, media_refs = 0, 0
    no_title, no_author, no_pubinfo, no_abbrev = 0, 0, 0, 0
    no_repository, repos_refs, no_call_number, private, tagged = 0, 0, 0, 0, 0
    media_types = {}
    last_changed = []

    db = open_readonly_database(args.get("tree_name"))
    total_sources = db.get_number_of_sources()

    for source in db.iter_sources():
        length = len(source.media_list)
        if length > 0:
            media += 1
            media_refs += length

        if not source.title:
            no_title += 1
        if not source.author:
            no_author += 1
        if not source.pubinfo:
            no_pubinfo += 1
        if not source.abbrev:
            no_abbrev += 1
        if not source.reporef_list:
            no_repository += 1
        else:
            repos_refs += len(source.reporef_list)
            for repo_ref in source.reporef_list:
                if not repo_ref.call_number:
                    no_call_number += 1
                media_type = repo_ref.media_type.serialize()
                if media_type not in media_types:
                    media_types[media_type] = 0
                media_types[media_type] += 1
        if source.private:
            private += 1
        if source.tag_list:
            tagged += 1
        analyze_change(last_changed, source.handle, source.change, 20)
    close_readonly_database(db)

    payload = {
        "changed": {"Source": last_changed},
        "source": {
            "total": (total_sources, None),
            "no_title": (no_title, total_sources),
            "no_author": (no_author, total_sources),
            "no_pubinfo": (no_pubinfo, total_sources),
            "no_abbrev": (no_abbrev, total_sources),
            "no_repository": (no_repository, total_sources),
            "repository_refs": (repos_refs, None),
            "no_call_number": (no_call_number, repos_refs),
            "types": media_types,
        },
        "privacy": {
            "source": (private, total_sources),
        },
        "tag": {
            "source": (tagged, total_sources),
        },
        "media": {
            "source": (media, total_sources),
            "source_refs": (media_refs, None),
        },
    }
    return post_processing(args, "Sources", total_sources, queue, payload)


def examine_citations(args, queue=None):
    """
    Parse and analyze citation objects.
    """
    media, media_refs = 0, 0
    no_source, no_page, no_date, private, tagged = 0, 0, 0, 0, 0
    very_low, low, normal, high, very_high = 0, 0, 0, 0, 0
    last_changed = []

    db = open_readonly_database(args.get("tree_name"))
    total_citations = db.get_number_of_citations()

    for citation in db.iter_citations():
        length = len(citation.media_list)
        if length > 0:
            media += 1
            media_refs += length

        if not get_date(citation):
            no_date += 1
        if not citation.source_handle:
            no_source += 1
        if not citation.page:
            no_page += 1
        if citation.private:
            private += 1
        if citation.tag_list:
            tagged += 1
        if citation.confidence == Citation.CONF_VERY_LOW:
            very_low += 1
        elif citation.confidence == Citation.CONF_LOW:
            low += 1
        elif citation.confidence == Citation.CONF_NORMAL:
            normal += 1
        elif citation.confidence == Citation.CONF_HIGH:
            high += 1
        elif citation.confidence == Citation.CONF_VERY_HIGH:
            very_high += 1
        analyze_change(last_changed, citation.handle, citation.change, 20)
    close_readonly_database(db)

    payload = {
        "changed": {"Citation": last_changed},
        "citation": {
            "total": (total_citations, None),
            "no_source": (no_source, total_citations),
            "no_date": (no_date, total_citations),
            "no_page": (no_page, total_citations),
            "confidence": {
                "very_low": (very_low, total_citations),
                "low": (low, total_citations),
                "normal": (normal, total_citations),
                "high": (high, total_citations),
                "very_high": (very_high, total_citations),
            },
        },
        "privacy": {
            "citation": (private, total_citations),
        },
        "tag": {
            "citation": (tagged, total_citations),
        },
        "media": {
            "citation": (media, total_citations),
            "citation_refs": (media_refs, None),
        },
    }
    return post_processing(args, "Citations", total_citations, queue, payload)


def examine_repositories(args, queue=None):
    """
    Parse and analyze repositories.
    """
    no_name, no_address, private, tagged = 0, 0, 0, 0
    repository_types = {}
    last_changed = []

    db = open_readonly_database(args.get("tree_name"))
    total_repositories = db.get_number_of_repositories()

    for repository in db.iter_repositories():
        repository_type = repository.get_type().serialize()
        if repository_type not in repository_types:
            repository_types[repository_type] = 0
        repository_types[repository_type] += 1

        if not repository.name:
            no_name += 1
        if not repository.address_list:
            no_address += 1
        if repository.private:
            private += 1
        if repository.tag_list:
            tagged += 1
        analyze_change(last_changed, repository.handle, repository.change, 20)
    close_readonly_database(db)

    payload = {
        "changed": {"Repository": last_changed},
        "repository": {
            "total": (total_repositories, None),
            "no_name": (no_name, total_repositories),
            "no_address": (no_address, total_repositories),
            "types": repository_types,
        },
        "privacy": {
            "repository": (private, total_repositories),
        },
        "tag": {
            "repository": (tagged, total_repositories),
        },
    }
    return post_processing(
        args, "Repositories", total_repositories, queue, payload
    )


def examine_notes(args, queue=None):
    """
    Parse and analyze notes.
    """
    no_text, private, tagged = 0, 0, 0
    note_types = {}
    last_changed = []

    db = open_readonly_database(args.get("tree_name"))
    total_notes = db.get_number_of_notes()

    for note in db.iter_notes():
        note_type = note.get_type().serialize()
        if note_type not in note_types:
            note_types[note_type] = 0
        note_types[note_type] += 1

        if not note.text:
            no_text += 1
        if note.private:
            private += 1
        if note.tag_list:
            tagged += 1
        analyze_change(last_changed, note.handle, note.change, 20)
    close_readonly_database(db)

    payload = {
        "changed": {"Note": last_changed},
        "note": {
            "total": (total_notes, None),
            "no_text": (no_text, total_notes),
            "types": note_types,
        },
        "privacy": {
            "note": (private, total_notes),
        },
        "tag": {
            "note": (tagged, total_notes),
        },
    }
    return post_processing(args, "Notes", total_notes, queue, payload)


def examine_tags(args, queue=None):
    """
    Parse and analyze tags.
    """
    last_changed = []

    db = open_readonly_database(args.get("tree_name"))
    total_tags = db.get_number_of_tags()

    for tag in db.iter_tags():
        analyze_change(last_changed, tag.handle, tag.change, 20)
    close_readonly_database(db)

    payload = {
        "changed": {"Tag": last_changed},
        "tag": {"total": (total_tags, None)},
    }
    return post_processing(args, "Tags", total_tags, queue, payload)


def examine_bookmarks(args):
    """
    Parse and analyze bookmarks.
    """
    db = open_readonly_database(args.get("tree_name"))
    person_bookmarks = len(db.get_bookmarks().bookmarks)
    family_bookmarks = len(db.get_family_bookmarks().bookmarks)
    event_bookmarks = len(db.get_event_bookmarks().bookmarks)
    place_bookmarks = len(db.get_place_bookmarks().bookmarks)
    media_bookmarks = len(db.get_media_bookmarks().bookmarks)
    source_bookmarks = len(db.get_source_bookmarks().bookmarks)
    citation_bookmarks = len(db.get_citation_bookmarks().bookmarks)
    repository_bookmarks = len(db.get_repo_bookmarks().bookmarks)
    note_bookmarks = len(db.get_note_bookmarks().bookmarks)
    total_bookmarks = (
        person_bookmarks
        + family_bookmarks
        + event_bookmarks
        + place_bookmarks
        + media_bookmarks
        + source_bookmarks
        + citation_bookmarks
        + repository_bookmarks
        + note_bookmarks
    )
    payload = {
        "bookmark": {
            "total": (total_bookmarks, None),
            "person": (person_bookmarks, total_bookmarks),
            "family": (family_bookmarks, total_bookmarks),
            "event": (event_bookmarks, total_bookmarks),
            "place": (place_bookmarks, total_bookmarks),
            "media": (media_bookmarks, total_bookmarks),
            "source": (source_bookmarks, total_bookmarks),
            "citation": (citation_bookmarks, total_bookmarks),
            "repository": (repository_bookmarks, total_bookmarks),
            "note": (note_bookmarks, total_bookmarks),
        }
    }
    close_readonly_database(db)
    return post_processing(args, "Bookmarks", total_bookmarks, None, payload)


def analyze_change(obj_list, obj_handle, change, max_length):
    """
    Analyze a change for inclusion in a last modified list.
    """
    bsindex = bisect(KeyWrapper(obj_list, key=lambda c: c[1]), change)
    obj_list.insert(bsindex, (obj_handle, change))
    if len(obj_list) > max_length:
        obj_list.pop(max_length)


# ------------------------------------------------------------------------
#
# KeyWrapper class
#
# ------------------------------------------------------------------------
class KeyWrapper:
    """
    For bisect to operate on an element of a tuple in the list.
    """

    __slots__ = "iter", "key"

    def __init__(self, iterable, key):
        self.iter = iterable
        self.key = key

    def __getitem__(self, i):
        return self.key(self.iter[i])

    def __len__(self):
        return len(self.iter)


def open_readonly_database(dbname):
    """
    Open database for read only access.
    """
    data = lookup_family_tree(dbname)
    dbpath, dummy_locked, dummy_locked_by, backend = data
    database = make_database(backend)
    database.load(dbpath, mode=DBMODE_R, update=False)
    return database


def close_readonly_database(db):
    """
    Close database making sure lock persists for core application as
    existing code will delete it when closing a read only instance.
    """
    save_dir = db.get_save_path()
    if not os.path.isfile(os.path.join(save_dir, DBLOCKFN)):
        save_dir = None
    db.close(update=False)
    if save_dir:
        write_lock_file(save_dir)


def post_processing(args, obj_type, total, queue, payload):
    """
    Handle collection post processing.
    """
    if args.get("time"):
        print(
            "{0:<12} {1:6} {2}".format(
                obj_type, total, time.time() - args.get("start_time")
            ),
            file=sys.stderr,
        )
    if queue:
        queue.put(payload)
    else:
        return payload


def get_object_list(dbname):
    """
    Prepare object list based on descending number of objects.
    """
    db = open_readonly_database(dbname)
    object_list = [
        ("Person", db.get_number_of_people()),
        ("Family", db.get_number_of_families()),
        ("Event", db.get_number_of_events()),
        ("Place", db.get_number_of_places()),
        ("Media", db.get_number_of_media()),
        ("Source", db.get_number_of_sources()),
        ("Citation", db.get_number_of_citations()),
        ("Repository", db.get_number_of_repositories()),
        ("Note", db.get_number_of_notes()),
        ("Tag", db.get_number_of_tags()),
    ]
    close_readonly_database(db)
    object_list.sort(key=lambda x: x[1], reverse=True)
    total = sum([y for (x, y) in object_list])
    return total, [x for (x, y) in object_list]


def fold(one, two):
    """
    Fold a set of dictionary entries into another.
    """
    for key in two.keys():
        if key not in one:
            one.update({key: two[key]})
        else:
            for subkey in two[key]:
                if subkey not in one[key]:
                    one[key].update({subkey: two[key][subkey]})


TASK_HANDLERS = {
    "Person": examine_people,
    "Family": examine_families,
    "Event": examine_events,
    "Place": examine_places,
    "Media": examine_media,
    "Source": examine_sources,
    "Citation": examine_citations,
    "Repository": examine_repositories,
    "Note": examine_notes,
    "Tag": examine_tags,
}


def gather_serial_statistics(args, obj_list):
    """
    Gather statistics using non-concurrent serial mode.
    """
    facts = examine_bookmarks(args)
    for obj_type in obj_list:
        results = TASK_HANDLERS[obj_type](args)
        fold(facts, results)
    return facts


def gather_concurrent_statistics(args, obj_list):
    """
    Gather statistics using multiprocessing mode.
    """
    workers = {}
    queues = {}
    for obj_type in obj_list:
        queues[obj_type] = Queue()
        workers[obj_type] = Process(
            target=TASK_HANDLERS[obj_type], args=(args, queues[obj_type])
        )
        workers[obj_type].start()

    facts = examine_bookmarks(args)
    obj_list.reverse()
    for obj_type in obj_list:
        result_set = queues[obj_type].get()
        workers[obj_type].join()
        fold(facts, result_set)
    return facts


def gather_statistics(args):
    """
    Gather tree statistics.
    """
    try:
        total, obj_list = get_object_list(args.get("tree_name"))
    except TypeError:
        print(
            "Error: Problem finding and loading tree: %s"
            % args.get("tree_name"),
            file=sys.stderr,
        )
        sys.exit(1)

    if args.get("serial"):
        facts = gather_serial_statistics(args, obj_list)
    else:
        facts = gather_concurrent_statistics(args, obj_list)
    return total, facts


def main():
    """
    Main program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tree",
        dest="tree_name",
        required=True,
        help="Tree name",
    )
    parser.add_argument(
        "-T",
        "--time",
        dest="time",
        default=False,
        action="store_true",
        help="Dump run times",
    )
    parser.add_argument(
        "-s",
        "--serial",
        dest="serial",
        default=False,
        action="store_true",
        help="Serial mode",
    )
    parser.add_argument(
        "-y",
        "--yaml",
        dest="yaml",
        default=False,
        action="store_true",
        help="Dump statistics in YAML format if YAML support available",
    )
    parsed_args = parser.parse_args()

    args = {
        "tree_name": parsed_args.tree_name,
        "time": parsed_args.time,
        "serial": parsed_args.serial,
    }
    if parsed_args.time:
        args["start_time"] = time.time()
        print("Run started", file=sys.stderr)

    total, facts = gather_statistics(args)

    if parsed_args.yaml:
        try:
            import yaml

            print(yaml.dump(facts))
        except ModuleNotFoundError:
            print("YAML support not available", file=sys.stderr)
    else:
        # https://stackoverflow.com/questions/38029058/sending-pickled-data-to-a-server
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="latin-1")
        print(pickle.dumps(facts).decode("latin-1"), end="", flush=True)
    if parsed_args.time:
        print(
            "{0:<12} {1:6} {2}".format(
                "Run complete", total, time.time() - args.start_time
            ),
            file=sys.stderr,
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
