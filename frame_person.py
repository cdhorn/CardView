#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
PersonProfileFrame
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk, Gdk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import EventType, Person, Family, Event, Span, ChildRef, EventRef, EventRoleType, Name, Surname
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.db import preset_name
from gramps.gui.editors import EditPerson, EditFamily, EditEvent, EditEventRef
from gramps.gui.selectors import SelectorFactory


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_image import ImageFrame
from frame_base import BaseProfile
from frame_utils import (
    _GENDERS, 
    get_relation, get_key_person_events,
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
# PersonProfileFrame class
#
# ------------------------------------------------------------------------
class PersonProfileFrame(Gtk.Frame, BaseProfile):
    """
    The PersonProfileFrame is intended to provide a summary of the core
    information about an individual. At a minimum this is their name,
    birth and death information. Their image is handled separately to
    better accomodate composite layouts.
    """

    def __init__(self, dbstate, uistate, person, context, space, config, router, relation=None, number=0, group=None):
        Gtk.Frame.__init__(self, hexpand=True, vexpand=False, shadow_type=Gtk.ShadowType.NONE)
        BaseProfile.__init__(self, dbstate, uistate, space, config, router)
        self.obj = person
        self.person = person
        self.context = context        
        self.relation = relation
        self.family_backlink_handle = None

        if context in ["family", "parent", "spouse"]:
            self.sections = Gtk.HBox(margin_right=0, margin_left=0, margin_top=0, margin_bottom=0, spacing=2, hexpand=True, expand=True)
        else:
            self.sections = Gtk.HBox(margin_right=3, margin_left=3, margin_top=3, margin_bottom=3, spacing=2, hexpand=True, expand=True)

        self.event_box = Gtk.EventBox()
        self.event_box.add(self.sections)
        self.event_box.connect('button-press-event', self.build_action_menu)
        self.add(self.event_box)
        
        if self.option(context, "show-image"):
            self.image = ImageFrame(self.dbstate.db,
                                    self.uistate, self.person,
                                    size=bool(self.option(context, "show-image-large")))
            if group:
                group.add_widget(self.image)
            if self.option(context, "show-image-first"):
                self.sections.pack_start(self.image, expand=False, fill=False, padding=0)
                
        subject_section = Gtk.VBox()
        self.sections.pack_start(subject_section, True, True, 0)

        display_name = name_displayer.display(self.person)
        text = "<b>{}</b>".format(display_name)
        if self.enable_tooltips:
            tooltip = "{} {} {}".format(_("Click to view"), display_name, _("or right click to select edit."))
        else:
            tooltip = None
        name = TextLink(text, self.person.handle, self.router, "link-person", tooltip=tooltip)
        name_box = Gtk.HBox(spacing=2)
        if number:
            label = Gtk.Label(use_markup=True, label=self.markup.format("{}. ".format(number)))
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

        home = False
        if self.relation and self.option(context, "show-relation"):
            text = ""
            if self.person.handle == self.relation.handle:
                text = _("Home person")
                home = True
            else:
                text = get_relation(self.dbstate.db, self.person, self.relation, depth=global_config.get("behavior.generation-depth"))
            if text:
                label = self.make_label(text)
                relation_section.pack_start(label, False, False, 0)

        metadata_section = Gtk.VBox()
        self.sections.pack_start(metadata_section, False, False, 0)

        gramps_id = self.get_gramps_id_label()
        metadata_section.pack_start(gramps_id, False, False, 0)

        flowbox = self.get_tags_flowbox()
        if flowbox:
            metadata_section.pack_start(flowbox, False, False, 0)
        
        if self.option(context, "show-image"):
            if not self.option(context, "show-image-first"):
                self.sections.pack_start(self.image, expand=False, fill=False, padding=0)

    def _load_base_facts(self, key_events):
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
            self.add_event(key_events["death"], reference=key_events["birth"], show_age=self.option(self.context, "show-age"))
            if self.option(self.context, "show-burial"):
                self.add_event(key_events["burial"], reference=key_events["birth"], show_age=self.option(self.context, "show-age"))
        return living

    def add_custom_actions(self):
        if self.context in ["active"]:
            self.action_menu.append(self._add_new_person_event_option())
        if self.context in ["parent", "spouse"]:
            self.action_menu.append(self._add_new_family_event_option())
        if self.context in ["active"]:            
            self.action_menu.append(self._add_new_parents_option())
            self.action_menu.append(self._add_existing_parents_option())
            self.action_menu.append(self._add_new_spouse_option())
        if self.context in ["sibling", "child"]:
            self.action_menu.append(self._remove_existing_parent_family_option())
        if self.context in ["parent", "spouse"]:
            self.action_menu.append(self._add_new_child_to_family_option())
            self.action_menu.append(self._add_existing_person_to_family_option())
            self.action_menu.append(self._remove_existing_partner_family_option())

    def _add_new_parents_option(self):
        image = Gtk.Image.new_from_icon_name('gramps-parents-add', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Add a new set of parents"))
        item.connect('activate', self.add_new_parents)
        return item

    def add_new_parents(self, *obj):
        family = Family()
        ref = ChildRef()
        ref.ref = self.person.handle
        family.add_child_ref(ref)

        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass
    
    def _add_existing_parents_option(self):
        image = Gtk.Image.new_from_icon_name('gramps-parents-open', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Add person as child to an existing family"))
        item.connect('activate', self.add_existing_parents)
        return item

    def add_existing_parents(self, *obj):
        SelectFamily = SelectorFactory('Family')
        skip = set(self.person.get_family_handle_list())
        dialog = SelectFamily(self.dbstate, self.uistate, skip=skip)
        family = dialog.run()
        if family:
            self.dbstate.db.add_child_to_family(family, self.person)

    def _add_new_spouse_option(self):
        image = Gtk.Image.new_from_icon_name('gramps-spouse', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Add a new family with person as parent"))
        item.connect('activate', self.add_new_spouse)
        return item

    def add_new_spouse(self, *obj):
        family = Family()
        if self.person.gender == Person.MALE:
            family.set_father_handle(self.person.handle)
        else:
            family.set_mother_handle(self.person.handle)

        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def _remove_existing_partner_family_option(self, spouse=False):
        image = Gtk.Image.new_from_icon_name('list-remove', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Remove parent from this family"))
        item.connect('activate', self.remove_existing_partner_family)
        return item
        
    def remove_existing_partner_family(self, obj):
        if self.family_backlink_handle:
            self.dbstate.db.remove_parent_from_family(self.person.handle, self.family_backlink_handle)

    def _remove_existing_parent_family_option(self):
        image = Gtk.Image.new_from_icon_name('list-remove', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Remove child from this family"))
        item.connect('activate', self.remove_existing_parent_family)
        return item

    def remove_existing_parent_family(self, obj):
        if self.family_backlink_handle:
            self.dbstate.db.remove_child_from_family(self.person.handle, self.person.family_backlink_handle)

    def _add_new_person_event_option(self):
        image = Gtk.Image.new_from_icon_name('gramps-event', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Add a new person event"))
        item.connect('activate', self.add_new_person_event)
        return item

    def add_new_person_event(self, obj):
        event = Event()
        ref = EventRef()
        ref.ref = self.person.handle

        try:
            EditEventRef(self.dbstate, self.uistate, [], event, ref, self.added_new_person_event)
        except WindowActiveError:
            pass

    def added_new_person_event(self, reference, primary):
        with DbTxn(_("Add person event"), self.dbstate.db) as trans:
            self.person.add_event_ref(reference)
            self.dbstate.db.commit_person(self.person, trans)

    def _add_new_family_event_option(self):
        image = Gtk.Image.new_from_icon_name('gramps-event', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Add a new family event"))
        item.connect('activate', self.add_new_family_event)
        return item

    def add_new_family_event(self, obj):
        event = Event()
        event.set_type(EventType(EventType.MARRIAGE))
        ref = EventRef()
        ref.set_role(EventRoleType(EventRoleType.FAMILY))
        ref.ref = self.family_backlink_handle

        try:
            EditEventRef(self.dbstate, self.uistate, [], event, ref, self.added_new_family_event)
        except WindowActiveError:
            pass

    def added_new_family_event(self, reference, primary):
        family = self.dbstate.db.get_family_from_handle(self.family_backlink_handle)
        with DbTxn(_("Add family event"), self.dbstate.db) as trans:
            family.add_event_ref(reference)
            self.dbstate.db.commit_family(family, trans)

    def _add_new_child_to_family_option(self):
        image = Gtk.Image.new_from_icon_name('gramps-person', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Add a new child to the family"))
        item.connect('activate', self.add_new_child_to_family)
        return item

    def add_new_child_to_family(self, *obj):
        handle = self.family_backlink_handle
        callback = lambda x: self.callback_add_child(x, handle)
        person = Person()
        name = Name()
        #the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        family = self.dbstate.db.get_family_from_handle(self.family_backlink_handle)
        father = self.dbstate.db.get_person_from_handle(family.get_father_handle())
        if father:
            preset_name(father, name)
        else:
            mother = self.dbstate.db.get_person_from_handle(family.get_mother_handle())
            preset_name(father, name)
        person.set_primary_name(name)
        try:
            EditPerson(self.dbstate, self.uistate, [], person, callback=callback)
        except WindowActiveError:
            pass

    def callback_add_child(self, person, family_handle):
        ref = ChildRef()
        ref.ref = person.get_handle()
        family = self.dbstate.db.get_family_from_handle(family_handle)
        family.add_child_ref(ref)

        with DbTxn(_("Add Child to Family"), self.dbstate.db) as trans:
            #add parentref to child
            person.add_parent_family_handle(family_handle)
            #default relationship is used
            self.dbstate.db.commit_person(person, trans)
            #add child to family
            self.dbstate.db.commit_family(family, trans)

    def _add_existing_person_to_family_option(self):
        image = Gtk.Image.new_from_icon_name('gramps-person', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Add an existing person to the family as a child"))
        item.connect('activate', self.add_existing_person_to_family)
        return item

    def add_existing_person_to_family(self, *obj):
        SelectPerson = SelectorFactory('Person')
        handle = self.family_backlink_handle
        family = self.dbstate.db.get_family_from_handle(handle)
        # it only makes sense to skip those who are already in the family
        skip_list = [family.get_father_handle(),
                     family.get_mother_handle()]
        skip_list.extend(x.ref for x in family.get_child_ref_list())

        selector = SelectPerson(self.dbstate, self.uistate, [],
                                _("Select Child"), skip=skip_list)
        person = selector.run()
        if person:
            self.callback_add_child(person, handle)
