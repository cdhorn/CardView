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
Common utility functions and classes
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import hashlib
from html import escape

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.lib import EventType, Person, Span
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.db import family_name

from ..timeline import RELATIVES

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .common_const import (
    _CONFIDENCE,
    _KP_ENTER,
    _RETURN,
    _SPACE,
    CONFIDENCE_COLOR_SCHEME,
    GRAMPS_OBJECTS,
)

_ = glocale.translation.sgettext


def get_age(base_event, current_event, today=None):
    """
    Return age text if applicable.
    """
    if base_event and base_event.date:
        if current_event and current_event.date or today:
            if today:
                current = today
            else:
                current = current_event.date
            span = Span(base_event.date, current)
            if span.is_valid():
                precision = global_config.get(
                    "preferences.age-display-precision"
                )
                age = str(span.format(precision=precision))
                if age and age != "unknown":
                    return age
    return ""


def button_activated(event, mouse_button):
    """
    Test if specific button press happened.
    """
    return (
        event.type == Gdk.EventType.BUTTON_PRESS
        and event.button == mouse_button
    ) or (
        event.type == Gdk.EventType.KEY_PRESS
        and event.keyval in (_RETURN, _KP_ENTER, _SPACE)
    )


def get_gramps_object_type(obj):
    """
    Return information for primary and some secondary Gramps objects.
    """
    for obj_type in GRAMPS_OBJECTS:
        if isinstance(obj, obj_type[0]):
            return obj_type[2]
    return ""


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
    result = calc.get_one_relationship(
        db, base_person, person, extra_info=True
    )
    if result[0]:
        return "{} {} {}".format(
            result[0].capitalize(), _("of"), base_person_name
        )
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
        self,
        name,
        obj_type=None,
        handle=None,
        callback=None,
        tooltip=None,
        hexpand=False,
        bold=True,
        markup=None,
    ):
        Gtk.EventBox.__init__(self)
        self.name = escape(name)
        if markup:
            self.name = markup.format(self.name)
        if bold:
            self.name = "<b>{}</b>".format(self.name)
        self.label = Gtk.Label(
            hexpand=hexpand,
            halign=Gtk.Align.START,
            wrap=True,
            xalign=0.0,
            justify=Gtk.Justification.LEFT,
        )
        self.label.set_markup(self.name)
        self.add(self.label)
        if callback:
            self.connect("button-press-event", callback, obj_type, handle)
            self.connect("enter-notify-event", self.enter)
            self.connect("leave-notify-event", self.leave)
        if tooltip:
            self.set_tooltip_text(tooltip)

    def enter(self, _dummy_obj, _dummy_event):
        """
        Cursor entered so highlight.
        """
        self.label.set_markup("<u>{}</u>".format(self.name))

    def leave(self, _dummy_obj, _dummy_event):
        """
        Cursor left so reset.
        """
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
    background = config.get("options.colors.confidence.{}".format(key))
    border = config.get("options.colors.confidence.border-{}".format(key))
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

    background = config.get("options.colors.relations.{}".format(key))
    border = config.get("options.colors.relations.border-{}".format(key))
    return format_color_css(background, border)


def get_event_category_color_css(index, config):
    """
    Return css color string based on event category.
    """
    if not index:
        return ""

    background = config.get("options.colors.events.{}".format(index))
    border = config.get("options.colors.events.border-{}".format(index))
    return format_color_css(background, border)


def get_event_role_color_css(index, config):
    """
    Return css color string based on event role.
    """
    if not index:
        return ""

    background = config.get("options.colors.roles.{}".format(index))
    border = config.get("options.colors.roles.border-{}".format(index))
    return format_color_css(background, border)


def get_person_color_css(person, living=False, home=None):
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


def get_family_color_css(family, divorced=False):
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
        background = global_config.get("colors.family{}".format(values[key]))
    return format_color_css(background, border)


def get_participants(db, event):
    """
    Get all of the participants related to an event.
    Returns people and also a descriptive string.
    """
    participants = []
    result_list = list(
        db.find_backlink_handles(
            event.handle, include_classes=["Person", "Family"]
        )
    )
    people = [x[1] for x in result_list if x[0] == "Person"]
    for handle in people:
        person = db.get_person_from_handle(handle)
        if not person:
            continue
        for event_ref in person.get_event_ref_list():
            if event.handle == event_ref.ref:
                participants.append(
                    (
                        "Person",
                        person,
                        event_ref,
                        name_displayer.display(person),
                    )
                )
    families = [x[1] for x in result_list if x[0] == "Family"]
    for handle in families:
        family = db.get_family_from_handle(handle)
        if not family:
            continue
        for event_ref in family.get_event_ref_list():
            if event.handle == event_ref.ref:
                participants.append(
                    ("Family", family, event_ref, family_name(family, db))
                )
    return participants


