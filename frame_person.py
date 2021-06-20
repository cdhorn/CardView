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
from gramps.gen.errors import WindowActiveError
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
    get_relation,
    get_key_person_events,
    TextLink,
    format_date_string,
)

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


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
        family_backlink=None
    ):
        GrampsFrame.__init__(self, dbstate, uistate, router, space, config, person, context)
        self.person = person
        self.relation = relation
        self.family_backlink = family_backlink

        if self.option(context, "show-image"):
            self.load_image(groups)
            if self.option(context, "show-image-first"):
                self.body.pack_start(self.image, expand=False, fill=False, padding=0)

        subject_section = Gtk.VBox()
        if groups and "data" in groups:
            groups["data"].add_widget(subject_section)
        self.body.pack_start(subject_section, True, True, 0)

        display_name = name_displayer.display(self.person)
        text = "<b>{}</b>".format(display_name)
        if self.enable_tooltips:
            tooltip = "{} {} {}".format(
                _("Click to view"), display_name, _("or right click to select edit.")
            )
        else:
            tooltip = None
        name = TextLink(
            text, self.person.handle, self.router, "link-person", tooltip=tooltip
        )
        name_box = Gtk.HBox(spacing=2)
        if number:
            label = Gtk.Label(
                use_markup=True, label=self.markup.format("{}. ".format(number))
            )
            name_box.pack_start(label, False, False, 0)
        if self.option(context, "show-gender"):
            label = Gtk.Label(label=_GENDERS[self.person.gender])
            name_box.pack_start(label, False, False, 0)
        name_box.pack_start(name, False, False, 0)
        subject_section.pack_start(name_box, True, True, 0)

        events_section = Gtk.HBox()
        subject_section.pack_start(events_section, True, True, 0)

        key_events = get_key_person_events(
            self.dbstate.db,
            self.person,
            show_baptism=self.option(context, "show-baptism"),
            show_burial=self.option(context, "show-burial"),
        )
        events_section.pack_start(self.facts_grid, True, True, 0)
        self.living = self._load_base_facts(key_events)
        if self.living:
            self.living = probably_alive(self.person, self.dbstate.db)

        relation_section = Gtk.VBox()
        subject_section.pack_start(relation_section, True, True, 0)

        if self.relation and self.option(context, "show-relation"):
            text = ""
            if self.person.handle == self.relation.handle:
                text = _("Home person")
            else:
                text = get_relation(
                    self.dbstate.db,
                    self.person,
                    self.relation,
                    depth=global_config.get("behavior.generation-depth"),
                )
            if text:
                label = self.make_label(text)
                relation_section.pack_start(label, False, False, 0)

        metadata_section = Gtk.VBox()
        if groups and "metadata" in groups:
            groups["metadata"].add_widget(metadata_section)
        self.body.pack_start(metadata_section, False, False, 0)

        gramps_id = self.get_gramps_id_label()
        metadata_section.pack_start(gramps_id, False, False, 0)

        flowbox = self.get_tags_flowbox()
        if flowbox:
            metadata_section.pack_start(flowbox, False, False, 0)

        if self.option(context, "show-image"):
            if not self.option(context, "show-image-first"):
                self.body.pack_start(self.image, expand=False, fill=False, padding=0)

        self.set_css_style()

    def _load_base_facts(self, key_events):
        """
        Load the basic facts about a person.
        """
        living = True
        if key_events["death"] or key_events["burial"]:
            living = False

        if self.option(self.context, "event-format") == 0:
            text = format_date_string(key_events["birth"], key_events["death"])
            label = self.make_label(text)
            self.facts_grid.attach(label, 0, self.facts_row, 1, 1)
            self.facts_row = self.facts_row + 1
            return living

        self.add_event(key_events["birth"])
        if self.option(self.context, "show-baptism"):
            self.add_event(key_events["baptism"])

        if key_events["death"] or key_events["burial"]:
            self.add_event(
                key_events["death"],
                reference=key_events["birth"],
                show_age=self.option(self.context, "show-age"),
            )
            if self.option(self.context, "show-burial"):
                self.add_event(
                    key_events["burial"],
                    reference=key_events["birth"],
                    show_age=self.option(self.context, "show-age"),
                )
        return living

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
        with DbTxn(_("Add person event"), self.dbstate.db) as trans:
            self.person.add_event_ref(reference)
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
        ref = ChildRef()
        ref.ref = self.person.handle
        family.add_child_ref(ref)

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
                return
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
            if not self.confirm_action(
                    "Warning",
                    "You are about to remove {} from the family of {}.\n\nAre you sure you want to continue?".format(person_name, family_text)
            ):
                return
            self.dbstate.db.remove_child_from_family(
                self.person.handle, self.family_backlink
            )

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.config.get(
                "preferences.profile.person.layout.use-color-scheme"
        ):
            return ""
        
        if self.obj.gender == Person.MALE:
            key = "male"
        elif self.obj.gender == Person.FEMALE:
            key = "female"
        else:
            key = "unknown"
        if self.living:
            value = "alive"
        else:
            value = "dead"
        border_color = global_config.get("colors.border-{}-{}".format(key, value))
        if self.relation and self.relation.handle == self.obj.handle:
            key = "home"
            value = "person"
        background_color = global_config.get("colors.{}-{}".format(key, value))

        scheme = global_config.get("colors.scheme")
        css = ""
        if background_color:
            css = "background-color: {};".format(background_color[scheme])
        if border_color:
            css = "{} border-color: {};".format(css, border_color[scheme])
        return css
