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
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import (
    ChildRef,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    Name,
    Person,
    PersonRef,
)
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.db import family_name
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import (
    EditEventRef,
    EditFamily,
    EditName,
    EditPerson,
    EditPersonRef,
)
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from ..common.common_const import _GENDERS, _RECIPROCAL_ASSOCIATIONS
from ..common.common_utils import get_person_color_css, menu_item, submenu_item
from ..common.common_vitals import format_date_string
from .frame_reference import ReferenceGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PersonGrampsFrame class
#
# ------------------------------------------------------------------------
class PersonGrampsFrame(ReferenceGrampsFrame):
    """
    The PersonGrampsFrame exposes some of the basic facts about a Person.
    """

    def __init__(self, grstate, groptions, person, reference_tuple=None):
        ReferenceGrampsFrame.__init__(
            self, grstate, groptions, person, reference_tuple=reference_tuple
        )
        self.relation = groptions.relation
        self.backlink = groptions.backlink
        self.context = groptions.option_space.split(".")[2]

        display_name = name_displayer.display(person)
        name = self.get_link(
            display_name,
            "Person",
            person.handle,
        )
        name_box = Gtk.HBox(spacing=2)
        if groptions.frame_number:
            label = Gtk.Label(
                use_markup=True,
                label=self.detail_markup.format(
                    "".join((str(groptions.frame_number), ". "))
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

        event_cache = []
        for event_ref in person.get_primary_event_ref_list():
            event_cache.append(self.fetch("Event", event_ref.ref))
        self.birth, self.death, self.living = self._get_birth_death(
            event_cache
        )

        if self.get_option("event-format") == 0:
            self.load_years()
        else:
            self.load_fields("facts", "lfield-", event_cache)
            if "active" in groptions.option_space:
                self.load_fields("extra", "mfield-", event_cache)
        del event_cache
        if groptions.age_base:
            self.load_age_at_event()

        self.enable_drag()
        self.dnd_drop_targets.append(DdTargets.EVENT.target())
        self.dnd_drop_targets.append(DdTargets.PERSON_LINK.target())
        self.enable_drop()
        self.set_css_style()

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        if DdTargets.EVENT.drag_type == dnd_type:
            self.add_new_person_event(None, event_handle=obj_or_handle)
            return True
        if DdTargets.PERSON_LINK.drag_type == dnd_type:
            self.add_new_person_ref(obj_or_handle)
            return True
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def load_age_at_event(self):
        """
        Parse and if have birth load age field.
        """
        if self.birth:
            self.load_age(
                self.birth.get_date_object(), self.groptions.age_base
            )

    def load_years(self):
        """
        Parse and load birth and death dates only.
        """
        text = format_date_string(self.birth, self.death)
        self.add_fact(self.get_label(text))

    def _get_birth_death(self, event_cache):
        """
        Extract birth and death events.
        """
        birth = False
        death = False
        living = True
        birth_ref = self.primary.obj.get_birth_ref()
        death_ref = self.primary.obj.get_death_ref()
        for event in event_cache:
            event_handle = event.get_handle()
            if birth_ref and event_handle == birth_ref.ref:
                birth = event
            elif death_ref and event_handle == death_ref.ref:
                death = event
                living = False
            elif event.get_type().is_death_fallback():
                living = False

        if living:
            living = probably_alive(self.primary.obj, self.grstate.dbstate.db)
        return birth, death, living

    def load_fields(self, grid_key, option_prefix, event_cache):
        """
        Parse and load a set of facts about a person.
        """
        args = {
            "event_format": self.get_option("event-format"),
            "event_cache": event_cache,
            "have_birth": self.birth,
            "have_death": self.death,
        }
        key = "".join((option_prefix, "skip-birth-alternates"))
        args.update({"skip_birth_alternates": self.get_option(key)})
        key = "".join((option_prefix, "skip-death-alternates"))
        args.update({"skip_death_alternates": self.get_option(key)})
        self.load_grid(grid_key, option_prefix, args=args)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.grstate.config.get(
            "options.global.display.use-color-scheme"
        ):
            return ""

        return get_person_color_css(
            self.primary.obj,
            living=self.living,
            home=self.relation,
        )

    def add_custom_actions(self, context_menu):
        """
        Add action menu items for the person based on the context in which
        they are present in relation to the active person.
        """
        context_menu.append(
            menu_item(
                "go-home",
                _("Set home person"),
                self.set_default_person,
            )
        )
        context_menu.append(
            menu_item(
                "gramps-event",
                _("Add a new primary event"),
                self.add_new_person_event,
            )
        )
        context_menu.append(
            menu_item(
                "gramps-event",
                _("Add as participant to an existing event"),
                self.add_existing_person_event,
            )
        )
        if self.context in ["parent", "spouse", "family", "sibling", "child"]:
            context_menu.append(self._add_new_family_event_option())
        if self.context in ["parent", "spouse"]:
            context_menu.append(self._add_new_child_option())
            context_menu.append(self._add_existing_child_option())
            context_menu.append(self._remove_family_parent_option())
        if self.context in ["sibling", "child"]:
            self._set_preferred_parents_option(context_menu)
            context_menu.append(
                menu_item(
                    "list-remove",
                    _("Remove child from this family"),
                    self.remove_family_child,
                )
            )
        context_menu.append(self._parents_option())
        context_menu.append(self._partners_option())
        context_menu.append(self._associations_option())
        context_menu.append(self._names_option())

    def _names_option(self):
        """
        Build the names submenu.
        """
        menu = Gtk.Menu()
        menu.add(menu_item("list-add", _("Add a new name"), self.add_name))
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
            message = " ".join(
                (
                    _("Added"),
                    _("Name"),
                    name.get_regular_name(),
                    _("to"),
                    self.primary.obj_lang,
                    self.primary.obj.get_gramps_id(),
                )
            )
            self.primary.obj.add_alternate_name(name)
            self.primary.commit(self.grstate, message)

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
        if self.confirm_action(_("Warning"), prefix, "\n\n<b>", text, "</b>"):
            message = " ".join(
                (
                    _("Deleted"),
                    _("Name"),
                    text,
                    _("from"),
                    self.primary.obj_lang,
                    self.primary.obj.get_gramps_id(),
                )
            )
            name_list = []
            for alternate_name in self.primary.obj.get_alternate_names():
                if alternate_name.serialize() != name.serialize():
                    name_list.append(alternate_name)
            self.primary.obj.set_alternate_names(name_list)
            self.primary.commit(self.grstate, message)

    def add_existing_person_event(self, *_dummy_args):
        """
        Add person to existing event.
        """
        select_event = SelectorFactory("Event")
        skip = set([x.ref for x in self.primary.obj.get_event_ref_list()])
        dialog = select_event(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        event = dialog.run()
        if event:
            self.add_new_person_event(None, event_handle=event.get_handle())

    def add_new_person_event(self, _dummy_obj, event_handle=None):
        """
        Add a new event for a person.
        """
        if event_handle:
            for event_ref in self.primary.obj.get_event_ref_list():
                if event_ref.ref == event_handle:
                    return
            event = self.fetch("Event", event_handle)
            ref = EventRef()
            ref.ref = event.get_handle()
            ref.set_role(EventRoleType(EventRoleType.UNKNOWN))
        else:
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

    def added_new_person_event(self, reference, event):
        """
        Finish adding a new event for a person.
        """
        message = " ".join(
            (
                _("Added"),
                _("Person"),
                self.primary.obj.get_gramps_id(),
                _("to"),
                _("Event"),
                event.get_gramps_id(),
            )
        )
        if event.get_type() == EventType.BIRTH:
            if self.primary.obj.get_birth_ref() is None:
                self.primary.obj.set_birth_ref(reference)
            else:
                self.primary.obj.add_event_ref(reference)
        elif event.get_type() == EventType.DEATH:
            if self.primary.obj.get_death_ref() is None:
                self.primary.obj.set_death_ref(reference)
            else:
                self.primary.obj.add_event_ref(reference)
        else:
            self.primary.obj.add_event_ref(reference)
        self.primary.commit(self.grstate, message)

    def _associations_option(self):
        """
        Build the associations submenu.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item(
                "list-add",
                _("Add an association for a new person"),
                self.add_association_new_person,
            )
        )
        menu.add(
            menu_item(
                "list-add",
                _("Add an association for an existing person"),
                self.add_association_existing_person,
            )
        )
        if len(self.primary.obj.get_person_ref_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(
                submenu_item(
                    "gramps-person", _("Remove an association"), removemenu
                )
            )
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            for person_ref in self.primary.obj.get_person_ref_list():
                person = self.fetch("Person", person_ref.ref)
                person_name = name_displayer.display(person)
                removemenu.add(
                    menu_item(
                        "list-remove",
                        person_name,
                        self.remove_association,
                        person_ref,
                    )
                )
                menu.add(
                    menu_item(
                        "gramps-person",
                        person_name,
                        self.edit_association,
                        person_ref,
                    )
                )
        return submenu_item("gramps-person", _("Associations"), menu)

    def edit_association(self, _dummy_obj, person_ref):
        """
        Launch the person reference editor.
        """
        try:
            EditPersonRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                person_ref,
                self._save_association_edit,
            )
        except WindowActiveError:
            pass

    def _save_association_edit(self, person_ref):
        """
        Save the person ref edit.
        """
        if person_ref:
            person = self.fetch("Person", person_ref.ref)
            message = self._commit_message(
                _("PersonRef"), person.get_gramps_id(), action="update"
            )
            self.primary.commit(self.grstate, message)

    def add_association_new_person(self, _dummy_obj):
        """
        Create a new person for the association.
        """
        person = Person()
        try:
            EditPerson(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                person,
                self.add_new_person_ref,
            )
        except WindowActiveError:
            pass

    def add_association_existing_person(self, _dummy_obj):
        """
        Select an existing person for the association.
        """
        select_person = SelectorFactory("Person")
        skip = set([x.ref for x in self.primary.obj.get_person_ref_list()])
        skip.add(self.primary.obj.get_handle())
        dialog = select_person(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        person_handle = dialog.run()
        if person_handle:
            self.add_new_person_ref(person_handle)

    def add_new_person_ref(self, person_obj_or_handle):
        """
        Add a new person reference aka association.
        """
        if isinstance(person_obj_or_handle, str):
            person_handle = person_obj_or_handle
        else:
            person_handle = person_obj_or_handle.get_handle()
        for person_ref in self.primary.obj.get_person_ref_list():
            if person_ref.ref == person_handle:
                return
        ref = PersonRef()
        ref.ref = person_handle
        try:
            EditPersonRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                ref,
                self._added_new_person_ref,
            )
        except WindowActiveError:
            pass

    def _added_new_person_ref(self, reference):
        """
        Finish adding a new reference for a person.
        """
        person = self.fetch("Person", reference.ref)
        message = " ".join(
            (
                _("Added"),
                _("PersonRef"),
                person.get_gramps_id(),
                _("to"),
                _("Person"),
                self.primary.obj.get_gramps_id(),
            )
        )
        self.primary.obj.add_person_ref(reference)
        self.primary.commit(self.grstate, message)

        if self.get_option(
            "options.global.general.create-reciprocal-associations"
        ):
            ref = PersonRef()
            ref.ref = self.primary.obj.get_handle()
            ref.set_note_list(reference.get_note_list())
            ref.set_citation_list(reference.get_citation_list())
            ref.set_privacy(reference.get_privacy())
            if reference.get_relation() in _RECIPROCAL_ASSOCIATIONS:
                ref.set_relation(
                    _RECIPROCAL_ASSOCIATIONS[reference.get_relation()]
                )
            callback = lambda x: self._added_reciprocal_person_ref(
                x, reference.ref
            )
            try:
                EditPersonRef(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    ref,
                    callback,
                )
            except WindowActiveError:
                pass

    def _added_reciprocal_person_ref(self, reference, reciprocal_handle):
        """
        Finish adding a reciprocal reference for a person.
        """
        person = GrampsObject(self.fetch("Person", reciprocal_handle))
        message = " ".join(
            (
                _("Added"),
                _("PersonRef"),
                self.primary.obj.get_gramps_id(),
                _("to"),
                _("Person"),
                person.obj.get_gramps_id(),
            )
        )
        person.obj.add_person_ref(reference)
        person.commit(self.grstate, message)

    def remove_association(self, _dummy_obj, person_ref):
        """
        Remove an association.
        """
        person = self.fetch("Person", person_ref.ref)
        text = "".join((name_displayer.display(person),))
        prefix = _(
            "You are about to remove the following association with this "
            "person:"
        )
        extra = _(
            "Note this does not delete the person. You can also use the "
            "undo option under edit if you change your mind later."
        )
        if self.confirm_action(
            _("Warning"), prefix, "\n\n<b>", text, "</b>\n\n", extra
        ):
            new_list = []
            for ref in self.primary.obj.get_person_ref_list():
                if not ref.ref == person_ref.ref:
                    new_list.append(ref)
            message = " ".join(
                (
                    _("Removed"),
                    _("PersonRef"),
                    person.get_gramps_id(),
                    _("from"),
                    _("Person"),
                    self.primary.obj.get_gramps_id(),
                )
            )
            self.primary.obj.set_person_ref_list(new_list)
            self.primary.commit(self.grstate, message)

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

    def _remove_family_parent_option(self):
        """
        Build menu item for removing as parent from a family.
        """
        image = Gtk.Image.new_from_icon_name("list-remove", Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(
            always_show_image=True,
            image=image,
            label=_("Remove parent from this family"),
        )
        item.connect("activate", self.remove_family_parent)
        return item

    def remove_family_parent(self, _dummy_obj):
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
            message = " ".join(
                (
                    _("You are about to remove"),
                    person_name,
                    _("as the partner of"),
                    partner_name,
                    _("and a parent of this family."),
                )
            )
        else:
            message = " ".join(
                (
                    _("You are about to remove"),
                    person_name,
                    _("as a parent of this family."),
                )
            )
        if self.confirm_action(_("Warning"), message):
            self.grstate.dbstate.db.remove_parent_from_family(
                self.primary.obj.get_handle(), self.groptions.backlink
            )

    def _set_preferred_parents_option(self, menu):
        """
        Build menu item to set new preferred parents.
        """
        if self.reference:
            main_parents = self.primary.obj.get_main_parents_family_handle()
            if self.reference_base.obj.get_handle() != main_parents:
                menu.append(
                    menu_item(
                        "gramps-parents-add",
                        _("Make current parents preferred"),
                        self.set_main_parents,
                    )
                )

    def set_main_parents(self, *_dummy_args):
        """
        Set preferred parents.
        """
        message = " ".join(
            (
                _("Setting"),
                _("Family"),
                self.reference_base.obj.get_gramps_id(),
                _("as"),
                _("Main"),
                _("Parents"),
                _("for"),
                _("Person"),
                self.primary.obj.get_gramps_id(),
            )
        )
        self.primary.obj.set_main_parent_family_handle(
            self.reference_base.obj.get_handle()
        )
        self.primary.commit(self.grstate, message)

    def remove_family_child(self, _dummy_obj):
        """
        Remove a child from the family.
        """
        if not self.groptions.backlink:
            return
        person_name = name_displayer.display(self.primary.obj)
        family = self.fetch("Family", self.groptions.backlink)
        family_text = family_name(family, self.grstate.dbstate.db)
        message = " ".join(
            (
                _("You are about to remove"),
                person_name,
                "from the family of",
                family_text,
                ".",
            )
        )
        if self.confirm_action(_("Warning"), message):
            self.grstate.dbstate.db.remove_child_from_family(
                self.primary.obj.get_handle(), self.backlink
            )

    def set_default_person(self, *_dummy_obj):
        """
        Set the default person.
        """
        self.grstate.dbstate.db.set_default_person_handle(
            self.primary.obj.get_handle()
        )

    def edit_person_ref(self, *_dummy_obj):
        """
        Launch the editor.
        """
        try:
            EditPersonRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.reference.obj,
                self.save_ref,
            )
        except WindowActiveError:
            pass
