#
# Gramps - a GTK+/GNOME based genealogy program
#
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
FamilyFrame
"""

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
from gramps.gen.lib import EventType
from gramps.gen.utils.db import family_name
from gramps.gui.ddtargets import DdTargets

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..common.common_utils import get_family_color_css
from ..menus.menu_utils import (
    add_family_child_options,
    add_family_event_option,
    add_ldsords_menu,
    menu_item,
)
from .frame_person import PersonFrame
from .frame_primary import PrimaryFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# FamilyFrame Class
#
# ------------------------------------------------------------------------
class FamilyFrame(PrimaryFrame):
    """
    The FamilyFrame exposes some of the basic information about a Couple.
    """

    def __init__(
        self,
        grstate,
        groptions,
        family,
    ):
        if "active" in groptions.option_space:
            anchor = "active.family"
        else:
            anchor = "group.family"
        self.compact = grstate.config.get(".".join((anchor, "compact-mode")))
        if groptions.force_compact:
            self.compact = True
        self.partner1 = Gtk.HBox(hexpand=True)
        self.partner2 = Gtk.HBox(hexpand=True)
        PrimaryFrame.__init__(self, grstate, groptions, family)
        self.divorced = False
        self.family = family
        self.relation = groptions.relation
        self.__add_couple_title(family)
        self.__add_couple_facts(anchor, family)
        self.show_all()
        self.enable_drag()
        if not self.parent2 and (
            not family.father_handle or not family.mother_handle
        ):
            self.dnd_drop_targets.append(DdTargets.PERSON_LINK.target())
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_couple_title(self, family):
        """
        Add couple title.
        """
        if family.type:
            title = str(family.type)
        else:
            title = _("Unknown")
        self.parent1, self.parent2 = self._get_parents()
        if not self.compact:
            profile = self._get_profile(self.parent1)
            if profile:
                self.partner1.add(profile)
            if self.parent2:
                profile = self._get_profile(self.parent2)
                if profile:
                    self.partner2.add(profile)
        else:
            title = family_name(family, self.grstate.dbstate.db)
        label = self.get_link(title, "Family", family.handle)
        self.widgets["title"].pack_start(label, True, True, 0)

    def __add_couple_facts(self, anchor, family):
        """
        Add couple facts.
        """
        event_cache = []
        for event_ref in family.event_ref_list:
            event_cache.append(self.fetch("Event", event_ref.ref))
        option_prefix = "".join((anchor, ".lfield-"))
        self.load_fields("facts", option_prefix, event_cache)
        if "active" in self.groptions.option_space:
            option_prefix = "".join((anchor, ".mfield-"))
            self.load_fields("extra", option_prefix, event_cache)
        del event_cache

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        if DdTargets.PERSON_LINK.drag_type == dnd_type:
            action = action_handler(
                "Family", self.grstate, self.primary, obj_or_handle
            )
            action.add_missing_spouse()
            return True
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def build_layout(self):
        """
        Construct framework for couple layout, overrides base class.
        """
        widgets = self.widgets

        vcontent = Gtk.VBox(spacing=3)
        widgets["body"].pack_start(vcontent, True, True, 0)
        if self.compact:
            vcontent.pack_start(self.eventbox, True, True, 0)
        else:
            self.__build_full_layout(vcontent)
        data_content = Gtk.HBox()
        self.eventbox.add(data_content)
        if "active" in self.groptions.option_space:
            image_mode = self.get_option("active.family.image-mode")
        else:
            image_mode = self.get_option("group.family.image-mode")
        if image_mode in [3, 4]:
            data_content.pack_start(widgets["image"], False, False, 0)

        fact_block = Gtk.VBox()
        data_content.pack_start(fact_block, True, True, 0)
        fact_block.pack_start(widgets["title"], True, True, 0)
        fact_section = Gtk.HBox(valign=Gtk.Align.START, vexpand=True)
        fact_section.pack_start(widgets["facts"], True, True, 0)
        if "active" in self.groptions.option_space:
            fact_section.pack_start(widgets["extra"], True, True, 0)
        fact_block.pack_start(fact_section, True, True, 0)
        fact_block.pack_end(widgets["icons"], True, True, 0)

        attribute_block = Gtk.VBox(halign=Gtk.Align.END)
        data_content.pack_start(attribute_block, True, True, 0)
        attribute_block.pack_start(widgets["id"], True, True, 0)
        attribute_block.pack_start(widgets["attributes"], True, True, 0)

        if image_mode in [1, 2]:
            data_content.pack_end(widgets["image"], False, False, 0)

    def __build_full_layout(self, vcontent):
        """
        Build full uncompact layout.
        """
        size_groups = self.groptions.size_groups

        if self.groptions.vertical_orientation:
            vcontent.pack_start(self.partner1, True, True, 0)
            vcontent.pack_start(self.eventbox, True, True, 0)
            vcontent.pack_start(self.partner2, True, True, 0)
        else:
            group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
            partners = Gtk.HBox(hexpand=True, spacing=3)
            vcontent.pack_start(partners, True, True, 0)
            group.add_widget(self.partner1)
            if "partner1" in size_groups:
                size_groups["partner1"].add_widget(self.partner1)
            partners.pack_start(self.partner1, True, True, 0)
            group.add_widget(self.partner2)
            if "partner2" in size_groups:
                size_groups["partner2"].add_widget(self.partner2)
            partners.pack_start(self.partner2, True, True, 0)
            vcontent.pack_start(self.eventbox, True, True, 0)

    def load_fields(self, grid_key, option_prefix, event_cache):
        """
        Parse and load a set of facts about a couple.
        """
        have_marriage, have_divorce = None, None
        for event in event_cache:
            event_type = event.get_type()
            if event_type == EventType.MARRIAGE:
                have_marriage = event
            elif event_type == EventType.DIVORCE:
                have_divorce = event
                self.divorced = True
        args = {
            "event_format": self.get_option("event-format"),
            "event_cache": event_cache,
            "have_marriage": have_marriage,
            "have_divorce": have_divorce,
        }
        key = "".join((option_prefix, "skip-marriage-alternates"))
        args.update({"skip_marriage_alternates": self.get_option(key)})
        key = "".join((option_prefix, "skip-divorce-alternates"))
        args.update({"skip_divorce_alternates": self.get_option(key)})
        self.load_grid(grid_key, option_prefix, args=args)

    def load_attributes(self):
        """
        Load any user defined attributes.
        """
        if "active" in self.groptions.option_space:
            option_prefix = "active.family.rfield-"
        else:
            option_prefix = "group.family.rfield-"
        args = {
            "skip_labels": not self.get_option(
                "".join((option_prefix, "show-labels"))
            )
        }
        self.load_grid("attributes", option_prefix, args)

    def _get_profile(self, person):
        if person:
            self.groptions.set_backlink(self.family.handle)
            profile = PersonFrame(self.grstate, self.groptions, person)
            return profile
        return None

    def _get_parents(self):
        father = None
        if self.family.father_handle:
            father = self.fetch("Person", self.family.father_handle)
        mother = None
        if self.family.mother_handle:
            mother = self.fetch("Person", self.family.mother_handle)

        if self.groptions.maternal_mode:
            partner1, partner2 = mother, father
            if not partner1:
                partner1, partner2 = father, None
        else:
            partner1, partner2 = father, mother
            if not partner1:
                partner1, partner2 = mother, None
        return partner1, partner2

    def add_custom_actions(self, context_menu):
        """
        Add action menu items for the person based on the context in which
        they are present in relation to the active person.
        """
        if (
            "parent" in self.groptions.option_space
            or "spouse" in self.groptions.option_space
        ):
            action = action_handler("Family", self.grstate, self.primary)
            self._add_partner_options(context_menu)
            add_family_event_option(context_menu, action)
            add_family_child_options(context_menu, action)
            add_ldsords_menu(self.grstate, context_menu, self.primary)

    def _add_partner_options(self, context_menu):
        """
        Add partner specific options.
        """
        partner1, partner2 = self._get_parents()
        for partner in [partner1, partner2]:
            if partner:
                name = name_displayer.display(partner)
                if name:
                    action = action_handler("Person", self.grstate, partner)
                    text = " ".join((_("Edit"), name))
                    context_menu.append(
                        menu_item(
                            "gtk-edit",
                            text,
                            action.edit_object,
                        )
                    )
        if not self.grstate.config.get("menu.go-to-person"):
            return
        for partner in [partner1, partner2]:
            if partner:
                name = name_displayer.display(partner)
                if name:
                    text = " ".join((_("Go to"), name))
                    context_menu.append(
                        menu_item(
                            "gramps-person",
                            text,
                            self.goto_person,
                            partner.handle,
                        )
                    )

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if self.grstate.config.get("display.use-color-scheme"):
            return get_family_color_css(
                self.primary.obj, divorced=self.divorced
            )
        return ""
