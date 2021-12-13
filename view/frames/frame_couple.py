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
CoupleGrampsFrame
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
from gramps.gen.lib import EventType
from gramps.gui.ddtargets import DdTargets

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import get_family_color_css, menu_item
from .frame_person import PersonGrampsFrame
from .frame_primary import PrimaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# CoupleGrampsFrame class
#
# ------------------------------------------------------------------------
class CoupleGrampsFrame(PrimaryGrampsFrame):
    """
    The CoupleGrampsFrame exposes some of the basic information about a Couple.
    """

    def __init__(
        self,
        grstate,
        groptions,
        family,
    ):
        if "active" in groptions.option_space:
            anchor = "options.active.family"
        else:
            anchor = "options.group.family"
        self.compact = grstate.config.get(".".join((anchor, "compact-mode")))
        if groptions.force_compact:
            self.compact = True

        self.partner1 = Gtk.HBox(hexpand=True)
        self.partner2 = Gtk.HBox(hexpand=True)
        PrimaryGrampsFrame.__init__(self, grstate, groptions, family)
        self.divorced = False
        self.family = family
        self.relation = groptions.relation

        title = _("Unknown")
        if self.family.type:
            title = str(self.family.type)

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
            data = self.get_title()
            if data:
                if "]" in data:
                    title = data.split("]")[1].strip()

        label = self.get_link(title, "Family", family.handle)
        self.widgets["title"].pack_start(label, True, True, 0)

        event_cache = []
        for event_ref in family.get_event_ref_list():
            event_cache.append(self.fetch("Event", event_ref.ref))

        option_prefix = "".join((anchor, ".lfield-"))
        self.load_fields("facts", option_prefix, event_cache)

        if "active" in groptions.option_space:
            option_prefix = "".join((anchor, ".mfield-"))
            self.load_fields("extra", option_prefix, event_cache)
        del event_cache

        self.show_all()
        self.enable_drag()
        if not self.parent2:
            if (
                not family.get_father_handle()
                or not family.get_mother_handle()
            ):
                self.dnd_drop_targets.append(DdTargets.PERSON_LINK.target())
        self.enable_drop()
        self.set_css_style()

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        if DdTargets.PERSON_LINK.drag_type == dnd_type:
            self.add_missing_spouse(obj_or_handle)
            return True
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def build_layout(self):
        """
        Construct framework for couple layout, overrides base class.
        """
        vcontent = Gtk.VBox(spacing=3)
        self.widgets["body"].pack_start(
            vcontent, expand=True, fill=True, padding=0
        )
        if not self.compact:
            if self.groptions.vertical_orientation:
                vcontent.pack_start(
                    self.partner1, expand=True, fill=True, padding=0
                )
                vcontent.pack_start(
                    self.eventbox, expand=True, fill=True, padding=0
                )
                vcontent.pack_start(
                    self.partner2, expand=True, fill=True, padding=0
                )
            else:
                group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
                partners = Gtk.HBox(hexpand=True, spacing=3)
                vcontent.pack_start(
                    partners, expand=True, fill=True, padding=0
                )
                group.add_widget(self.partner1)
                if "partner1" in self.groptions.size_groups:
                    self.groptions.size_groups["partner1"].add_widget(
                        self.partner1
                    )
                partners.pack_start(
                    self.partner1, expand=True, fill=True, padding=0
                )
                group.add_widget(self.partner2)
                if "partner2" in self.groptions.size_groups:
                    self.groptions.size_groups["partner2"].add_widget(
                        self.partner2
                    )
                partners.pack_start(
                    self.partner2, expand=True, fill=True, padding=0
                )
                vcontent.pack_start(
                    self.eventbox, expand=True, fill=True, padding=0
                )
        else:
            vcontent.pack_start(
                self.eventbox, expand=True, fill=True, padding=0
            )
        data_content = Gtk.HBox()
        self.eventbox.add(data_content)
        if "active" in self.groptions.option_space:
            image_mode = self.get_option("options.active.family.image-mode")
        else:
            image_mode = self.get_option("options.group.family.image-mode")
        if image_mode in [3, 4]:
            data_content.pack_start(
                self.widgets["image"], expand=False, fill=False, padding=0
            )

        fact_block = Gtk.VBox()
        data_content.pack_start(fact_block, expand=True, fill=True, padding=0)
        fact_block.pack_start(
            self.widgets["title"], expand=True, fill=True, padding=0
        )
        fact_section = Gtk.HBox(valign=Gtk.Align.START, vexpand=True)
        fact_section.pack_start(
            self.widgets["facts"], expand=True, fill=True, padding=0
        )
        if "active" in self.groptions.option_space:
            fact_section.pack_start(
                self.widgets["extra"], expand=True, fill=True, padding=0
            )
        fact_block.pack_start(fact_section, expand=True, fill=True, padding=0)
        fact_block.pack_end(
            self.widgets["icons"], expand=True, fill=True, padding=0
        )

        attribute_block = Gtk.VBox(halign=Gtk.Align.END)
        data_content.pack_start(
            attribute_block, expand=True, fill=True, padding=0
        )
        attribute_block.pack_start(
            self.widgets["id"], expand=True, fill=True, padding=0
        )
        attribute_block.pack_start(
            self.widgets["attributes"], expand=True, fill=True, padding=0
        )

        if image_mode in [1, 2]:
            data_content.pack_end(
                self.widgets["image"], expand=False, fill=False, padding=0
            )

    def load_fields(self, grid_key, option_prefix, event_cache):
        """
        Parse and load a set of facts about a couple.
        """
        have_marriage, have_divorce = None, None
        for event in event_cache:
            if event.get_type() == EventType.MARRIAGE:
                have_marriage = event
            elif event.get_type() == EventType.DIVORCE:
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
            option_prefix = "options.active.family.rfield-"
        else:
            option_prefix = "options.group.family.rfield-"
        args = {
            "skip_labels": not self.get_option(
                "".join((option_prefix, "show-labels"))
            )
        }
        self.load_grid("attributes", option_prefix, args)

    def _get_profile(self, person):
        if person:
            self.groptions.set_backlink(self.family.handle)
            profile = PersonGrampsFrame(
                self.grstate,
                self.groptions,
                person,
            )
            return profile
        return None

    def _get_parents(self):
        father = None
        if self.family.get_father_handle():
            father = self.fetch("Person", self.family.get_father_handle())
        mother = None
        if self.family.get_mother_handle():
            mother = self.fetch("Person", self.family.get_mother_handle())

        partner1 = father
        partner2 = mother
        if not partner1:
            partner1 = mother
            partner2 = None
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
            self._add_partner_options(context_menu)
            context_menu.append(self._add_new_family_event_option())
            context_menu.append(self._add_new_child_option())
            context_menu.append(self._add_existing_child_option())

    def _add_partner_options(self, context_menu):
        """
        Add partner specific options.
        """
        partner1, partner2 = self._get_parents()
        for partner in [partner1, partner2]:
            if partner:
                name = name_displayer.display(partner)
                if name:
                    text = " ".join((_("Edit"), name))
                    context_menu.append(
                        menu_item(
                            "gtk-edit",
                            text,
                            self.edit_primary_object,
                            partner,
                            "Person",
                        )
                    )

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
                            partner.get_handle(),
                        )
                    )

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.grstate.config.get("options.global.use-color-scheme"):
            return ""

        return get_family_color_css(self.primary.obj, divorced=self.divorced)

    def add_missing_spouse(self, spouse_handle):
        """
        Add missing spouse for the family.
        """
        if not self.primary.obj.get_father_handle():
            self.primary.obj.set_father_handle(spouse_handle)
        elif not self.primary.obj.get_mother_handle():
            self.primary.obj.set_mother_handle(spouse_handle)
        else:
            return
        self.edit_primary_object()
