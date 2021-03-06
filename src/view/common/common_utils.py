#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2015-2016  Nick Hall
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
Common utility functions and classes
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
import hashlib
from html import escape

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Person
from gramps.gen.lib.primaryobj import BasicPrimaryObject
from gramps.gen.utils.db import navigation_label

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .common_const import (
    _CONFIDENCE,
    _KP_ENTER,
    _RETURN,
    _SPACE,
    BUTTON_PRIMARY,
    CONFIDENCE_COLOR_SCHEME,
    GRAMPS_OBJECTS,
)
from .timeline import RELATIVES

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TextLink Class
#
# ------------------------------------------------------------------------
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
        self.obj_type = obj_type
        self.callback = callback
        self.handle = handle
        self.name = escape(name)
        if markup:
            self.name = markup.format(self.name)
        if bold:
            self.name = "<b>%s</b>" % self.name
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
            self.connect("button-press-event", self.validate)
            self.connect("enter-notify-event", self.enter)
            self.connect("leave-notify-event", self.leave)
        if tooltip:
            self.set_tooltip_text(tooltip)

    def validate(self, _dummy_obj, event):
        """
        Validate primary button click.
        """
        if button_pressed(event, BUTTON_PRIMARY):
            self.callback(self.obj_type, self.handle)
            return True
        return False

    def enter(self, _dummy_obj, _dummy_event):
        """
        Cursor entered so highlight.
        """
        self.label.set_markup("<u>%s</u>" % self.name)

    def leave(self, _dummy_obj, _dummy_event):
        """
        Cursor left so reset.
        """
        self.label.set_markup(self.name)


def get_object_type(obj, lang=False):
    """
    Return Gramps object information.
    """
    for obj_data in GRAMPS_OBJECTS:
        if isinstance(obj, obj_data[0]):
            if lang:
                return obj_data[2]
            return obj_data[1]
    return ""


def button_pressed(event, mouse_button):
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


def button_released(event, mouse_button):
    """
    Test if specific button release happened.
    """
    return (
        event.type == Gdk.EventType.BUTTON_RELEASE
        and event.button == mouse_button
    ) or (
        event.type == Gdk.EventType.KEY_PRESS
        and event.keyval in (_RETURN, _KP_ENTER, _SPACE)
    )


def get_confidence(level):
    """
    Return textual string for the confidence level.
    """
    return _CONFIDENCE[level]


def format_color_css(background, border):
    """
    Return a formatted css color string.
    """
    scheme = global_config.get("colors.scheme")
    css = ""
    if background:
        css = "background-color: %s;" % background[scheme]
    if border:
        css = "%s border-color: %s;" % (css, border[scheme])
    return css


def get_confidence_color_css(index, config):
    """
    Return css color string based on confidence rating.
    """
    if not index and index != 0:
        return ""

    key = CONFIDENCE_COLOR_SCHEME[index]
    background = config.get("colors.confidence.%s" % key)
    border = config.get("colors.confidence.border-%s" % key)
    return format_color_css(background, border)


def get_relationship_color_css(relationship, config):
    """
    Return css color string based on relationship.
    """
    if not relationship:
        return ""

    index = relationship.lower()
    key = None
    if index == "self":
        key = "active"
    else:
        key = "none"
        for relative in RELATIVES:
            if relative in index:
                if relative in ["wife", "husband"]:
                    key = "spouse"
                else:
                    key = relative
                break

    background = config.get("colors.relations.%s" % key)
    border = config.get("colors.relations.border-%s" % key)
    return format_color_css(background, border)


def get_event_category_color_css(index, config):
    """
    Return css color string based on event category.
    """
    if not index:
        return ""

    background = config.get("colors.events.%s" % index)
    border = config.get("colors.events.border-%s" % index)
    return format_color_css(background, border)


def get_event_role_color_css(index, config):
    """
    Return css color string based on event role.
    """
    if not index:
        return ""

    background = config.get("colors.roles.%s" % index)
    border = config.get("colors.roles.border-%s" % index)
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

    border = global_config.get("colors.border-%s-%s" % (key, value))
    if home and home.handle == person.handle:
        key = "home"
        value = "person"
    background = global_config.get("colors.%s-%s" % (key, value))
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
        background = global_config.get("colors.family%s" % values[key])
    return format_color_css(background, border)


def get_config_option(config, option, full=False):
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
    if option_data:
        return option_data.split(":")
    return "", ""


