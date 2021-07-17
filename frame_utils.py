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
# Python modules
#
# ------------------------------------------------------------------------
from html import escape


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
from gramps.gen.errors import HandleError
from gramps.gen.lib import (
    AttributeType,
    Citation,
    Event,
    EventType,
    Family,
    Media,
    Note,
    Person,
    Place,
    Repository,
    Source,
)
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.db import family_name
from gramps.gui.ddtargets import DdTargets
from gramps.gui.selectors import SelectorFactory


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

CONFIDENCE_COLOR_SCHEME = {
    Citation.CONF_VERY_LOW: "very-low",
    Citation.CONF_LOW: "low",
    Citation.CONF_NORMAL: "normal",
    Citation.CONF_HIGH: "high",
    Citation.CONF_VERY_HIGH: "very-high",
}

EVENT_DISPLAY_MODES = [
    (0, _("Show life span only and nothing else")),
    (1, _("Single line with place")),
    (2, _("Single line with no place")),
    (3, _("Abbreviated single line with place")),
    (4, _("Abbreviated single line with no place")),
    (5, _("Split line")),
    (6, _("Abbreviated split line")),
]

TAG_DISPLAY_MODES = [
    (0, _("Disabled")),
    (1, _("Show icons")),
    (2, _("Show tag names"))
]

IMAGE_DISPLAY_MODES = [
    (0, _("No image displayed")),
    (1, _("Small image on right")),
    (2, _("Large image on right")),
    (3, _("Small image on left")),
    (4, _("Large image on left")),
]

SEX_DISPLAY_MODES = [
    (0, _("No indicator displayed")),
    (1, _("Indicator to left of name")),
    (2, _("Indicator to right of name"))
]

