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
Common utility functions related to people, families and events
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.lib import EventType, Person, Span
from gramps.gen.lib.date import Today
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.db import family_name

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------

_ = glocale.translation.sgettext


def get_span(date1, date2, strip=True):
    """
    Return span.
    """
    span = Span(date1, date2)
    if span.is_valid():
        precision = global_config.get("preferences.age-display-precision")
        age = str(span.format(precision=precision))
        if age and age != "unknown":
            if strip:
                return age.strip("()")
            return age
    return ""


def get_age(base_event, current_event, today=None, strip=False):
    """
    Return age text if applicable.
    """
    if base_event and base_event.date:
        if current_event and current_event.date or today:
            if today:
                current = today
            else:
                current = current_event.date
            return get_span(base_event.date, current, strip=strip)
    return ""


def format_date_string(event1, event2):
    """
    Format a simple one line date string.
    """
    text = ""
    if event1:
        text = glocale.date_displayer.display(event1.date)
    text = "".join((text, " - "))
    if event2:
        text = "".join((text, glocale.date_displayer.display(event2.date)))
    text.strip()
    if text == "-":
        return ""
    return text


def get_relation(db, person, relation, depth=15):
    """
    Calculate relationship between two people.
    """
    if isinstance(relation, Person):
        base_person = relation
    else:
        base_person = db.get_person_from_handle(relation)
    base_person_name = base_person.primary_name.get_regular_name().strip()

    calc = get_relationship_calculator(reinit=True, clocale=glocale)
    calc.set_depth(depth)
    result = calc.get_one_relationship(
        db, base_person, person, extra_info=True
    )
    if result[0]:
        return " ".join((result[0].capitalize(), _("of"), base_person_name))
    return None


def get_key_person_events(
    db, person, show_baptism=False, show_burial=False, birth_only=False
):
    """
    Get some of the key events in the life of a person. If no birth or death
    we use fallbacks unless we know those are specifically requested.
    """
    birth = None
    baptism = None
    christening = None
    death = None
    burial = None
    cremation = None
    will = None
    probate = None
    religion = []
    occupation = []
    for ref in person.get_primary_event_ref_list():
        event = db.get_event_from_handle(ref.ref)
        if event:
            if event.type == EventType.BIRTH:
                birth = event
                if birth_only:
                    break
                continue
            if event.type == EventType.BAPTISM:
                baptism = event
                if birth_only:
                    break
                continue
            if event.type == EventType.CHRISTEN:
                christening = event
                if birth_only:
                    break
                continue
            if event.type == EventType.DEATH:
                death = event
                continue
            if event.type == EventType.BURIAL:
                burial = event
                continue
            if event.type == EventType.CREMATION:
                cremation = event
                continue
            if event.type == EventType.PROBATE:
                probate = event
                continue
            if event.type == EventType.WILL:
                will = event
                continue
            if event.type == EventType.RELIGION:
                religion.append(event)
                continue
            if event.type == EventType.OCCUPATION:
                occupation.append(event)
                continue

    if baptism is None:
        baptism = christening
    if birth is None and not show_baptism:
        birth = baptism

    if burial is None:
        burial = cremation
    if death is None and not show_burial:
        death = burial
    if death is None and burial is None:
        death = probate
        if death is None:
            death = will

    return {
        "birth": birth,
        "baptism": baptism,
        "death": death,
        "burial": burial,
        "religion": religion,
        "occupation": occupation,
    }


def get_key_family_events(db, family):
    """
    Get the two key events in the formation and dissolution of a
    family. Consider all the alternates and rank them.
    """
    marriage = None
    marriage_settlement = None
    marriage_license = None
    marriage_contract = None
    marriage_banns = None
    marriage_alternate = None
    engagement = None
    divorce = None
    annulment = None
    divorce_filing = None
    for ref in family.get_event_ref_list():
        event = db.get_event_from_handle(ref.ref)
        if event:
            if event.type == EventType.MARRIAGE:
                if marriage is None:
                    marriage = event
            if event.type == EventType.MARR_SETTL:
                marriage_settlement = event
            if event.type == EventType.MARR_LIC:
                marriage_license = event
            if event.type == EventType.MARR_CONTR:
                marriage_contract = event
            if event.type == EventType.MARR_BANNS:
                marriage_banns = event
            if event.type == EventType.MARR_ALT:
                marriage_alternate = event
            if event.type == EventType.ENGAGEMENT:
                engagement = event
            if event.type == EventType.DIVORCE:
                if divorce is None:
                    divorce = event
            if event.type == EventType.ANNULMENT:
                annulment = event
            if event.type == EventType.DIV_FILING:
                divorce_filing = event

    if marriage is None:
        if marriage_alternate:
            marriage = marriage_alternate
        elif marriage_contract:
            marriage = marriage_contract
        elif marriage_settlement:
            marriage = marriage_settlement
        elif marriage_license:
            marriage = marriage_license
        elif marriage_banns:
            marriage = marriage_banns
        elif engagement:
            marriage = engagement

    if divorce is None:
        if annulment:
            divorce = annulment
        elif divorce_filing:
            divorce = divorce_filing

    return marriage, divorce