def save_config_option(config, option, option_type, option_value=""):
    """
    Save a compound config option.
    """
    config.set(option, "%s:%s" % (option_type, option_value))


def citation_option_text(db, citation):
    """
    Helper to build citation description string.
    """
    if citation.source_handle:
        source = db.get_source_from_handle(citation.source_handle)
        if source.title:
            text = source.title
        else:
            text = "[%s]" % _("Missing Source")
    if citation.page:
        text = "%s: %s" % (text, citation.page)
    else:
        text = "%s: [%s]" % (text, _("Missing Page"))
    return text


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


def prepare_icon(name, size=Gtk.IconSize.SMALL_TOOLBAR, tooltip=None):
    """
    Prepare an icon.
    """
    icon = Gtk.Image()
    icon.set_from_icon_name(name, size)
    if not tooltip:
        return icon
    image = Gtk.EventBox(tooltip_text=tooltip)
    image.add(icon)
    return image


def pack_icon(
    widget,
    name,
    size=Gtk.IconSize.SMALL_TOOLBAR,
    tooltip=None,
    add=False,
    start=False,
):
    """
    Pack an icon in a widget.
    """
    icon = prepare_icon(name, size=size, tooltip=tooltip)
    if add:
        return widget.add(icon)
    if start:
        return widget.pack_start(icon, False, False, 1)
    return widget.pack_end(icon, False, False, 1)


def find_reference(obj, reference_type, reference_handle):
    """
    Find a specific reference object inside a given object.
    """
    if reference_type == "EventRef":
        reference_list = obj.event_ref_list
    elif reference_type == "ChildRef":
        reference_list = obj.child_ref_list
    elif reference_type == "MediaRef":
        reference_list = obj.media_list
    elif reference_type == "PersonRef":
        reference_list = obj.person_ref_list
    elif reference_type == "RepoRef":
        reference_list = obj.reporef_list
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
    obj_list = grstate.dbstate.db.find_backlink_handles(obj.handle)
    for (obj_type, obj_handle) in obj_list:
        if obj_type in seek:
            work_obj = grstate.fetch(obj_type, obj_handle)
            reference = find_secondary_object(
                work_obj, reference_type, reference_hash
            )
            if reference:
                return work_obj
    return None


def get_secondary_object_list(obj, secondary_type):
    """
    Return list of secondary objects.
    """
    if secondary_type == "Name":
        secondary_list = [obj.primary_name] + obj.alternate_names
    elif secondary_type == "Attribute":
        secondary_list = obj.attribute_list
    elif secondary_type == "Address":
        secondary_list = obj.address_list
    elif secondary_type == "LdsOrd":
        secondary_list = obj.lds_ord_list
    elif secondary_type == "ChildRef":
        secondary_list = obj.child_ref_list
    elif secondary_type == "PersonRef":
        secondary_list = obj.person_ref_list
    elif secondary_type == "RepoRef":
        secondary_list = obj.reporef_list
    else:
        return None
    return secondary_list


def find_secondary_object(obj, secondary_type, secondary_hash):
    """
    Find a specific secondary object inside a given object.
    """
    secondary_list = get_secondary_object_list(obj, secondary_type)
    if secondary_list:
        for secondary_obj in secondary_list:
            sha256_hash = hashlib.sha256()
            sha256_hash.update(str(secondary_obj.serialize()).encode("utf-8"))
            if sha256_hash.hexdigest() == secondary_hash:
                return secondary_obj
    return None


def find_modified_secondary_object(secondary_type, old_obj, updated_obj):
    """
    Compares an old and updated object to find the updated secondary object.
    This is assumed to be used in a specific context where no one added a
    new one, and it is okay if they deleted and old one.
    """
    old_list = get_secondary_object_list(old_obj, secondary_type)
    new_list = get_secondary_object_list(updated_obj, secondary_type)
    for obj in old_list:
        obj_serialized = obj.serialize()
        for new_obj in new_list:
            if new_obj.serialize() == obj_serialized:
                new_list.remove(new_obj)
                break
    if len(new_list) == 1:
        return new_list[0]
    return None


def make_scrollable(widget, hexpand=False, vexpand=True):
    """
    Prepare a scrollable widget.
    """
    scroll = Gtk.ScrolledWindow(hexpand=hexpand, vexpand=vexpand)
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    viewport = Gtk.Viewport()
    viewport.add(widget)
    scroll.add(viewport)
    return scroll


