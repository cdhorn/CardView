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


def get_key_family_events(db, family):
    """
    Get the two key events in the formation and dissolution of a family.
    """
    marriage = None
    divorce = None
    for ref in family.get_event_ref_list():
        event = db.get_event_from_handle(ref.ref)
        if event:
            if event.type == EventType.MARRIAGE:
                marriage = event
            elif event.type == EventType.DIVORCE:
                divorce = event
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
    father_death_ref = father.get_death_ref()
    if father_death_ref:
        father_death = db.get_event_from_handle(father_death_ref.ref)
    else:
        father_death = None

    mother = db.get_person_from_handle(family.get_mother_handle())
    mother_death_ref = mother.get_death_ref()
    if mother_death_ref:
        mother_death = db.get_event_from_handle(mother_death_ref.ref)
    else:
        mother_death = None

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