def get_primary_participant(participants):
    """
    Return first primary participant found, or first if none found
    """
    for participant in participants:
        (obj_type, dummy_obj, obj_event_ref, dummy_obj_name) = participant
        role = obj_event_ref.get_role()
        if obj_type == "Person" and role.is_primary():
            return participant
        if obj_type == "Family" and role.is_family():
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

    for participant in participants:
        (dummy_obj_type, obj, dummy_obj_event_ref, obj_name) = participant
        if obj.get_handle() == primary_obj.get_handle():
            continue
        text = "{}; {}".format(text, obj_name)
    return text


def get_config_option(config, option, full=False, dbid=None):
    """
    Extract a compound config option.
    """
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
        default_value = config.get_default(option)
        if isinstance(default_value, str):
            option_parts = default_value.split(":")
            return option_parts
        return []
    return option_data.split(":")


def save_config_option(
    config, option, option_type, option_value="", dbid=None
):
    """
    Save a compound config option.
    """
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


class ConfigReset(Gtk.ButtonBox):
    """
    Class to manage resetting configuration options.
    """

    def __init__(self, dialog, grstate, space, label=None):
        Gtk.ButtonBox.__init__(self, spacing=6)
        self.set_layout(Gtk.ButtonBoxStyle.END)
        self.button = Gtk.Button(hexpand=False)
        self.pack_start(self.button, False, False, 0)
        self.grstate = grstate
        self.dialog = dialog
        self.config = grstate.config
        self.space = space
        if label:
            self.button.set_label(label)
        else:
            self.button.set_label(_("Defaults"))
        self.button.connect("clicked", self.reset_option_space)
        self.button.set_tooltip_text(
            _(
                "This option will examine a set of options and set any "
                "that were changed back to their default value. It may "
                "apply to a whole page or in some cases a part of a page. "
                "Note if it finds and has to reset any values when done "
                "it will close the configuration dialog and you will need "
                "to reopen it. Redraw logic has not been implemented yet."
            )
        )

    def confirm_reset(self):
        """
        Confirm reset action.
        """
        dialog = Gtk.Dialog(parent=self.grstate.uistate.window)
        dialog.set_title(_("Reset Option Defaults"))
        dialog.set_default_size(500, 300)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)

        message = _(
            "You are about to reset the options on this page back to "
            "their default values.\n\n"
            "If any options are found to reset then when done the "
            "configuration dialog will close and you will need to "
            "reopen it if needed.\n\n"
            "Are you sure you want to proceed?"
        )
        label = Gtk.Label(
            hexpand=True,
            vexpand=True,
            halign=Gtk.Align.CENTER,
            justify=Gtk.Justification.CENTER,
            use_markup=True,
            wrap=True,
            label=message,
        )
        dialog.vbox.add(label)
        all_button = Gtk.CheckButton(
            label=_("Reset all options to defaults, not just this page.")
        )
        dialog.vbox.add(all_button)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            if all_button.get_active():
                self.space = "options."
            return True
        return False

    def reset_option_space(self, _dummy_obj):
        """
        Reset any options that changed in a given space.
        """
        if self.confirm_reset():
            reset_option = False
            options = self.get_option_space()
            for option in options:
                current_value = self.config.get(option)
                default_value = self.config.get_default(option)
                if current_value != default_value:
                    self.config.set(option, default_value)
                    reset_option = True
            if reset_option:
                self.dialog.done(None, None)

    def get_option_space(self):
        """
        Get all the options available in a given space.
        """
        settings = self.config.get_section_settings("options")
        prefix = self.space.replace("options.", "")
        prefix_length = len(prefix)
        options = []
        for setting in settings:
            if setting[:prefix_length] == prefix:
                options.append("options.{}".format(setting))
        return options


def attribute_option_text(attribute):
    """
    Helper to build attribute description string.
    """
    text = "{}: {}".format(attribute.get_type(), attribute.get_value())
    if len(text) > 50:
        text = text[:50] + "..."
    return text


def citation_option_text(db, citation):
    """
    Helper to build citation description string.
    """
    if citation.source_handle:
        source = db.get_source_from_handle(citation.source_handle)
        if source.get_title():
            text = source.get_title()
        else:
            text = "[{}]".format(_("Missing Source"))
    if citation.page:
        text = "{}: {}".format(text, citation.page)
    else:
        text = "{}: [{}]".format(text, _("Missing Page"))
    return text


def note_option_text(note):
    """
    Helper to build note description string.
    """
    notetype = str(note.get_type())
    text = note.get()[:50].replace("\n", " ")
    if len(text) > 40:
        text = text[:40] + "..."
    return "{}: {}".format(notetype, text)


