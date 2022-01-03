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
PersonFrame
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
from gramps.gen.utils.alive import probably_alive
from gramps.gui.ddtargets import DdTargets

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..actions import PersonAction
from ..common.common_const import _GENDERS
from ..common.common_utils import get_person_color_css
from ..common.common_vitals import format_date_string
from .frame_reference import ReferenceFrame
from ..menus.menu_utils import (
    menu_item,
    add_associations_menu,
    add_names_menu,
    add_parents_menu,
    add_partners_menu,
    add_person_menu_options,
)

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PersonFrame class
#
# ------------------------------------------------------------------------
class PersonFrame(ReferenceFrame):
    """
    The PersonFrame exposes some of the basic facts about a Person.
    """

    def __init__(self, grstate, groptions, person, reference_tuple=None):
        ReferenceFrame.__init__(
            self, grstate, groptions, person, reference_tuple=reference_tuple
        )
        self.relation = groptions.relation
        self.backlink = groptions.backlink
        self.context = groptions.option_space.split(".")[2]
        self.__add_person_title(person)
        self.__add_person_facts(person)
        if groptions.age_base:
            self.__load_age_at_event()
        self.enable_drag()
        self.dnd_drop_targets.append(DdTargets.EVENT.target())
        self.dnd_drop_targets.append(DdTargets.PERSON_LINK.target())
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_person_title(self, person):
        """
        Add person title.
        """
        display_name = name_displayer.display(person)
        name = self.get_link(
            display_name,
            "Person",
            person.handle,
        )
        name_box = Gtk.HBox(spacing=2)
        if self.groptions.frame_number:
            label = Gtk.Label(
                use_markup=True,
                label=self.detail_markup.format(
                    "".join((str(self.groptions.frame_number), ". "))
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

    def __add_person_facts(self, person):
        """
        Add person facts.
        """
        event_cache = []
        for event_ref in person.get_primary_event_ref_list():
            event_cache.append(self.fetch("Event", event_ref.ref))
        self.birth, self.death, self.living = self.__get_birth_death(
            event_cache
        )
        if self.get_option("event-format") == 0:
            self.__load_years()
        else:
            self.__load_fields("facts", "lfield-", event_cache)
            if "active" in self.groptions.option_space:
                self.__load_fields("extra", "mfield-", event_cache)
        del event_cache

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

    def __load_age_at_event(self):
        """
        Parse and if have birth load age field.
        """
        if self.birth:
            self.load_age(
                self.birth.get_date_object(), self.groptions.age_base
            )

    def __load_years(self):
        """
        Parse and load birth and death dates only.
        """
        text = format_date_string(self.birth, self.death)
        self.add_fact(self.get_label(text))

    def __get_birth_death(self, event_cache):
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

    def __load_fields(self, grid_key, option_prefix, event_cache):
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
        action = PersonAction(self.grstate, self.primary)
        context_menu.append(
            menu_item(
                "go-home",
                _("Set home person"),
                action.set_default_person,
            )
        )
        context_menu.append(
            menu_item(
                "gramps-event",
                _("Add a new primary event"),
                action.add_new_event,
            )
        )
        context_menu.append(
            menu_item(
                "gramps-event",
                _("Add as participant to an existing event"),
                action.add_existing_event,
            )
        )
        if self.groptions.backlink:
            family = self.grstate.dbstate.db.get_family_from_handle(
                self.groptions.backlink
            )
            add_person_menu_options(
                self.grstate, context_menu, self.primary, family, self.context
            )
        add_parents_menu(self.grstate, context_menu, self.primary)
        add_partners_menu(self.grstate, context_menu, self.primary)
        add_associations_menu(self.grstate, context_menu, self.primary)
        add_names_menu(self.grstate, context_menu, self.primary)
