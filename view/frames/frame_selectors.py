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
Frame option selection classes
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
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import HandleError
from gramps.gen.lib import (
    AttributeType,
    EventType,
)
from gramps.gen.display.name import displayer as name_displayer
from gramps.gui.selectors import SelectorFactory


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_utils import get_config_option, save_config_option

_ = glocale.translation.sgettext


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
        dbid=False,
        text=None,
        obj_type="Person",
    ):
        Gtk.HBox.__init__(self, hexpand=False, spacing=6)
        self.option = option
        self.grstate = grstate
        self.dbid = None
        if dbid:
            self.dbid = self.grstate.dbstate.db.get_dbid()

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

        self.user_field_types = [
            "None",
            "Attribute",
            "Fact",
            "Event",
            "Relation",
        ]
        self.user_field_types_lang = [
            _("None"),
            _("Attribute"),
            _("Fact"),
            _("Event"),
            _("Relation"),
        ]
        if mode != "all":
            del self.user_field_types_lang[-1]
            if mode != "event":
                del self.user_field_types_lang[-1]
                del self.user_field_types_lang[-1]
        for item in self.user_field_types_lang:
            self.type_selector.append_text(item)

        self.attribute_etoi, self.attribute_itoe = get_attribute_maps(
            self.grstate.dbstate.db, obj_type
        )
        self.attribute_names = sorted(self.attribute_itoe.keys())
        for attribute_type in self.attribute_names:
            self.attribute_selector.append_text(attribute_type)

        self.event_etoi, self.event_itoe = get_event_maps(
            self.grstate.dbstate.db
        )
        self.event_names = sorted(self.event_itoe.keys())
        for event_type in self.event_names:
            self.event_selector.append_text(event_type)

        self.all_matches.set_tooltip_text(
            _(
                "Enabling this option will enable the display of all "
                "records found. This is generally undesirable for most "
                "things, but can sometimes be useful if for example "
                "someone held multiple occupations and you wanted that "
                "information available at a glance."
            )
        )

        user_type = "None"
        user_value = ""
        user_option = False
        current_option = get_config_option(
            self.grstate.config,
            self.option,
            dbid=self.dbid,
        )
        if current_option and current_option[0] != "None":
            user_type = current_option[0]
            user_value = current_option[1]
            if len(current_option) >= 3:
                if current_option[2] == "True":
                    user_option = True
        current_index = self.user_field_types.index(user_type)
        self.type_selector.set_active(current_index)
        self.type_selector.set_tooltip_text(
            _(
                "All person or family facts displayed are user "
                "configurable and they may be populated with event, "
                "fact, attribute or relation data in a number of "
                "different combinations. Not all combinations may "
                "make sense, but this mechanism allows the user to "
                "tailor the view to their needs. Note fact and event "
                "types are the same, the difference between them is "
                "that for an event the date and place are displayed "
                "while for a fact the event description is displayed. "
                "So a baptism is an event while an occupation can be "
                "thought of as a fact."
            )
        )

        if current_index in [2, 3]:
            self.hide_selectors(event=False, all=False)
            if self.event_etoi[user_value] in self.event_names:
                current_index = self.event_names.index(
                    self.event_etoi[user_value]
                )
                self.event_selector.set_active(current_index)
                self.all_matches.set_active(user_option)
        elif current_index == 1:
            self.hide_selectors(attribute=False, all=False)
            if self.attribute_etoi[user_value] in self.attribute_names:
                current_index = self.attribute_names.index(
                    self.attribute_etoi[user_value]
                )
                self.attribute_selector.set_active(current_index)
        elif current_index == 4:
            self.hide_selectors(relation=False)
            try:
                person = self.grstate.fetch("Person", user_value)
                name = name_displayer.display(person)
                self.relation_selector.set_label(name)
            except HandleError:
                self.relation_selector.set_label("")
            except AttributeError:
                self.relation_selector.set_label("")
        else:
            self.hide_selectors()

        self.type_selector.connect("changed", self.update_type)
        self.event_selector.connect("changed", self.update_event_choice)
        self.all_matches.connect("toggled", self.update_all_choice)
        self.attribute_selector.connect("changed", self.update_attribute_choice)
        self.relation_selector.connect("clicked", self.update_relation_choice)

    def hide_selectors(
        self, event=True, attribute=True, relation=True, all=True
    ):
        """
        Hide the inactive selectors.
        """
        if event:
            self.event_selector.hide()
        if relation:
            self.relation_selector.hide()
        if attribute:
            self.attribute_selector.hide()
        if all:
            self.all_matches.hide()

    def update_type(self, _dummy_obj):
        """
        Save updated option data.
        """
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        current_type = self.user_field_types[current_index]
        save_config_option(
            self.grstate.config, self.option, current_type, "", dbid=self.dbid
        )
        if current_type in ["Event", "Fact"]:
            self.hide_selectors(event=False, all=False)
            current_index = self.event_names.index(self.event_etoi["Unknown"])
            self.event_selector.set_active(current_index)
            self.event_selector.show()
            self.all_matches.show()
            self.update_event_choice()
        elif current_type == "Attribute":
            self.hide_selectors(attribute=False, all=False)
            current_index = self.attribute_names.index(
                self.attribute_etoi["None"]
            )
            self.attribute_selector.set_active(current_index)
            self.attribute_selector.show()
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

    def update_event_choice(self, *_dummy_obj):
        """
        Save updated event choice.
        """
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index in [2, 3]:
            current_value = self.event_selector.get_active_text()
            if self.all_matches.get_active():
                current_option = "True"
            else:
                current_option = "False"
            save_config_option(
                self.grstate.config,
                self.option,
                self.user_field_types[current_index],
                "{}:{}".format(self.event_itoe[current_value], current_option),
                dbid=self.dbid,
            )

    def update_all_choice(self, *_dummy_obj):
        """
        Save updated show all choice.
        """
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index in [2, 3]:
            self.update_event_choice()

    def update_attribute_choice(self, *_dummy_obj):
        """
        Save updated attribute choice.
        """
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index == 1:
            current_value = self.attribute_selector.get_active_text()
            save_config_option(
                self.grstate.config,
                self.option,
                self.user_field_types[current_index],
                self.attribute_itoe[current_value],
                dbid=self.dbid,
            )

    def update_relation_choice(self, *_dummy_obj):
        """
        Save updated relation choice.
        """
        select_person = SelectorFactory("Person")
        selector = select_person(
            self.grstate.dbstate, self.grstate.uistate, [], _("Select Person")
        )
        person = selector.run()
        if person:
            name = name_displayer.display(person)
            self.relation_selector.set_label(name)
            save_config_option(
                self.grstate.config,
                self.option,
                "Relation",
                person.get_handle(),
                dbid=self.dbid,
            )

    def hide_button(self, _dummy_obj):
        """
        Hide relation button.
        """
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index != 4:
            self.relation_selector.hide()

    def hide_event_selector(self, _dummy_obj):
        """
        Hide event selector.
        """
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index not in [2, 3]:
            self.event_selector.hide()
            self.all_matches.hide()

    def hide_attribute_selector(self, _dummy_obj):
        """
        Hide attribute selector.
        """
        current_type_lang = self.type_selector.get_active_text()
        current_index = self.user_field_types_lang.index(current_type_lang)
        if current_index != 1:
            self.attribute_selector.hide()
            if current_index not in [2, 3]:
                self.all_matches.hide()
