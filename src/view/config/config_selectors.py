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
Config option selection classes
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
from copy import copy

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import HandleError
from gramps.gen.lib import AttributeType, EventType
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import get_config_option, save_config_option
from ..services.service_fields import FieldCalculatorService

_ = glocale.translation.sgettext

VALUE_TYPES = {
    "None": _("None"),
    "Attribute": _("Attribute"),
    "Calculated": _("Calculated"),
    "Event": _("Event"),
    "Fact": _("Fact"),
    "Relationship": _("Relationship"),
}

CALCULATED_PERSON_TYPES = {
    "None": _("None"),
    "Child Number": _("Child Number"),
    "Duration": _("Duration"),
    "Lifespan": _("Lifespan"),
    "Living": _("Living"),
    "Occupations": _("Occupations"),
    "Maternal Progenitors": _("Maternal Progenitors"),
    "Paternal Progenitors": _("Paternal Progenitors"),
}

CALCULATED_FAMILY_TYPES = {
    "None": _("None"),
    "Duration": _("Duration"),
    "Ages": _("Ages"),
    "Bride Age": _("Bride Age"),
    "Groom Age": _("Groom Age"),
    "Relationship": _("Relationship"),
}

CALCULATED_ATTRIBUTE_TYPES = {
    "None": _("None"),
    "Soundex": _("Soundex"),
}


def get_type_maps(mode):
    """
    Get category type maps.
    """
    itoe = {}
    categories = copy(VALUE_TYPES)
    if mode != "all":
        del categories["Relationship"]
        if mode == "status":
            del categories["Calculated"]
            del categories["Fact"]
            del categories["Attribute"]
        elif mode != "event":
            del categories["Event"]
            del categories["Fact"]
    for category in categories:
        itoe.update({categories[category]: category})
    return categories, itoe