TIMELINE_COLOR_MODES = [
    (0, _("Person scheme")),
    (1, _("Relationship scheme")),
    (2, _("Event category scheme")),
    (3, _("Evidence confidence scheme"))
]


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
    elif isinstance(obj, Media):
        return "Media", DdTargets.MEDIAOBJ, 'gramps-media'
    
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
            self, name, obj_type=None, handle=None, callback=None, tooltip=None, hexpand=False, bold=True
    ):
        Gtk.EventBox.__init__(self)
        self.name = escape(name)
        if bold:
            self.name = "<b>{}</b>".format(self.name)
        self.label = Gtk.Label(hexpand=hexpand, halign=Gtk.Align.START, wrap=True)
        self.label.set_markup(self.name)
        self.add(self.label)
        if callback:
            self.connect("button-press-event", callback, obj_type, handle)
            self.connect("enter-notify-event", self.enter)
            self.connect("leave-notify-event", self.leave)
        if tooltip:
            self.set_tooltip_text(tooltip)

    def enter(self, obj, event):
        self.label.set_markup("<u>{}</u>".format(self.name))

    def leave(self, obj, event):
        self.label.set_markup(self.name)


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
    """
    participants = []
    text = ""
    comma = ""
    result_list = list(
        db.find_backlink_handles(event.handle,
                                 include_classes=['Person', 'Family'])
    )
    people = set([x[1] for x in result_list if x[0] == 'Person'])
    for handle in people:
        person = db.get_person_from_handle(handle)
        if not person:
            continue
        for event_ref in person.get_event_ref_list():
            if event.handle == event_ref.ref:
                participants.append(('Person', person, event_ref))
                text = "{}{}{}".format(text, comma, name_displayer.display(person))
                comma = ", "
    family = set([x[1] for x in result_list if x[0] == 'Family'])
    for handle in family:
        family = db.get_family_from_handle(handle)
        if not family:
            continue
        for event_ref in family.get_event_ref_list():
            if event.handle == event_ref.ref:
                participants.append(('Family', family, event_ref))
                family_text = family_name(family, db)
                text = "{}{}{}".format(text, comma, family_text)
                comma = ", "
    return participants, text


def get_config_option(config, option, full=False, dbid=None, defaults=None):
    try:
        option_data = config.get(option)
    except AttributeError:
        if not full:
            return "", ""
        return False
    if full:
        return option_data
    if dbid:
        current_option_list = option_data.split(",")
        for current_option in current_option_list:
            if ":" in current_option:
                option_parts = current_option.split(":")
                if option_parts[0] == dbid:
                    return option_parts[1:]
        if defaults:
            for default_option, default_value in defaults:
                if option == default_option:
                    if isinstance(default_value, str):
                        option_parts = default_value.split(":")
                        return option_parts
        return []
    return option_data.split(":")


def save_config_option(config, option, option_type, option_value="", dbid=None):
    if dbid:
        option_list = []
        option_data = config.get(option)
        if option_data:
            current_option_list = option_data.split(",")
            for current_option in current_option_list:
                option_parts = current_option.split(":")
                if len(option_parts) >= 3:
                    if option_parts[0] != dbid:
                        option_list.append(current_option)
        option_list.append("{}:{}:{}".format(dbid, option_type, option_value))
        config.set(option, ",".join(option_list))
    else:
        config.set(option, "{}:{}".format(option_type, option_value))


def get_attribute_types(db, obj_type):
    """
    Get the available attribute types based on current object type.
    """
    if obj_type == "Person":
        return db.get_person_attribute_types()
    if obj_type == "Family":
        return db.get_family_attribute_types()
    if obj_type == "Event":
        return db.get_event_attribute_types()
    if obj_type == "Media":
        return db.get_media_attribute_types()
    if obj_type == "Source":
        return db.get_source_attribute_types()
    if obj_type == "Citation":
        return db.get_source_attribute_types()
    return []


def get_attribute_maps(db, obj_type):
    """
    Return forward and reverse language mappings for attribute types.
    """
    etoi = {}
    itoe = {}
    inames = []
    enames = []
    for attribute_type in AttributeType().get_standard_names():
        inames.append(attribute_type)
    for attribute_type in AttributeType().get_standard_xml():
        enames.append(attribute_type)
    while len(enames) > 0:
        etoi.update({enames[0]: inames[0]})
        itoe.update({inames[0]: enames[0]})
        del enames[0]
        del inames[0]

    for attribute in get_attribute_types(db, obj_type):
        etoi.update({attribute: attribute})
        itoe.update({attribute: attribute})
    if "None" not in etoi:
        etoi.update({"None": _("None")})
        itoe.update({_("None"): "None"})
    return etoi, itoe


def get_event_maps(db):
    """
    Return forward and reverse language mappings for event types.
    """
    etoi = {}
    itoe = {}
    inames = []
    enames = []
    for event_type in EventType().get_standard_names():
        inames.append(event_type)
    for event_type in EventType().get_standard_xml():
        enames.append(event_type)
    while len(enames) > 0:
        etoi.update({enames[0]: inames[0]})
        itoe.update({inames[0]: enames[0]})
        del enames[0]
        del inames[0]

    for event in db.get_event_types():
        etoi.update({event: event})
        itoe.update({event: event})
    if "None" not in etoi:
        etoi.update({"None": _("None")})
        itoe.update({_("None"): "None"})
    return etoi, itoe


class AttributeSelector(Gtk.ComboBoxText):
    """
    An attribute selector for the configdialog.
    """

    def __init__(self, option, config, db, obj_type, dbid=False, tooltip=None):
        Gtk.ComboBoxText.__init__(self)
        self.option = option
        self.config = config
        self.dbid = None
        if dbid:
            self.dbid = db.get_dbid()

        self.etoi, self.itoe = get_attribute_maps(db, obj_type)
        attribute_names = sorted(self.itoe.keys())
        for attribute_type in attribute_names:
            self.append_text(attribute_type)

        current_option = get_config_option(self.config, self.option, dbid=self.dbid)
        current_value = "None"
        if current_option and len(current_option) >= 2:
            current_value = current_option[1]
        if current_value in self.etoi:
            current_index = attribute_names.index(self.etoi[current_value])
        self.set_active(current_index)
        self.connect("changed", self.update)
        if tooltip:
            self.set_tooltip_text(tooltip)

    def update(self, obj):
        current_value = self.get_active_text()
        save_config_option(self.config, self.option, "Attribute", self.itoe[current_value], dbid=self.dbid)


class FrameFieldSelector(Gtk.HBox):
    """
    A custom selector for the user defined fields for the configdialog.
    """

    def __init__(self, option, config, dbstate, uistate, number, dbid=False, defaults=None, text=None, relation=True, obj_type="Person"):
        Gtk.HBox.__init__(self, hexpand=False, spacing=6)
        self.option = option
        self.config = config
        self.dbstate = dbstate
        self.uistate = uistate
        self.defaults = defaults
        self.dbid = None
        if dbid:
            self.dbid = self.dbstate.db.get_dbid()

        if text:
            label_text = "{} {}:".format(text, number)
        else:
            label_text = "{} {}:".format(_("Field"), number)
        label = Gtk.Label(label=label_text)
        self.pack_start(label, False, False, 0)
        self.type_selector = Gtk.ComboBoxText()
        self.pack_start(self.type_selector, False, False, 0)
        self.event_selector = Gtk.ComboBoxText()
        self.event_selector.connect("show", self.hide_event_selector)
        self.pack_start(self.event_selector, False, False, 0)
        self.attribute_selector = Gtk.ComboBoxText()
        self.attribute_selector.connect("show", self.hide_attribute_selector)
        self.pack_start(self.attribute_selector, False, False, 0)
        self.all_matches = Gtk.CheckButton(label=_("All"))
        self.all_matches.connect("show", self.hide_event_selector)
        self.pack_start(self.all_matches, False, False, 0)
        self.relation_selector = Gtk.Button()
        self.relation_selector.connect("show", self.hide_button)
        self.pack_start(self.relation_selector, False, False, 0)

        self.user_field_types = ["None", "Event", "Fact", "Attribute", "Relation"]
        self.user_field_types_lang = [_("None"), _("Event"), _("Fact"), _("Attribute"), _("Relation")]
        if not relation:
            del self.user_field_types_lang[-1]
        for option in self.user_field_types_lang:
            self.type_selector.append_text(option)

        self.attribute_etoi, self.attribute_itoe = get_attribute_maps(self.dbstate.db, obj_type)
        self.attribute_names = sorted(self.attribute_itoe.keys())
        for attribute_type in self.attribute_names:
            self.attribute_selector.append_text(attribute_type)

        self.event_etoi, self.event_itoe = get_event_maps(self.dbstate.db)
        self.event_names = sorted(self.event_itoe.keys())
        for event_type in self.event_names:
            self.event_selector.append_text(event_type)

        self.all_matches.set_tooltip_text(_("Enabling this option will enable the display of all records found. This is generally undesirable for most things, but can sometimes be useful if for example someone held multiple occupations and you wanted that information available at a glance."))

        user_type = "None"
        user_value = ""
        user_option = False
        current_option = get_config_option(
            self.config,
            self.option,
            dbid=self.dbid,
            defaults=self.defaults
        )
        if current_option and current_option[0] != "None":
            user_type = current_option[0]
            user_value = current_option[1]
            if len(current_option) >= 3:
                if current_option[2] == "True":
                    user_option = True
        current_index = self.user_field_types.index(user_type)
        self.type_selector.set_active(current_index)
        self.type_selector.set_tooltip_text(_("All person or family facts displayed are user configurable and they may be populated with event, fact, attribute or relation data in a number of different combinations. Not all combinations may make sense, but this mechanism allows the user to tailor the view to their needs. Note fact and event types are the same, the difference between them is that for an event the date and place are displayed while for a fact the event description is displayed. So a baptism is an event while an occupation can be thought of as a fact."))

        if current_index in [1, 2]:
            self.hide_selectors(event=False, all=False)
            if self.event_etoi[user_value] in self.event_names:
                current_index = self.event_names.index(self.event_etoi[user_value])
                self.event_selector.set_active(current_index)
                self.all_matches.set_active(user_option)
        elif current_index == 3:
            self.hide_selectors(attribute=False, all=False)
            if self.attribute_etoi[user_value] in self.attribute_names:
                current_index = self.attribute_names.index(self.attribute_etoi[user_value])
                self.attribute_selector.set_active(current_index)
                self.all_matches.set_active(user_option)
        elif current_index == 4:
            self.hide_selectors(relation=False)
            try:
                person = self.dbstate.db.get_person_from_handle(user_value)
                name = name_displayer.display(person)
                self.relation_selector.set_label(name)
            except HandleError:
                self.relation_selector.set_label("")
        else:
            self.hide_selectors()

        self.type_selector.connect("changed", self.update_type)
        self.event_selector.connect("changed", self.update_event_choice)
        self.all_matches.connect("toggled", self.update_all_choice)
        self.attribute_selector.connect("changed", self.update_attribute_choice)
        self.relation_selector.connect("clicked", self.update_relation_choice)

    def hide_selectors(self, event=True, attribute=True, relation=True, all=True):
        if event:
            self.event_selector.hide()
        if relation:
            self.relation_selector.hide()
        if attribute:
            self.attribute_selector.hide()
        if all:
            self.all_matches.hide()

    def update_type(self, obj):
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        current_type = self.user_field_types[current_index]
        save_config_option(self.config, self.option, current_type, "", dbid=self.dbid)
        if current_type in ["Event", "Fact"]:
            self.hide_selectors(event=False, all=False)
            current_index = self.event_names.index(self.event_etoi["Unknown"])
            self.event_selector.set_active(current_index)
            self.event_matches.set_active(False)
            self.event_selector.show()
            self.all_matches.show()
            self.update_event_choice()
        elif current_type == "Attribute":
            self.hide_selectors(attribute=False, all=False)
            current_index = self.attribute_names.index(self.attribute_etoi["None"])
            self.attribute_selector.set_active(current_index)
            self.attribute_selector.show()
            self.all_matches.show()
            self.update_attribute_choice()
        elif current_type == "Relation":
            self.hide_selectors(relation=False)
            self.relation_selector.set_label("")
            self.relation_selector.show()
            self.update_relation_choice()
        else:
            self.all_matches.set_active(False)
            self.relation_selector.set_label("")
            self.hide_selectors()

    def update_event_choice(self, *obj):
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index in [1, 2]:
            current_value = self.event_selector.get_active_text()
            if self.all_matches.get_active():
                current_option = "True"
            else:
                current_option = "False"
            save_config_option(
                self.config,
                self.option,
                self.user_field_types[current_index],
                "{}:{}".format(self.event_itoe[current_value], current_option),
                dbid=self.dbid
            )

    def update_all_choice(self, *obj):
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index in [1, 2]:
            self.update_event_choice()
        elif current_index == 3:
            self.update_attribute_choice()

    def update_attribute_choice(self, *obj):
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index == 3:
            current_value = self.attribute_selector.get_active_text()
            if self.all_matches.get_active():
                current_option = "True"
            else:
                current_option = "False"
            save_config_option(
                self.config,
                self.option,
                self.user_field_types[current_index],
                "{}:{}".format(self.attribute_itoe[current_value], current_option),
                dbid=self.dbid
            )

    def update_relation_choice(self, *obj):
        SelectPerson = SelectorFactory("Person")
        selector = SelectPerson(
            self.dbstate, self.uistate, [], _("Select Person")
        )
        person = selector.run()
        if person:
            name = name_displayer.display(person)
            self.relation_selector.set_label(name)
            save_config_option(
                self.config,
                self.option,
                "Relation",
                person.get_handle(),
                dbid=self.dbid
            )

    def hide_button(self, obj):
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index != 4:
            self.relation_selector.hide()

    def hide_event_selector(self, obj):
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index not in [1, 2]:
            self.event_selector.hide()
            if current_index != 3:
                self.all_matches.hide()

    def hide_attribute_selector(self, obj):
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index != 3:
            self.attribute_selector.hide()
            if current_index not in [1, 2]:
                self.all_matches.hide()


class ConfigReset(Gtk.Button):
    """
    Class to manage resetting configuration options.
    """

    def __init__(self, dialog, config, space, defaults, label=None):
        Gtk.Button.__init__(self, hexpand=False)
        self.dialog = dialog
        self.config = config
        self.space = "{}.".format(space)
        self.defaults = defaults
        if label:
            self.set_label(label)
        else:
            self.set_label(_("Reset Page Defaults"))
        self.connect("clicked", self.reset)
        self.set_tooltip_text(_("This option will examine a set of options and set any that were changed back to their default value. It may apply to a whole page or in some cases a part of a page. Note if it finds and has to reset any values when done it will close the configuration dialog and you will need to reopen it. Redraw logic has not been implemented yet."))

    def reset(self, obj):
        option_length = len(self.space)
        reset_option = False
        for option, value in self.defaults:
            if option[:option_length] == self.space:
                current_value = self.config.get(option)
                if current_value != value:
                    print("resetting {}".format(option))
                    self.config.set(option, value)
                    reset_option = True
        if reset_option:
            self.dialog.done(None, None)
