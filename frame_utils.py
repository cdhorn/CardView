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
Frame utility functions and classes.
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import (
    Citation,
    Event,
    EventType,
    Family,
    Note,
    Person,
    Place,
    Repository,
    Source,
)
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.relationship import get_relationship_calculator
from gramps.gui.ddtargets import DdTargets


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from timeline import EVENT_CATEGORIES, RELATIVES

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

_GENDERS = {
    Person.MALE: "\u2642",
    Person.FEMALE: "\u2640",
    Person.UNKNOWN: "\u2650",
}

_CONFIDENCE = {
    Citation.CONF_VERY_LOW: _("Very Low"),
    Citation.CONF_LOW: _("Low"),
    Citation.CONF_NORMAL: _("Normal"),
    Citation.CONF_HIGH: _("High"),
    Citation.CONF_VERY_HIGH: _("Very High"),
}

EVENT_FORMATS = {
    0: _("Show life span only and nothing else"),
    1: _("Single line with place"),
    2: _("Single line with no place"),
    3: _("Abbreviated single line with place"),
    4: _("Abbreviated single line with no place"),
    5: _("Split line"),
    6: _("Abbreviated split line"),
}

COLOR_SCHEMES = {
    0: _("Person scheme"),
    1: _("Relationship scheme"),
    2: _("Event category scheme"),
    3: _("Evidence confidence scheme")
}

CONFIDENCE_COLOR_SCHEME = {
    Citation.CONF_VERY_LOW: "very-low",
    Citation.CONF_LOW: "low",
    Citation.CONF_NORMAL: "normal",
    Citation.CONF_HIGH: "high",
    Citation.CONF_VERY_HIGH: "very-high",
}

TAG_MODES = {
    0: _("Disabled"),
    1: _("Show icons"),
    2: _("Show tag names")
}


def get_gramps_object_type(obj):
    """
    Return information for a primary Gramps object.
    """
    if isinstance(obj, Person):
        return "Person", DdTargets.PERSON_LINK, 'gramps-person'
    elif isinstance(obj, Family):
        return "Family", DdTargets.FAMILY_LINK, 'gramps-family'
    elif isinstance(obj, Event):
        return "Event", DdTargets.EVENT, 'gramps-event'
    elif isinstance(obj, Place):
        return "Place", DdTargets.PLACE_LINK, 'gramps-place'
    elif isinstance(obj, Source):
        return "Source", DdTargets.SOURCE_LINK, 'gramps-source'
    elif isinstance(obj, Citation):
        return "Citation", DdTargets.CITATION_LINK, 'gramps-citation'
    elif isinstance(obj, Repository):
        return "Repository", DdTargets.REPO_LINK, 'gramps-repository'
    elif isinstance(obj, Note):
        return "Note", DdTargets.NOTE_LINK, 'gramps-notes'
    
def format_date_string(event1, event2):
    """
    Format a simple one line date string.
    """
    text = ""
    if event1:
        text = glocale.date_displayer.display(event1.date)
    text = "{} - ".format(text)
    if event2:
        text = "{}{}".format(text, glocale.date_displayer.display(event2.date))
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
    result = calc.get_one_relationship(db, base_person, person, extra_info=True)
    if result[0]:
        return "{} {} {}".format(result[0].capitalize(), _("of"), base_person_name)
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


def get_confidence(level):
    """
    Return textual string for the confidence level.
    """
    return _CONFIDENCE[level]


class TextLink(Gtk.EventBox):
    """
    A simple class for treating a label as a hyperlink.
    """

    def __init__(
        self, name, handle=None, callback=None, action=None, tooltip=None, hexpand=False
    ):
        Gtk.EventBox.__init__(self)
        self.label = Gtk.Label(hexpand=hexpand, halign=Gtk.Align.START, wrap=True)
        self.label.set_markup(name.replace('&', '&amp;'))
        self.add(self.label)
        self.name = name
        if callback:
            self.connect("button-press-event", callback, handle, action)
            self.connect("enter-notify-event", self.enter)
            self.connect("leave-notify-event", self.leave)
        if tooltip:
            self.set_tooltip_text(tooltip)

    def enter(self, obj, event):
        self.label.set_markup("<u>{}</u>".format(self.name.replace('&', '&amp;')))

    def leave(self, obj, event):
        self.label.set_markup(self.name.replace('&', '&amp;'))


class EventFormatSelector(Gtk.ComboBoxText):
    """
    An event format selector for the configdialog.
    """

    def __init__(self, option, config):
        Gtk.ComboBoxText.__init__(self)
        self.option = option
        self.config = config
        for key in EVENT_FORMATS:
            self.append_text(EVENT_FORMATS[key])
        current = self.config.get(self.option)
        self.set_active(current)
        self.connect("changed", self.update)

    def update(self, obj):
        current = self.get_active()
        self.config.set(self.option, current)