def get_attribute_types(db, obj_type):
    """
    Get available attribute types based on current object type.
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
    return etoi, itoe


def get_calculated_maps(obj_type):
    """
    Return forward and reverse language mappings for calculated types.
    """
    itoe = {}
    values = FieldCalculatorService().get_values(obj_type)
    if values:
        for value in values:
            itoe.update({values[value]: value})
    return values, itoe


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
    return etoi, itoe


def map_builder(db, obj_type, value_type):
    """
    Build and return needed option maps.
    """
    etoi, itoe = {}, {}
    if value_type in ["Event", "Fact"]:
        etoi, itoe = get_event_maps(db)
    elif value_type in ["Calculated"]:
        etoi, itoe = get_calculated_maps(obj_type)
    elif value_type in ["Attribute"]:
        etoi, itoe = get_attribute_maps(db, obj_type)
    elif value_type in ["Types"]:
        etoi, itoe = get_type_maps(obj_type)
    if "None" not in etoi:
        etoi.update({"None": _("None")})
        itoe.update({_("None"): "None"})
    return etoi, itoe


# ------------------------------------------------------------------------
#
# FieldSelector Class
#
# ------------------------------------------------------------------------
class FieldSelector(Gtk.HBox):
    """
    Language sensitive field or person selector.
    """

    def __init__(self, grstate, option, obj_type, value_type, value="None"):
        Gtk.HBox.__init__(self, vexpand=False, hexpand=False)
        self.grstate = grstate
        self.option = option
        self.obj_type = obj_type
        self.value_type = value_type
        self.value = value
        self.etoi = {}
        self.itoe = {}
        self.person = None
        self.selector = None
        self.ready = False
        self.load(obj_type, value_type, value=value)
        self.ready = True

    def load(self, obj_type, value_type, value="None"):
        """
        Load selector.
        """
        list(map(self.remove, self.get_children()))
        self.obj_type = obj_type
        self.value_type = value_type
        self.value = value
        if self.value_type == "Relationship":
            self.load_relation()
        else:
            self.load_value()
        self.pack_start(self.selector, False, False, 0)
        self.show_all()

    def load_value(self):
        """
        Load value selector.
        """
        self.selector = Gtk.ComboBoxText()
        self.etoi, self.itoe = map_builder(
            self.grstate.dbstate.db, self.obj_type, self.value_type
        )
        keys = sorted(self.itoe.keys())
        for value in keys:
            self.selector.append_text(value)
        if self.value in self.etoi and self.etoi[self.value] in keys:
            index = keys.index(self.etoi[self.value])
            self.selector.set_active(index)
        if self.value_type not in ["None", "Types"]:
            self.selector.connect("changed", self.update_value)

    def load_relation(self):
        """
        Load relation selector.
        """
        self.selector = Gtk.Button()
        self.person = None
        if self.value and not self.ready:
            try:
                self.person = self.grstate.fetch("Person", self.value)
                self.selector.set_label(name_displayer.display(self.person))
            except HandleError:
                self.selector.set_label(_("None"))
            except AttributeError:
                self.selector.set_label(_("None"))
        else:
            self.select_relation()
        self.selector.connect("clicked", self.select_relation)

    def select_relation(self, *_dummy_args):
        """
        Select a relation.
        """
        select_person = SelectorFactory("Person")
        selector = select_person(
            self.grstate.dbstate, self.grstate.uistate, [], _("Select Person")
        )
        self.person = selector.run()
        if self.person:
            self.selector.set_label(name_displayer.display(self.person))
            self.update_value()

    def get_index(self):
        """
        Get current index.
        """
        if self.value_type == "Relationship":
            if self.person:
                return self.person.get_handle()
        else:
            value = self.selector.get_active_text()
            if value in self.itoe:
                return self.itoe[value]
        return "None"

    def update_value(self, *_dummy_obj):
        """
        Save updated value choice.
        """
        current_value = self.get_index()
        save_config_option(
            self.grstate.config,
            self.option,
            self.value_type,
            current_value,
        )


# ------------------------------------------------------------------------
#
# FrameFieldSelector Class
#
# ------------------------------------------------------------------------
class FrameFieldSelector(Gtk.HBox):
    """
    A custom selector for the user defined fields for the configdialog.
    """

    def __init__(
        self,
        option,
        grstate,
        number,
        mode="all",
        text=None,
        obj_type="Person",
        size_groups=None,
    ):
        Gtk.HBox.__init__(self, hexpand=False, spacing=6)
        self.option = option
        self.grstate = grstate
        self.obj_type = obj_type

        if text:
            label_text = "%s %s:" % (text, str(number))
        else:
            label_text = "%s %s:" % (_("Field"), str(number))
        label = Gtk.Label(label=label_text)
        if size_groups and "label" in size_groups:
            size_groups["label"].add_widget(label)
        self.pack_start(label, False, False, 0)
        user_type, user_value = self.get_current_option()

        self.type_selector = FieldSelector(
            self.grstate, option, mode, "Types", value=user_type
        )
        if size_groups and "type" in size_groups:
            size_groups["type"].add_widget(self.type_selector)
        self.pack_start(self.type_selector, False, False, 0)

        self.value_selector = FieldSelector(
            self.grstate,
            option,
            self.obj_type,
            user_type,
            value=user_value,
        )
        if size_groups and "value" in size_groups:
            size_groups["value"].add(self.value_selector)
        self.pack_start(self.value_selector, False, False, 0)

        self.type_selector.set_tooltip_text(
            _(
                "All person or family facts displayed are user "
                "configurable and they may be populated with event, "
                "fact, attribute, relationship or calculated data "
                "in a number of different combinations. Not all "
                "combinations may make sense, but this mechanism "
                "allows the user to tailor the view to their needs. "
                "Note fact and event types are the same, the "
                "difference between them is that for an event the "
                "date and place are displayed while for a fact the "
                "event description is displayed. So a baptism is an "
                "event while an occupation can be thought of as a fact."
            )
        )
        self.type_selector.selector.connect("changed", self.update_type)

    def get_current_option(self):
        """
        Get current option value.
        """
        user_type = "None"
        user_value = "None"
        current_option = get_config_option(
            self.grstate.config,
            self.option,
        )
        if current_option and current_option[0] != "None":
            user_type = current_option[0]
            user_value = current_option[1]
        return user_type, user_value

    def update_type(self, _dummy_obj):
        """
        Type changed, clear selections.
        """
        current_type = self.type_selector.get_index()
        save_config_option(
            self.grstate.config,
            self.option,
            current_type,
            "None",
        )
        self.value_selector.load(self.obj_type, current_type)
