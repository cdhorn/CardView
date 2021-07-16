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
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.db import DbTxn
from gramps.gen.errors import HandleError, WindowActiveError
from gramps.gen.lib import (
    EventType,
    Person,
    Family,
    Event,
    ChildRef,
    EventRef,
    EventRoleType,
    Name,
    Surname,
)
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.db import family_name, preset_name
from gramps.gui.editors import EditPerson, EditFamily, EditEventRef
from gramps.gui.selectors import SelectorFactory


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsFrame
from frame_utils import (
    _GENDERS,
    format_date_string,
    get_key_person_events,
    get_person_color_css,
    get_relation,
    TextLink,
)

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

_BIRTH_EQUIVALENTS = ["Baptism", "Christening"]
_DEATH_EQUIVALENTS = ["Burial", "Cremation", "Probate"]


# ------------------------------------------------------------------------
#
# PersonGrampsFrame class
#
# ------------------------------------------------------------------------
class PersonGrampsFrame(GrampsFrame):
    """
    The PersonGrampsFrame exposes some of the basic facts about a Person.
    """

    def __init__(
        self,
        dbstate,
        uistate,
        person,
        context,
        space,
        config,
        router,
        relation=None,
        number=0,
        groups=None,
        family_backlink=None,
        defaults=None
    ):
        GrampsFrame.__init__(self, dbstate, uistate, router, space, config, person, context, groups=groups, defaults=defaults)
        self.person = person
        self.relation = relation
        self.family_backlink = family_backlink
        self.event_cache = []

        for event_ref in self.obj.get_primary_event_ref_list():
            self.event_cache.append(self.dbstate.db.get_event_from_handle(event_ref.ref))
        self.enable_drag()
        self.enable_drop()

        display_name = name_displayer.display(self.person)
        if self.enable_tooltips:
            tooltip = "{} {} {}".format(
                _("Click to view"), display_name, _("or right click to select edit.")
            )
        else:
            tooltip = None
        name = TextLink(
            display_name, "Person", self.person.handle, self.switch_object, tooltip=tooltip, bold=True
        )
        name_box = Gtk.HBox(spacing=2)
        if number:
            label = Gtk.Label(
                use_markup=True, label=self.markup.format("{}. ".format(number))
            )
            name_box.pack_start(label, False, False, 0)
        if self.option(context, "sex-mode") == 1:
            name_box.pack_start(Gtk.Label(label=_GENDERS[self.person.gender]), False, False, 0)
        name_box.pack_start(name, False, False, 0)
        if self.option(context, "sex-mode") == 2:
            name_box.pack_start(Gtk.Label(label=_GENDERS[self.person.gender]), False, False, 0)
        self.title.pack_start(name_box, True, True, 0)

        self.living = probably_alive(self.person, self.dbstate.db)

        self.load_fields("facts-field")
        if self.context == "active":
            self.load_fields("extra-field", extra=True)

        while len(self.event_cache) > 0:
            del self.event_cache[0]
        self.set_css_style()

    def load_fields(self, field_type, extra=False):
        """
        Parse and load a set of facts about a person.
        """
        key = "{}-skip-birth-alternates".format(field_type)
        skip_birth_alternates = self.option(self.context, key)
        key = "{}-skip-death-alternates".format(field_type)
        skip_death_alternates = self.option(self.context, key)
        have_birth = False
        have_death = False
        for event in self.event_cache:
            if event.get_type().xml_str() == "Birth":
                have_birth = True
            elif event.get_type().xml_str() == "Death":
                have_death = True

        count = 1
        while count < 8:
            option = self.option(
                self.context,
                "{}-{}".format(field_type, count),
                full=False,
                keyed=True
            )
            if option and option[0] != "None" and len(option) > 1 and option[1]:
                if len(option) >= 3:
                    if option[2] == "True":
                        show_all = True
                    else:
                        show_all = False
                if option[0] == "Event":
                    self.add_field_for_event(
                        option[1],
                        extra=extra,
                        show_all=show_all,
                        skip_birth=skip_birth_alternates,
                        have_birth=have_birth,
                        skip_death=skip_death_alternates,
                        have_death=have_death
                    )
                elif option[0] == "Fact":
                    self.add_field_for_fact(option[1], extra=extra, show_all=show_all)
                elif option[0] == "Attribute":
                    self.add_field_for_attribute(option[1], extra=extra, show_all=show_all)
                elif option[0] == "Relation":
                    self.add_field_for_relation(option[1], extra=extra)
            count = count + 1

    def add_field_for_event(self, event_type, extra=False, show_all=False,
                            skip_birth=False, have_birth=None, skip_death=False, have_death=None):
        """
        Find an event and load the data.
        """
        for event in self.event_cache:
            if event.get_type().xml_str() == event_type:
                if skip_birth and have_birth:
                    if event_type in _BIRTH_EQUIVALENTS:
                        return
                if skip_death and have_death:
                    if event_type in _DEATH_EQUIVALENTS:
                        return
                self.add_event(event, extra=extra)
                if not show_all:
                    return

    def add_field_for_fact(self, event_type, extra=False, show_all=False):
        """
        Find an event and load the data.
        """
        for event in self.event_cache:
            if event.get_type().xml_str() == event_type:
                if event.get_description():
                    label = self.make_label(str(event.get_type()))
                    fact = self.make_label(event.get_description())
                    self.add_fact(fact, label=label, extra=extra)
                    if not show_all:
                        return

    def add_field_for_attribute(self, attribute_type, extra=False, show_all=False):
        """
        Find an attribute and load the data.
        """
        for attribute in self.obj.get_attribute_list():
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
        if self.person.handle == handle:
            text = _("Home person")
        else:
            try:
                relation = self.dbstate.db.get_person_from_handle(handle)
                relationship = get_relation(
                    self.dbstate.db,
                    self.person,
                    relation,
                    depth=global_config.get("behavior.generation-depth"),
                )
                if relationship:
                    text = relationship.title()
                else:
                    name = name_displayer.display(relation)
                    text = "{} {}".format(_("Not related to"), name)
            except HandleError:
                text = "[{}]".format(_("Missing Person"))
        if text:
            label = self.make_label(text)
            self.add_fact(label, extra=extra)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.config.get("preferences.profile.person.layout.use-color-scheme"):
            return ""

        return get_person_color_css(self.obj, self.config, living=self.living, home=self.relation)

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
            self.action_menu.append(self._add_existing_child_to_family_option())
            self.action_menu.append(self._remove_as_parent_from_family_option())
        if self.context in ["sibling", "child"]:
            self.action_menu.append(self._remove_child_from_family_option())
        self.action_menu.append(self._parents_option())
        self.action_menu.append(self._partners_option())

    def _add_new_person_event_option(self):
        """
        Build menu item for adding a new event for a person.
        """
        return self._menu_item("gramps-event", _("Add a new person event"), self.add_new_person_event)

    def add_new_person_event(self, obj):
        """
        Add a new event for a person.
        """
        event = Event()
        ref = EventRef()
        ref.ref = self.person.handle
        try:
            EditEventRef(
                self.dbstate, self.uistate, [], event, ref, self.added_new_person_event
            )
        except WindowActiveError:
            pass

    def added_new_person_event(self, reference, primary):
        """
        Finish adding a new event for a person.
        """
        event = self.dbstate.db.get_event_from_handle(reference.ref)
        action = "{} {} {} {} {}".format(
            _("Added Person"),
            self.person.get_gramps_id(),
            _("to"),
            _("Event"),
            event.get_gramps_id()
        )
        with DbTxn(action, self.dbstate.db) as trans:
            if self.person.add_event_ref(reference):
                self.dbstate.db.commit_person(self.person, trans)

    def _parents_option(self):
        """
        Build menu option for managing parents.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("gramps-parents-add", _("Add a new set of parents"), self.add_new_parents))
        menu.add(self._menu_item("gramps-parents-open", _("Add as child to an existing family"), self.add_existing_parents))
        if self.obj.parent_family_list:
            menu.add(Gtk.SeparatorMenuItem())
            for handle in self.obj.parent_family_list:
                family = self.dbstate.db.get_family_from_handle(handle)
                family_text = family_name(family, self.dbstate.db)
                menu.add(self._menu_item("gramps-parents", family_text, self.edit_object, family, "Family"))
        return self._submenu_item("gramps-parents", _("Parents"), menu)

    def add_new_parents(self, *obj):
        """
        Add new parents for the person.
        """
        family = Family()
        child_ref = ChildRef()
        child_ref.ref = self.person.handle
        family.add_child_ref(child_ref)
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def add_existing_parents(self, *obj):
        """
        Add existing parents for the person.
        """
        SelectFamily = SelectorFactory("Family")
        skip = set(self.person.get_family_handle_list())
        dialog = SelectFamily(self.dbstate, self.uistate, skip=skip)
        family = dialog.run()
        if family:
            self.dbstate.db.add_child_to_family(family, self.person)

    def _partners_option(self):
        """
        Build menu option for managing partners.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("gramps-spouse", _("Add as parent of new family"), self.add_new_family))
        if self.obj.family_list:
            menu.add(Gtk.SeparatorMenuItem())
            for handle in self.obj.family_list:
                family = self.dbstate.db.get_family_from_handle(handle)
                family_text = family_name(family, self.dbstate.db)
                menu.add(self._menu_item("gramps-spouse", family_text, self.edit_object, family, "Family"))
        return self._submenu_item("gramps-spouse", _("Spouses"), menu)

    def add_new_family(self, *obj):
        """
        Add person as head of a new family.
        """
        family = Family()
        if self.person.gender == Person.MALE:
            family.set_father_handle(self.person.handle)
        else:
            family.set_mother_handle(self.person.handle)
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def _remove_as_parent_from_family_option(self, spouse=False):
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

    def remove_as_parent_from_family(self, obj):
        """
        Remove a parent from a family.
        """
        if self.family_backlink:
            person_name = name_displayer.display(self.person)
            family = self.dbstate.db.get_family_from_handle(self.family_backlink)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            partner_handle = None
            if self.person.handle == father_handle:
                if mother_handle:
                    partner_handle = mother_handle
            elif self.person.handle == mother_handle:
                if father_handle:
                    partner_handle = father_handle
            if partner_handle:
                partner = self.dbstate.db.get_person_from_handle(partner_handle)
                partner_name = name_displayer.display(partner)
                text = "You are about to remove {} as the partner of {} and a parent of this family.".format(person_name, partner_name)
            else:
                text = "You are about to remove {} as a parent of this family.".format(person_name)
            if not self.confirm_action(
                    "Warning",
                    "{}\n\nAre you sure you want to continue?".format(text)
            ):
                self.dbstate.db.remove_parent_from_family(
                    self.person.handle, self.family_backlink
                )
 
    def _remove_child_from_family_option(self):
        """
        Build menu item for removing child from a family.
        """
        return self._menu_item("list-remove", _("Remove child from this family"), self.remove_child_from_family)

    def remove_child_from_family(self, obj):
        """
        Remove a child from the family.
        """
        if self.family_backlink:
            person_name = name_displayer.display(self.person)
            family = self.dbstate.db.get_family_from_handle(self.family_backlink)
            family_text = family_name(family, self.dbstate.db)
            if self.confirm_action(
                    "Warning",
                    "You are about to remove {} from the family of {}.\n\nAre you sure you want to continue?".format(person_name, family_text)
            ):
                self.dbstate.db.remove_child_from_family(
                    self.person.handle, self.family_backlink
                )