class TagModeSelector(Gtk.ComboBoxText):
    """
    A tag display mode selector for the configdialog.
    """

    def __init__(self, option, config):
        Gtk.ComboBoxText.__init__(self)
        self.option = option
        self.config = config
        for key in TAG_MODES:
            self.append_text(TAG_MODES[key])
        current = self.config.get(self.option)
        self.set_active(current)
        self.connect("changed", self.update)

    def update(self, obj):
        current = self.get_active()
        self.config.set(self.option, current)


class ColorSchemeSelector(Gtk.ComboBoxText):
    """
    A color scheme selector for the configdialog.
    """

    def __init__(self, option, config):
        Gtk.ComboBoxText.__init__(self)
        self.option = option
        self.config = config
        for key in COLOR_SCHEMES:
            self.append_text(COLOR_SCHEMES[key])
        current = self.config.get(self.option)
        self.set_active(current)
        self.connect("changed", self.update)

    def update(self, obj):
        current = self.get_active()
        self.config.set(self.option, current)


def format_color_css(background, border):
    """
    Return a formatted css color string.
    """
    scheme = global_config.get("colors.scheme")
    css = ""
    if background:
        css = "background-color: {};".format(background[scheme])
    if border:
        css = "{} border-color: {};".format(css, border[scheme])
    return css


def get_confidence_color_css(index, config):
    """
    Return css color string based on confidence rating.
    """
    if not index and index != 0:
        return ""

    key = CONFIDENCE_COLOR_SCHEME[index]
    background = config.get("preferences.profile.colors.confidence.{}".format(key))
    border = config.get("preferences.profile.colors.confidence.border-{}".format(key))
    return format_color_css(background, border)


def get_relationship_color_css(index, config):
    """
    Return css color string based on relationship.
    """
    if not index:
        return ""

    key = None
    if index == "self":
        key = "active"
    else:
        key = "none"
        for relative in RELATIVES:
            if relative in ["wife", "husband"]:
                if "spouse" in index:
                    key = "spouse"
            elif relative in index:
                key = relative
                break

    background = config.get("preferences.profile.colors.relations.{}".format(key))
    border = config.get("preferences.profile.colors.relations.border-{}".format(key))
    return format_color_css(background, border)


def get_event_category_color_css(index, config):
    """
    Return css color string based on event category.
    """
    if not index:
        return ""

    background = config.get("preferences.profile.colors.events.{}".format(index))
    border = config.get("preferences.profile.colors.events.border-{}".format(index))
    return format_color_css(background, border)


def get_person_color_css(person, config, living=False, home=None):
    """
    Return css color string based on person information.
    """
    if not person:
        return ""
        
    if person.gender == Person.MALE:
        key = "male"
    elif person.gender == Person.FEMALE:
        key = "female"
    else:
        key = "unknown"
    if living:
        value = "alive"
    else:
        value = "dead"

    border = global_config.get("colors.border-{}-{}".format(key, value))
    if home and home.handle == person.handle:
        key = "home"
        value = "person"
    background = global_config.get("colors.{}-{}".format(key, value))
    return format_color_css(background, border)


def get_family_color_css(family, config, divorced=False):
    """
    Return css color string based on family information.
    """
    background = global_config.get("colors.family")
    border = global_config.get("colors.border-family")

    if family and family.type is not None:
        key = family.type.value
        if divorced:
            border = global_config.get("colors.border-family-divorced")
            key = 99
        values = {
            0: "-married",
            1: "-unmarried",
            2: "-civil-union",
            3: "-unknown",
            4: "",
            99: "-divorced",
        }
        background = global_config.get(
            "colors.family{}".format(values[key])
        )
    return format_color_css(background, border)


def get_participants(db, event):
    """
    Get all of the participants related to an event.
    Returns people and also a descriptive string.
    We eventually need to handle family but defer for moment.
    """
    participants = []
    text = ""
    comma = ""
    result_list = list(
        db.find_backlink_handles(event.handle,
                                 include_classes=['Person'])
    )
    people = set([x[1] for x in result_list if x[0] == 'Person'])
    for handle in people:
        person = db.get_person_from_handle(handle)
        if not person:
            continue
        for event_ref in person.get_event_ref_list():
            if event.handle == event_ref.ref:
                participants.append((person, event_ref))
                text = "{}{}{}".format(text, comma, name_displayer.display(person))
                comma = ", "
    return participants, text