def get_participants(db, event):
    """
    Get all of the participants related to an event.
    Returns people and also a descriptive string.
    """
    participants = []
    event_handle = event.get_handle()
    result_list = list(
        db.find_backlink_handles(
            event_handle, include_classes=["Person", "Family"]
        )
    )
    people = [x[1] for x in result_list if x[0] in ["Person"]]
    for handle in people:
        person = db.get_person_from_handle(handle)
        if not person:
            continue
        for event_ref in person.get_event_ref_list():
            if event_handle in [event_ref.ref]:
                participants.append(
                    (
                        "Person",
                        person,
                        event_ref,
                        name_displayer.display(person),
                    )
                )
                break
    families = [x[1] for x in result_list if x[0] in ["Family"]]
    for handle in families:
        family = db.get_family_from_handle(handle)
        if not family:
            continue
        for event_ref in family.get_event_ref_list():
            if event_handle in [event_ref.ref]:
                participants.append(
                    ("Family", family, event_ref, family_name(family, db))
                )
                break
    return participants


def get_primary_participant(participants):
    """
    Return first primary participant found, or first if none found
    """
    for participant in participants:
        (obj_type, dummy_obj, obj_event_ref, dummy_obj_name) = participant
        role = obj_event_ref.get_role()
        if obj_type in ["Person"] and role.is_primary():
            return participant
        if obj_type in ["Family"] and role.is_family():
            return participant
    return participants[0]


def get_participants_text(participants, primary=None):
    """
    Return textual string of participant names.
    """
    if not primary:
        primary_participant = get_primary_participant(participants)
    else:
        primary_participant = primary
    (
        dummy_primary_type,
        primary_obj,
        dummy_primary_obj_event_ref,
        text,
    ) = primary_participant

    primary_obj_handle = primary_obj.get_handle()
    for participant in participants:
        (dummy_obj_type, obj, dummy_obj_event_ref, obj_name) = participant
        if obj.get_handle() == primary_obj_handle:
            continue
        text = "; ".join((text, obj_name))
    return text


def get_event_category(db, event):
    """
    Return the category for grouping an event.
    """
    event_type = event.get_type()
    for entry in event_type.get_menu_standard_xml():
        event_key = entry[0].lower().replace("life events", "vital")
        for event_id in entry[1]:
            if event_type == event_id:
                return event_key
    custom_event_types = db.get_event_types()
    for event_name in custom_event_types:
        if event_type.xml_str() == event_name:
            return "custom"
    return "other"


def get_marriage_duration(db, family_obj_or_handle):
    """
    Evaluate and return text string describing length of marriage.
    """
    if isinstance(family_obj_or_handle, str):
        family = db.get_family_from_handle(family_obj_or_handle)
    else:
        family = family_obj_or_handle

    if not family.get_father_handle():
        return ""
    if not family.get_mother_handle():
        return ""

    marriage, divorce = get_key_family_events(db, family)
    if marriage and divorce:
        return get_age(marriage, divorce, strip=True)

    father = db.get_person_from_handle(family.get_father_handle())
    father_events = get_key_person_events(db, father)
    father_death = father_events["death"]

    mother = db.get_person_from_handle(family.get_mother_handle())
    mother_events = get_key_person_events(db, mother)
    mother_death = mother_events["death"]

    father_sortval = None
    if father_death and father_death.get_date_object():
        father_sortval = father_death.get_date_object().sortval
    mother_sortval = None
    if mother_death and mother_death.get_date_object():
        mother_sortval = mother_death.get_date_object().sortval

    if father_sortval and mother_sortval:
        if father_sortval and mother_sortval:
            if father_sortval < mother_sortval:
                return get_age(marriage, father_death, strip=True)
            return get_age(marriage, mother_death, strip=True)
    elif father_sortval:
        return get_age(marriage, father_death, strip=True)
    elif mother_sortval:
        return get_age(marriage, mother_death, strip=True)

    if probably_alive(father, db) and probably_alive(mother, db):
        today = Today()
        return get_age(marriage, None, today=today, strip=True)
    return ""


def check_multiple_events(db, obj, event_type):
    """
    Check if an object has multiple events of a given type.
    """
    count = 0
    for event_ref in obj.get_event_ref_list():
        event = db.get_event_from_handle(event_ref.ref)
        if event.get_type() == event_type:
            count = count + 1
    return count > 1
