#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
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
PersonGrampsFrame
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
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import HandleError, WindowActiveError
from gramps.gen.lib import ChildRef, Event, EventRef, Family, Name, Person
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.db import family_name
from gramps.gui.editors import EditEventRef, EditFamily, EditName
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_const import (
    _BIRTH_EQUIVALENTS,
    _DEATH_EQUIVALENTS,
    _GENDERS,
)
from ..common.common_utils import (
    TextLink,
    format_date_string,
    get_person_color_css,
    get_relation,
    menu_item,
    submenu_item,
)
from .frame_primary import PrimaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PersonGrampsFrame class
#
# ------------------------------------------------------------------------
class PersonGrampsFrame(PrimaryGrampsFrame):
    """
    The PersonGrampsFrame exposes some of the basic facts about a Person.
    """

    def __init__(
        self,
        grstate,
        groptions,
        person,
    ):
        PrimaryGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            person,
        )
        self.relation = groptions.relation
        self.backlink = groptions.backlink
        self.context = groptions.option_space.split(".")[2]

        display_name = name_displayer.display(person)
        name = TextLink(
            display_name,
            "Person",
            person.handle,
            self.switch_object,
            bold=True,
        )
        name_box = Gtk.HBox(spacing=2)
        if groptions.frame_number:
            label = Gtk.Label(
                use_markup=True,
                label=self.markup.format(
                    "{}. ".format(groptions.frame_number)
                ),
            )
            name_box.pack_start(label, False, False, 0)
        if self.get_option("sex-mode") == 1:
            name_box.pack_start(
                Gtk.Label(label=_GENDERS[person.gender]), False, False, 0
            )
        name_box.pack_start(name, False, False, 0)
        if self.get_option("sex-mode") == 2:
            name_box.pack_start(
                Gtk.Label(label=_GENDERS[person.gender]), False, False, 0
            )
        self.widgets["title"].pack_start(name_box, True, True, 0)
        self.living = True

        event_cache = []
        for event_ref in person.get_primary_event_ref_list():
            event_cache.append(self.fetch("Event", event_ref.ref))
        if self.get_option("event-format") == 0:
            self.load_years(event_cache)
        else:
            self.load_fields(event_cache, "facts-field")
            if "active" in groptions.option_space:
                self.load_fields(event_cache, "extra-field", extra=True)
        if groptions.age_base:
            self.load_age_at_event(event_cache)
        del event_cache

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def load_age_at_event(self, event_cache):
        """
        Parse and if have birth load age field.
        """
        print("load_age_at_event")
        birth, dummy_var1 = self._get_birth_death(event_cache)
        if birth:
            self.load_age(birth.date, self.groptions.age_base)

    def load_years(self, event_cache):
        """
        Parse and load birth and death dates only.
        """
        birth, death = self._get_birth_death(event_cache)
        text = format_date_string(birth, death)
        self.add_fact(self.make_label(text))

    def _get_birth_death(self, event_cache):
        """
        Extract birth and death events.
        """
        birth = False
        death = False
        for event in event_cache:
            event_type = event.get_type().xml_str()
            if event_type == "Birth":
                birth = event
            elif event_type == "Death":
                death = event
                self.living = False
            elif event_type in _DEATH_EQUIVALENTS:
                self.living = False

        if self.living:
            self.living = probably_alive(
                self.primary.obj, self.grstate.dbstate.db
            )
        return birth, death

    def load_fields(self, event_cache, field_type, extra=False):
        """
        Parse and load a set of facts about a person.
        """
        key = "{}-skip-birth-alternates".format(field_type)
        skip_birth_alternates = self.get_option(key)
        key = "{}-skip-death-alternates".format(field_type)
        skip_death_alternates = self.get_option(key)
        have_birth, have_death = self._get_birth_death(event_cache)

        count = 1
        while count < 9:
            option = self.get_option(
                "{}-{}".format(field_type, count),
                full=False,
                keyed=True,
            )
            if (
                option
                and option[0] != "None"
                and len(option) > 1
                and option[1]
            ):
                if len(option) >= 3:
                    show_all = bool(option[2] == "True")
                if option[0] == "Event":
                    if option[1] == "Death" and self.living:
                        show_age = self.get_option("show-age")
                        if extra:
                            self.widgets["extra"].add_living(
                                have_birth, show_age=show_age
                            )
                        else:
                            self.widgets["facts"].add_living(
                                have_birth, show_age=show_age
                            )
                    else:
                        self.add_field_for_event(
                            event_cache,
                            option[1],
                            extra=extra,
                            show_all=show_all,
                            skip_birth=skip_birth_alternates,
                            have_birth=have_birth,
                            skip_death=skip_death_alternates,
                            have_death=have_death,
                        )
                elif option[0] == "Fact":
                    self.add_field_for_fact(
                        event_cache, option[1], extra=extra, show_all=show_all
                    )
                elif option[0] == "Attribute":
                    self.add_field_for_attribute(
                        option[1], extra=extra, show_all=show_all
                    )
                elif option[0] == "Relation":
                    self.add_field_for_relation(option[1], extra=extra)
            count = count + 1

    def add_field_for_event(
        self,
        event_cache,
        event_type,
        extra=False,
        show_all=False,
        skip_birth=False,
        have_birth=None,
        skip_death=False,
        have_death=None,
    ):
        """
        Find an event and load the data.
        """
        show_age = False
        for event in event_cache:
            if event.get_type().xml_str() == event_type:
                if skip_birth and have_birth:
                    if event_type in _BIRTH_EQUIVALENTS:
                        return
                if skip_death and have_death:
                    if event_type in _DEATH_EQUIVALENTS:
                        return
                if event_type in _DEATH_EQUIVALENTS or event_type == "Death":
                    show_age = self.get_option("show-age")
                self.add_event(
                    event, extra=extra, reference=have_birth, show_age=show_age
                )
                if not show_all:
                    return

    def add_field_for_fact(
        self, event_cache, event_type, extra=False, show_all=False
    ):
        """
        Find an event and load the data.
        """
        for event in event_cache:
            if event.get_type().xml_str() == event_type:
                if event.get_description():
                    label = TextLink(
                        str(event.get_type()),
                        "Event",
                        event.get_handle(),
                        self.switch_object,
                        bold=False,
                        markup=self.markup,
                    )
                    fact = TextLink(
                        event.get_description(),
                        "Event",
                        event.get_handle(),
                        self.switch_object,
                        bold=False,
                        markup=self.markup,
                    )
                    self.add_fact(fact, label=label, extra=extra)
                    if not show_all:
                        return

    def add_field_for_attribute(
        self, attribute_type, extra=False, show_all=False
    ):
        """
        Find an attribute and load the data.
        """
        for attribute in self.primary.obj.get_attribute_list():
            if attribute.get_type().xml_str() == attribute_type:
                if attribute.get_value():
                    label = self.make_label(str(attribute.get_type()))
                    fact = self.make_label(attribute.get_value())
                    self.add_fact(fact, label=label, extra=extra)
                    if not show_all:
                        return

    def add_field_for_relation(self, handle, extra=False):
        """
        Calculate a relation and load the fact.
        """
        text = ""
        if self.primary.obj.get_handle() == handle:
            text = _("Home person")
            label = self.make_label(text)
        else:
            try:
                relation = self.fetch("Person", handle)
                relationship = get_relation(
                    self.grstate.dbstate.db,
                    self.primary.obj,
                    relation,
                    depth=global_config.get("behavior.generation-depth"),
                )
                if relationship:
                    text = relationship.title()
                else:
                    name = name_displayer.display(relation)
                    text = "{} {}".format(_("Not related to"), name)
                label = TextLink(
                    text,
                    "Person",
                    handle,
                    self.switch_object,
                    bold=False,
                    markup=self.markup,
                )
            except HandleError:
                text = "[{}]".format(_("Missing Person"))
                label = self.make_label(text)
        if text:
            self.add_fact(label, extra=extra)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.grstate.config.get("options.global.use-color-scheme"):
            return ""

        return get_person_color_css(
            self.primary.obj,
            living=self.living,
            home=self.relation,
        )

    def add_custom_actions(self):
        """
        Add action menu items for the person based on the context in which
        they are present in relation to the active person.
        """
        self.action_menu.append(self._add_new_person_event_option())
        if self.context in ["parent", "spouse", "family", "sibling", "child"]:
            self.action_menu.append(self._add_new_family_event_option())
        if self.context in ["parent", "spouse"]:
            self.action_menu.append(self._add_new_child_to_family_option())
            self.action_menu.append(
                self._add_existing_child_to_family_option()
            )
            self.action_menu.append(
                self._remove_as_parent_from_family_option()
            )
        if self.context in ["sibling", "child"]:
            self.action_menu.append(self._remove_child_from_family_option())
        self.action_menu.append(self._parents_option())
        self.action_menu.append(self._partners_option())
        self.action_menu.append(self._names_option())

    def _names_option(self):
        """
        Build the names submenu.
        """
        menu = Gtk.Menu()
        menu.add(menu_item("list-add", _("Add a name"), self.add_name))
        if len(self.primary.obj.get_alternate_names()) > 0:
            removemenu = Gtk.Menu()
            menu.add(
                submenu_item("gramps-person", _("Remove a name"), removemenu)
            )
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            name = self.primary.obj.get_primary_name()
            given_name = name.get_regular_name()
            menu.add(
                menu_item("gramps-person", given_name, self.edit_name, name)
            )
            for name in self.primary.obj.get_alternate_names():
                given_name = name.get_regular_name()
                removemenu.add(
                    menu_item(
                        "list-remove", given_name, self.remove_name, name
                    )
                )
                menu.add(
                    menu_item(
                        "gramps-person", given_name, self.edit_name, name
                    )
                )
        return submenu_item("gramps-person", _("Names"), menu)

    def add_name(self, _dummy_obj):
        """
        Add a new name.
        """
        name = Name()
        try:
            EditName(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                name,
                self.added_name,
            )
        except WindowActiveError:
            pass

    def added_name(self, name):
        """
        Save the new name to finish adding it.
        """
        if name:
            action = "{} {} {} {} {} {}".format(
                _("Added"),
                _("Name"),
                name.get_regular_name(),
                _("to"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
            self.primary.obj.add_alternate_name(name)
            self.save_object(self.primary.obj, action_text=action)

    def remove_name(self, _dummy_obj, name):
        """
        Remove the given name from the current object.
        """
        if not name:
            return
        text = name.get_regular_name()
        prefix = _(
            "You are about to remove the following name from this object:"
        )
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"), "{}\n\n<b>{}</b>\n\n{}".format(prefix, text, confirm)
        ):
            action = "{} {} {} {} {} {}".format(
                _("Deleted"),
                _("Name"),
                text,
                _("from"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
            name_list = []
            for alternate_name in self.primary.obj.get_alternate_names():
                if alternate_name.serialize() != name.serialize():
                    name_list.append(alternate_name)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.primary.obj.set_alternate_names(name_list)
                self.grstate.dbstate.db.commit_person(self.primary.obj, trans)

    def _add_new_person_event_option(self):
        """
        Build menu item for adding a new event for a person.
        """
        return menu_item(
            "gramps-event",
            _("Add a new person event"),
            self.add_new_person_event,
        )

    def add_new_person_event(self, _dummy_obj):
        """
        Add a new event for a person.
        """
        event = Event()
        ref = EventRef()
        ref.ref = self.primary.obj.get_handle()
        try:
            EditEventRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                event,
                ref,
                self.added_new_person_event,
            )
        except WindowActiveError:
            pass

    def added_new_person_event(self, reference, _dummy_primary):
        """
        Finish adding a new event for a person.
        """
        event = self.fetch("Event", reference.ref)
        action = "{} {} {} {} {} {}".format(
            _("Added"),
            _("Person"),
            self.primary.obj.get_gramps_id(),
            _("to"),
            _("Event"),
            event.get_gramps_id(),
        )
        self.primary.obj.add_event_ref(reference)
        self.save_object(self.primary.obj, action_text=action)

    def _parents_option(self):
        """
        Build menu option for managing parents.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item(
                "gramps-parents-add",
                _("Add a new set of parents"),
                self.add_new_parents,
            )
        )
        menu.add(
            menu_item(
                "gramps-parents-open",
                _("Add as child to an existing family"),
                self.add_existing_parents,
            )
        )
        if self.primary.obj.get_parent_family_handle_list():
            menu.add(Gtk.SeparatorMenuItem())
            for handle in self.primary.obj.get_parent_family_handle_list():
                family = self.fetch("Family", handle)
                family_text = family_name(family, self.grstate.dbstate.db)
                menu.add(
                    menu_item(
                        "gramps-parents",
                        family_text,
                        self.edit_primary_object,
                        family,
                        "Family",
                    )
                )
        return submenu_item("gramps-parents", _("Parents"), menu)

    def add_new_parents(self, *_dummy_obj):
        """
        Add new parents for the person.
        """
        family = Family()
        child_ref = ChildRef()
        child_ref.ref = self.primary.obj.handle
        family.add_child_ref(child_ref)
        try:
            EditFamily(self.grstate.dbstate, self.grstate.uistate, [], family)
        except WindowActiveError:
            pass

    def add_existing_parents(self, *_dummy_obj):
        """
        Add existing parents for the person.
        """
        select_family = SelectorFactory("Family")
        skip = set(self.primary.obj.get_family_handle_list())
        dialog = select_family(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        family = dialog.run()
        if family:
            self.grstate.dbstate.db.add_child_to_family(
                family, self.primary.obj
            )

    def _partners_option(self):
        """
        Build menu option for managing partners.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item(
                "gramps-spouse",
                _("Add as parent of new family"),
                self.add_new_family,
            )
        )
        if self.primary.obj.get_family_handle_list():
            menu.add(Gtk.SeparatorMenuItem())
            for handle in self.primary.obj.get_family_handle_list():
                family = self.fetch("Family", handle)
                family_text = family_name(family, self.grstate.dbstate.db)
                menu.add(
                    menu_item(
                        "gramps-spouse",
                        family_text,
                        self.edit_primary_object,
                        family,
                        "Family",
                    )
                )
        return submenu_item("gramps-spouse", _("Spouses"), menu)

    def add_new_family(self, *_dummy_obj):
        """
        Add person as head of a new family.
        """
        family = Family()
        if self.primary.obj.gender == Person.MALE:
            family.set_father_handle(self.primary.obj.get_handle())
        else:
            family.set_mother_handle(self.primary.obj.get_handle())
        try:
            EditFamily(self.grstate.dbstate, self.grstate.uistate, [], family)
        except WindowActiveError:
            pass

    def _remove_as_parent_from_family_option(self):
        """
        Build menu item for removing as parent from a family.
        """
        image = Gtk.Image.new_from_icon_name("list-remove", Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(
            always_show_image=True,
            image=image,
            label=_("Remove parent from this family"),
        )
        item.connect("activate", self.remove_as_parent_from_family)
        return item

    def remove_as_parent_from_family(self, _dummy_obj):
        """
        Remove a parent from a family.
        """
        if not self.backlink:
            return
        person_name = name_displayer.display(self.primary.obj)
        family = self.fetch("Family", self.backlink)
        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()
        partner_handle = None
        if self.primary.obj.get_handle() == father_handle:
            if mother_handle:
                partner_handle = mother_handle
        elif self.primary.obj.get_handle() == mother_handle:
            if father_handle:
                partner_handle = father_handle
        if partner_handle:
            partner = self.fetch("Person", partner_handle)
            partner_name = name_displayer.display(partner)
            text = (
                "You are about to remove {} as the partner of {} "
                "and a parent of this family.".format(
                    person_name, partner_name
                )
            )
        else:
            text = (
                "You are about to remove {} as a parent of this "
                "family.".format(person_name)
            )
        if not self.confirm_action(
            "Warning",
            "{}\n\nAre you sure you want to continue?".format(text),
        ):
            self.grstate.dbstate.db.remove_parent_from_family(
                self.primary.obj.get_handle(), self.groptions.backlink
            )

    def _remove_child_from_family_option(self):
        """
        Build menu item for removing child from a family.
        """
        return menu_item(
            "list-remove",
            _("Remove child from this family"),
            self.remove_child_from_family,
        )

    def remove_child_from_family(self, _dummy_obj):
        """
        Remove a child from the family.
        """
        if not self.groptions.backlink:
            return
        person_name = name_displayer.display(self.primary.obj)
        family = self.fetch("Family", self.groptions.backlink)
        family_text = family_name(family, self.grstate.dbstate.db)
        if self.confirm_action(
            "Warning",
            "You are about to remove {} from the family of {}.\n\n"
            "Are you sure you want to continue?".format(
                person_name, family_text
            ),
        ):
            self.grstate.dbstate.db.remove_child_from_family(
                self.primary.obj.get_handle(), self.backlink
            )
