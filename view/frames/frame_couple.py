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


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_const import _MARRIAGE_EQUIVALENTS, _DIVORCE_EQUIVALENTS
from .frame_primary import PrimaryGrampsFrame
from .frame_person import PersonGrampsFrame
from .frame_utils import TextLink, get_family_color_css, get_key_family_events

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
        PrimaryGrampsFrame.__init__(self, grstate, groptions, family)
        self.divorced = False
        self.family = family
        self.relation = groptions.relation

        self.parent1, self.parent2 = self._get_parents()
        profile = self._get_profile(self.parent1)
        if profile:
            self.partner1.add(profile)
        if self.parent2:
            profile = self._get_profile(self.parent2)
            if profile:
                self.partner2.add(profile)

        if self.family.type:
            title = TextLink(
                str(self.family.type),
                "Family",
                family.handle,
                self.switch_object,
                bold=True,
            )
            self.title.pack_start(title, True, True, 0)

        event_cache = []
        for event_ref in family.get_event_ref_list():
            event_cache.append(
                grstate.dbstate.db.get_event_from_handle(event_ref.ref)
            )
        if "active" in groptions.option_space:
            anchor = "options.active.family"
        else:
            anchor = "options.group.family"
        self.load_fields(event_cache, anchor, "facts-field")
        if "active" in groptions.option_space:
            self.load_fields(event_cache, anchor, "extra-field", extra=True)
        del event_cache

        self.show_all()
        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def build_layout(self):
        """
        Construct framework for couple layout, overrides base class.
        """
        vcontent = Gtk.VBox(spacing=3)
        self.body.pack_start(vcontent, expand=True, fill=True, padding=0)
        if self.groptions.vertical_orientation:
            self.partner1 = Gtk.HBox(hexpand=True)
            vcontent.pack_start(
                self.partner1, expand=True, fill=True, padding=0
            )
            vcontent.pack_start(
                self.eventbox, expand=True, fill=True, padding=0
            )
            self.partner2 = Gtk.HBox(hexpand=True)
            vcontent.pack_start(
                self.partner2, expand=True, fill=True, padding=0
            )
        else:
            group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
            partners = Gtk.HBox(hexpand=True, spacing=3)
            vcontent.pack_start(partners, expand=True, fill=True, padding=0)
            self.partner1 = Gtk.HBox(hexpand=True)
            group.add_widget(self.partner1)
            if "partner1" in self.groptions.size_groups:
                self.groptions.size_groups["partner1"].add_widget(self.partner1)
            partners.pack_start(
                self.partner1, expand=True, fill=True, padding=0
            )
            self.partner2 = Gtk.HBox(hexpand=True)
            group.add_widget(self.partner2)
            if "partner2" in self.groptions.size_groups:
                self.groptions.size_groups["partner2"].add_widget(self.partner2)
            partners.pack_start(
                self.partner2, expand=True, fill=True, padding=0
            )
            vcontent.pack_start(
                self.eventbox, expand=True, fill=True, padding=0
            )
        data_content = Gtk.HBox()
        self.eventbox.add(data_content)
        if "active" in self.groptions.option_space:
            image_mode = self.get_option("options.active.family.image-mode")
        else:
            image_mode = self.get_option("options.group.family.image-mode")
        if image_mode and image_mode in [3, 4]:
            data_content.pack_start(
                self.image, expand=False, fill=False, padding=0
            )
        title_box = Gtk.VBox()
        title_box.pack_start(self.title, expand=True, fill=True, padding=0)
        fact_box = Gtk.HBox()
        fact_box.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
        fact_box.pack_start(self.extra_grid, expand=True, fill=True, padding=0)
        title_box.pack_start(fact_box, expand=True, fill=True, padding=0)
        tag_box = Gtk.HBox(hexpand=False, vexpand=False)
        tag_box.pack_start(self.tags, False, False, 0)
        title_box.pack_start(tag_box, expand=True, fill=True, padding=0)
        data_content.pack_start(title_box, expand=True, fill=True, padding=0)
        data_content.pack_start(
            self.metadata, expand=True, fill=True, padding=0
        )
        if image_mode in [1, 2]:
            data_content.pack_start(
                self.image, expand=False, fill=False, padding=0
            )

    def load_fields(self, event_cache, anchor, field_type, extra=False):
        """
        Parse and load a set of facts about a couple.
        """
        key = "{}.{}-skip-marriage-alternates".format(anchor, field_type)
        skip_marriage_alternates = self.get_option(key)
        key = "{}.{}-skip-divorce-alternates".format(anchor, field_type)
        skip_divorce_alternates = self.get_option(key)
        have_marriage = False
        have_divorce = False
        for event in event_cache:
            if event.get_type().xml_str() == "Marriage":
                have_marriage = event
            elif event.get_type().xml_str() == "Divorce":
                have_divorce = event
                self.divorced = True

        count = 1
        while count < 8:
            option = self.get_option(
                "{}.{}-{}".format(anchor, field_type, count),
                full=False,
                keyed=True,
            )
            if option and option[0] != "None" and len(option) > 1 and option[1]:
                if len(option) >= 3:
                    show_all = bool(option[2] == "True")
                if option[0] == "Event":
                    self.add_field_for_event(
                        event_cache,
                        option[1],
                        extra=extra,
                        show_all=show_all,
                        skip_marriage=skip_marriage_alternates,
                        have_marriage=have_marriage,
                        skip_divorce=skip_divorce_alternates,
                        have_divorce=have_divorce,
                    )
                elif option[0] == "Fact":
                    self.add_field_for_fact(
                        event_cache, option[1], extra=extra, show_all=show_all
                    )
                elif option[0] == "Attribute":
                    self.add_field_for_attribute(
                        option[1], extra=extra, show_all=show_all
                    )
            count = count + 1

    def add_field_for_event(
        self,
        event_cache,
        event_type,
        extra=False,
        show_all=False,
        skip_marriage=False,
        have_marriage=None,
        skip_divorce=False,
        have_divorce=None,
    ):
        """
        Find an event and load the data.
        """
        show_age = False
        for event in event_cache:
            if event.get_type().xml_str() == event_type:
                if skip_marriage and have_marriage:
                    if event_type in _MARRIAGE_EQUIVALENTS:
                        return
                if skip_divorce and have_divorce:
                    if event_type in _DIVORCE_EQUIVALENTS:
                        return
                if (
                    event_type in _DIVORCE_EQUIVALENTS
                    or event_type == "Divorce"
                ):
                    if "active" in self.groptions.option_space:
                        show_age = self.get_option(
                            "options.active.family.show-years"
                        )
                    else:
                        show_age = self.get_option(
                            "options.group.family.show-years"
                        )
                    self.divorced = True
                self.add_event(
                    event,
                    extra=extra,
                    reference=have_marriage,
                    show_age=show_age,
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

    def get_metadata_attributes(self):
        """
        Return a list of values for any user defined metadata attributes.
        """
        values = []
        number = 1
        if "active" in self.groptions.option_space:
            prefix = "options.active.family"
        else:
            prefix = "options.group.family"
        while number <= 8:
            option = self.get_option(
                "{}.metadata-attribute-{}".format(prefix, number),
                full=False,
                keyed=True,
            )
            if (
                option
                and option[0] == "Attribute"
                and len(option) >= 2
                and option[1]
            ):
                for attribute in self.primary.obj.get_attribute_list():
                    if attribute.get_type().xml_str() == option[1]:
                        if attribute.get_value():
                            values.append(attribute.get_value())
                        break
            number = number + 1
        return values

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
            father = self.grstate.dbstate.db.get_person_from_handle(
                self.family.get_father_handle()
            )
        mother = None
        if self.family.get_mother_handle():
            mother = self.grstate.dbstate.db.get_person_from_handle(
                self.family.get_mother_handle()
            )

        partner1 = father
        partner2 = mother
        if "active" in self.groptions.option_space:
            matrilineal = self.get_option(
                "options.active.family.show-matrilineal"
            )
            spouse_only = False
        else:
            matrilineal = self.get_option(
                "options.group.family.show-matrilineal"
            )
            spouse_only = self.get_option(
                "options.group.family.show-spouse-only"
            )
        if matrilineal:
            partner1 = mother
            partner2 = father
        if (
            "spouse" in self.groptions.option_space
            and "group" in self.groptions.option_space
            and spouse_only
            and self.relation
        ):
            if (
                partner1
                and partner1.handle == self.relation.handle
                or not partner1
            ):
                partner1 = partner2
            partner2 = None
        return partner1, partner2

    def add_custom_actions(self):
        """
        Add action menu items for the person based on the context in which
        they are present in relation to the active person.
        """
        if (
            "parent" in self.groptions.option_space
            or "spouse" in self.groptions.option_space
        ):
            self.action_menu.append(self._add_new_family_event_option())
            self.action_menu.append(self._add_new_child_to_family_option())
            self.action_menu.append(self._add_existing_child_to_family_option())

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.grstate.config.get("options.global.use-color-scheme"):
            return ""

        return get_family_color_css(self.primary.obj, divorced=self.divorced)