def menu_item(icon, label, callback, data1=None, data2=None):
    """
    Helper for constructing a menu item.
    """
    image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
    item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=label)
    if data2 is not None:
        item.connect("activate", callback, data1, data2)
    elif data1 is not None:
        item.connect("activate", callback, data1)
    else:
        item.connect("activate", callback)
    return item


def submenu_item(icon, label, menu):
    """
    Helper for constructing a submenu item.
    """
    image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
    item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=label)
    item.set_submenu(menu)
    return item


def get_bookmarks(db, obj_type):
    """
    Return bookmarks for given object type.
    """
    if obj_type == "Person":
        return db.get_bookmarks()
    if obj_type == "Citation":
        return db.get_citation_bookmarks()
    if obj_type == "Event":
        return db.get_event_bookmarks()
    if obj_type == "Family":
        return db.get_family_bookmarks()
    if obj_type == "Media":
        return db.get_media_bookmarks()
    if obj_type == "Note":
        return db.get_note_bookmarks()
    if obj_type == "Place":
        return db.get_place_bookmarks()
    if obj_type == "Source":
        return db.get_source_bookmarks()
    if obj_type == "Repository":
        return db.get_repo_bookmarks()
    return []


def pack_icon(widget, icon_name, tooltip=None, add=False, start=False):
    """
    Pack an icon in a widget.
    """
    icon = Gtk.Image()
    icon.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    if tooltip:
        image = Gtk.EventBox(tooltip_text=tooltip)
        image.add(icon)
    else:
        image = icon
    if add:
        return widget.add(image)
    if start:
        return widget.pack_start(image, False, False, 1)
    return widget.pack_end(image, False, False, 1)


def find_reference(obj, reference_type, reference_handle):
    """
    Find a specific reference object inside a given object.
    """
    if reference_type == "EventRef":
        reference_list = obj.get_event_ref_list()
    elif reference_type == "ChildRef":
        reference_list = obj.get_child_ref_list()
    elif reference_type == "MediaRef":
        reference_list = obj.get_media_list()
    elif reference_type == "PersonRef":
        reference_list = obj.get_person_ref_list()
    elif reference_type == "RepoRef":
        reference_list = obj.get_reporef_list()
    else:
        return None
    for reference in reference_list:
        if reference.ref == reference_handle:
            return reference
    return None


def find_referencer(grstate, obj, reference_type, reference_hash):
    """
    Given a referenced object and reference hash find the referencing object.
    """
    if reference_type == "ChildRef":
        seek = ["Family"]
    elif reference_type == "PersonRef":
        seek = ["Person"]
    elif reference_type == "RepoRef":
        seek = ["Source"]
    else:
        return None
    obj_list = grstate.dbstate.db.find_backlink_handles(obj.get_handle())
    for (obj_type, obj_handle) in obj_list:
        if obj_type in seek:
            work_obj = grstate.fetch(obj_type, obj_handle)
            reference = find_secondary_object(
                work_obj, reference_type, reference_hash
            )
            if reference:
                return work_obj
    return None


def find_secondary_object(obj, secondary_type, secondary_hash):
    """
    Find a specific secondary object inside a given object.
    """
    if secondary_type == "Name":
        secondary_list = [obj.get_primary_name()] + obj.get_alternate_names()
    elif secondary_type == "Attribute":
        secondary_list = obj.get_attribute_list()
    elif secondary_type == "Address":
        secondary_list = obj.get_address_list()
    elif secondary_type == "LdsOrd":
        secondary_list = obj.get_lds_ord_list()
    elif secondary_type == "ChildRef":
        secondary_list = obj.get_child_ref_list()
    elif secondary_type == "PersonRef":
        secondary_list = obj.get_person_ref_list()
    elif secondary_type == "RepoRef":
        secondary_list = obj.get_reporef_list()
    else:
        return None
    for secondary_obj in secondary_list:
        sha256_hash = hashlib.sha256()
        sha256_hash.update(str(secondary_obj.serialize()).encode("utf-8"))
        if sha256_hash.hexdigest() == secondary_hash:
            return secondary_obj
    return None


def get_event_category(self, event):
    """
    Return the category for grouping an event.
    """
    event_type = event.get_type()
    for entry in event_type.get_menu_standard_xml():
        event_key = entry[0].lower().replace("life events", "vital")
        for event_id in entry[1]:
            if event_type == event_id:
                return event_key
    custom_event_types = self.db_handle.get_event_types()
    for event_name in custom_event_types:
        if event_type.xml_str() == event_name:
            return "custom"
    return "other"