def set_dnd_css(row, top):
    """
    Set custom CSS for the drag and drop view.
    """
    if top:
        text = "top"
    else:
        text = "bottom"
    css = ".frame { border-%s-width: 3px; border-%s-color: #4e9a06; }" % (
        text,
        text,
    )
    provider = Gtk.CssProvider()
    provider.load_from_data(css.encode("utf-8"))
    context = row.get_style_context()
    context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
    context.add_class("frame")
    return provider


def describe_object(db, obj):
    """
    Return description string for a Gramps object.
    """

    def clean_title(title, split_character):
        """
        Cleanup title.
        """
        if split_character in title:
            return title.split(split_character)[1].strip()
        return title.strip()

    for obj_data in GRAMPS_OBJECTS:
        if isinstance(obj, obj_data[0]):
            (
                dummy_obj_class,
                obj_type,
                obj_lang,
                dummy_dnd_type,
                dummy_dnd_icon,
            ) = obj_data
            if not obj_lang:
                obj_lang = obj_type
            break
    if isinstance(obj, BasicPrimaryObject):
        title, dummy_obj = navigation_label(db, obj_type, obj.handle)
        title = clean_title(title, "]")
        if obj_type == "Event":
            title = clean_title(title, "-")
        return title
    if obj_type == "Tag":
        return obj.name
    if obj_type == "Attribute":
        return "%s: %s" % (_("Attribute"), str(obj.get_type()))
    if obj_type == "EventRef":
        title, dummy_obj = navigation_label(db, "Event", obj.ref)
        title = clean_title(title, "]")
        title = clean_title(title, "-")
        return "%s %s: %s" % (_("Event"), _("Reference"), title)
    if obj_type == "ChildRef":
        title, dummy_obj = navigation_label(db, "Person", obj.ref)
        title = clean_title(title, "]")
        return "%s %s: %s" % (_("Child"), _("Reference"), title)
    if obj_type == "PersonRef":
        title, dummy_obj = navigation_label(db, "Person", obj.ref)
        title = clean_title(title, "]")
        return "%s %s: %s" % (_("Person"), _("Reference"), title)
    return obj_lang


def format_address(address):
    """
    Return address lines.
    """
    lines = []
    if address.street:
        lines.append(address.street)
    elif hasattr(address, "addr") and address.addr:
        lines.append(address.addr)
    if address.country in ["USA", "United States", "United States of America"]:
        format_address_usa(lines, address)
    else:
        format_address_international(lines, address)
    return lines


def format_address_international(lines, address):
    """
    Format an international address.
    """
    if address.city:
        lines.append(address.city)
    elif address.locality:
        lines.append(address.locality)
    if address.county:
        lines.append(address.county)
    if address.postal:
        lines.append(address.postal)
    if address.country:
        lines.append(address.country)


def format_address_usa(lines, address):
    """
    Format a US style address.
    """
    line = ""
    comma = ""
    if address.city:
        line = address.city
        comma = ", "
    elif address.county:
        line = "%s%s%s" % (line, comma, address.county)
        comma = ", "
    if address.state:
        line = "%s%s%s" % (line, comma, address.state)
    if address.postal:
        line = "%s %s" % (line, address.postal)
    if line:
        lines.append(line)
    if address.country:
        lines.append(address.country)


def get_initial_object(db, obj_type=None):
    """
    Try to find an initial object.
    """
    if not db.is_open() and not db.get_dbid():
        return None

    if obj_type in [None, "Person"]:
        initial_person = db.find_initial_person()
        if initial_person:
            return (
                "Person",
                initial_person.handle,
                None,
                None,
                None,
                None,
            )

    if obj_type:
        search_list = [obj_type]
    else:
        search_list = [
            "Person",
            "Family",
            "Event",
            "Place",
            "Media",
            "Citation",
            "Source",
            "Repository",
        ]
    for search_type in search_list:
        get_handles = db.method("get_%s_handles", search_type)
        handles = get_handles()
        if handles:
            return (obj_type, handles[0], None, None, None, None)
    return None


def prepare_markup(config, key="detail", scheme=0):
    """
    Prepare text markup string.
    """
    if config.get("display.use-smaller-%s-font" % key):
        size = "small"
    else:
        size = "medium"

    foreground = config.get("display.default-foreground-color")
    return '<span foreground="%s" size="%s">{}</span>' % (
        foreground[scheme],
        size,
    )
