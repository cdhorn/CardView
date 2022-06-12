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
EventCard.
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.lib import EventType
from gramps.gen.utils.alive import probably_alive
from gramps.gui.ddtargets import DdTargets

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..common.common_utils import (
    get_confidence,
    get_confidence_color_css,
    get_event_category_color_css,
    get_event_role_color_css,
    get_family_color_css,
    get_person_color_css,
    get_relationship_color_css,
)
from ..common.common_strings import NONE, UNKNOWN, UNTITLED
from ..common.common_vitals import (
    check_multiple_events,
    get_event_category,
    get_participants,
    get_participants_text,
    get_primary_participant,
    get_relation,
)
from ..menus.menu_utils import add_participants_menu, menu_item
from .card_reference import ReferenceCard

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# EventCard Class
#
# ------------------------------------------------------------------------
class EventCard(ReferenceCard):
    """
    The EventCard exposes some of the basic facts about an Event.
    """

    def __init__(
        self,
        grstate,
        groptions,
        event,
        reference_tuple=None,
    ):
        ReferenceCard.__init__(
            self, grstate, groptions, event, reference_tuple=reference_tuple
        )
        self.event_confidence = 0
        self.event_role_type = "primary"
        self.event_relationship = "self"
        self.__add_event_age(event)
        self.participants = get_participants(grstate.dbstate.db, event)
        self.primary_participant = get_primary_participant(self.participants)
        event_type = glocale.translation.sgettext(event.type.xml_str())
        title, role = self._get_title_and_role(
            event_type, self.primary_participant
        )
        self.__add_event_title(event, title)
        self.__add_event_role(role)
        self.__add_event_date(event)
        self.__add_event_place(event)
        self.__add_event_description(event, event_type)
        self.__add_event_participants()
        self.__add_event_quality()
        self.enable_drag()
        self.dnd_drop_targets.append(DdTargets.PERSON_LINK.target())
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_event_title(self, event, title):
        """
        Add event title.
        """
        name = self.get_link(
            title,
            "Event",
            event.handle,
            hexpand=True,
        )
        self.widgets["title"].pack_start(name, True, True, 0)

    def __add_event_role(self, role):
        """
        Add event role.
        """
        if role and (
            self.get_option("show-role-always")
            or role
            not in [
                "Primary",
                "Family",
            ]
        ):
            self.add_fact(self.get_label(str(role)))

    def __add_event_age(self, event):
        """
        Load age data if needed.
        """
        event_date = event.get_date_object()
        age_base = self.groptions.age_base
        if event_date and age_base:
            if self.groptions.context in ["timeline"]:
                if self.grstate.config.get("timeline.person.show-age"):
                    self.load_age(age_base, event_date)
            elif self.grstate.config.get("group.event.show-age"):
                self.load_age(age_base, event_date)

    def __add_event_date(self, event):
        """
        Add event date.
        """
        date = glocale.date_displayer.display(event.get_date_object())
        if date:
            self.add_fact(self.get_label(date))

    def __add_event_place(self, event):
        """
        Add event place.
        """
        name = place_displayer.display_event(self.grstate.dbstate.db, event)
        if name:
            place = self.get_link(
                name,
                "Place",
                event.place,
                hexpand=False,
                title=False,
            )
            self.add_fact(place)

    def __add_event_description(self, event, event_type):
        """
        Add event description.
        """
        if self.get_option("show-description"):
            text = event.description
            if not text and self.primary_participant:
                text = "%s %s %s" % (
                    event_type,
                    _("of"),
                    self.primary_participant[3],
                )
            elif not text:
                text = UNKNOWN
            self.add_fact(self.get_label(text))

    def __add_event_participants(self):
        """
        Add event participants.
        """
        if self.get_option("show-participants") and len(self.participants) > 1:
            if "active" in self.groptions.option_space:
                self._load_participants()
            else:
                participant_text = get_participants_text(
                    self.participants,
                    primary=self.primary_participant,
                )
                self.add_fact(
                    self.get_label(
                        "%s %s" % (_("Participants"), participant_text)
                    )
                )

    def __add_event_quality(self):
        """
        Add event quality information.
        """
        text = self.get_quality_text()
        if text:
            self.add_fact(self.get_label(text.lower().capitalize()))

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        if DdTargets.PERSON_LINK.drag_type == dnd_type:
            action = action_handler("Event", self.grstate, self.primary)
            action.add_existing_participant(person_handle=obj_or_handle)
            return True
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def _get_title_and_role(self, event_type, primary_participant):
        """
        Calculate event title and role if there is a reference person.
        """
        if not primary_participant:
            return UNTITLED, NONE
        (
            dummy_primary_obj_type,
            primary_obj,
            primary_obj_event_ref,
            primary_obj_name,
        ) = primary_participant

        if self.reference:
            role = self.reference.obj.get_role()
        else:
            role = primary_obj_event_ref.get_role()
        self.__set_role_type(role)
        role_name = str(role)
        title = "%s %s %s" % (event_type, _("of"), primary_obj_name)
        if self.reference_base:
            if self.reference_base.obj.handle == primary_obj.handle:
                title = self.__adjust_title(title, event_type, primary_obj)
            if (
                self.groptions.relation
                and self.reference_base.obj_type == "Person"
            ):
                relationship = get_relation(
                    self.grstate.dbstate.db,
                    self.reference_base.obj,
                    self.groptions.relation,
                    depth=4,
                )
                if relationship:
                    self.event_role_type = "implicit"
                    self.event_relationship = relationship
                    text = relationship.split()[0].title()
                    title = "%s %s %s" % (event_type, _("of"), text)
                    role_name = "%s: %s" % (_("Implicit Family"), text)
        return title, role_name

    def __set_role_type(self, role):
        """
        Set event role type.
        """
        if role.is_family():
            self.event_role_type = "family"
        elif role.is_primary():
            self.event_role_type = "primary"
        else:
            self.event_role_type = "secondary"
        if "Unknown" in role.xml_str():
            self.event_role_type = "unknown"

    def __adjust_title(self, title, event_type, primary_obj):
        """
        Adjust title if primary event.
        """
        if (
            "family" not in self.groptions.option_space
            and "place" not in self.groptions.option_space
        ):
            title = event_type

            current_type = self.primary.obj.get_type()
            if current_type == EventType.BIRTH and check_multiple_events(
                self.grstate.dbstate.db, primary_obj, EventType.BIRTH
            ):
                birth_ref = primary_obj.get_birth_ref()
                if (
                    birth_ref is not None
                    and birth_ref.ref == self.primary.obj.handle
                ):
                    title = "%s*" % title
            elif current_type == EventType.DEATH and check_multiple_events(
                self.grstate.dbstate.db, primary_obj, EventType.DEATH
            ):
                death_ref = primary_obj.get_death_ref()
                if (
                    death_ref is not None
                    and death_ref.ref == self.primary.obj.handle
                ):
                    title = "%s*" % title
        return title

    def _load_participants(self):
        """
        Load participants data into extra facts fields.
        """
        (
            dummy_primary_obj_type,
            primary_obj,
            primary_obj_event_ref,
            primary_obj_name,
        ) = self.primary_participant
        self.add_fact(
            self.get_label(primary_obj_name),
            label=self.get_label(str(primary_obj_event_ref.get_role())),
            extra=True,
        )

        roles = []
        for (
            dummy_obj_type,
            obj,
            obj_event_ref,
            obj_name,
        ) in self.participants:
            if obj.handle == primary_obj.handle:
                continue
            roles.append((str(obj_event_ref.get_role()), obj_name))
        roles.sort(key=lambda x: x[0])
        for (role, obj_name) in roles:
            self.add_fact(
                self.get_label(obj_name),
                label=self.get_label(role),
                extra=True,
            )

    def get_quality_text(self):
        """
        Generate quality description string.
        """
        source_text, citation_text, confidence_text = self.get_quality_labels()
        text = ""
        comma = ""
        if self.get_option("show-source-count") and source_text:
            text = source_text
            comma = ", "
        if self.get_option("show-citation-count") and citation_text:
            text = "%s%s%s" % (text, comma, citation_text)
            comma = ", "
        if self.get_option("show-best-confidence") and confidence_text:
            text = "%s%s%s" % (text, comma, confidence_text)
        return text

    def get_quality_labels(self):
        """
        Generate textual description for confidence, source and citation counts.
        """
        sources = []
        if self.primary.obj.citation_list:
            for citation_handle in self.primary.obj.citation_list:
                citation = self.fetch("Citation", citation_handle)
                if citation.source_handle not in sources:
                    sources.append(citation.source_handle)
                if citation.confidence > self.event_confidence:
                    self.event_confidence = citation.confidence
        return (
            get_object_text(sources, _("Source"), _("Sources")),
            get_object_text(
                self.primary.obj.citation_list,
                _("Citation"),
                _("Citations"),
            ),
            get_confidence(self.event_confidence),
        )

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.grstate.config.get("display.use-color-scheme"):
            return ""

        scheme = self.get_option("color-scheme")
        if scheme == 1:
            return get_event_role_color_css(
                self.event_role_type, self.grstate.config
            )
        if scheme == 2:
            category = get_event_category(
                self.grstate.dbstate.db, self.primary.obj
            )
            return get_event_category_color_css(category, self.grstate.config)
        if scheme == 3:
            return get_confidence_color_css(
                self.event_confidence, self.grstate.config
            )
        if scheme == 4:
            return get_relationship_color_css(
                self.event_relationship, self.grstate.config
            )

        if self.primary_participant[0] == "Person":
            person = self.primary_participant[1]
        elif self.reference and self.reference.obj_type == "Person":
            person = self.reference_person
        else:
            person = None
        if person:
            living = probably_alive(person, self.grstate.dbstate.db)
            css_string = get_person_color_css(person, living=living)
        else:
            css_string = get_family_color_css(self.primary_participant[1])
        return css_string

    def add_custom_actions(self, context_menu):
        """
        Add action menu items for the event.
        """
        self.__add_birth_menu_option(context_menu)
        self.__add_death_menu_option(context_menu)
        add_participants_menu(
            self.grstate,
            context_menu,
            self.primary,
            self.participants,
        )

    def __add_birth_menu_option(self, context_menu):
        """
        Build set birth option if appropriate.
        """
        if (
            self.primary.obj.get_type() == EventType.BIRTH
            and self.reference_base
            and self.reference_base.obj.handle
            == self.primary_participant[1].handle
            and self.reference_base.obj.get_birth_ref().ref
            != self.primary.obj.handle
        ):
            action = action_handler(
                "Person", self.grstate, self.reference_base, self.primary
            )
            context_menu.append(
                menu_item(
                    "gramps-person",
                    _("Set preferred birth event"),
                    action.set_birth_event,
                )
            )

    def __add_death_menu_option(self, context_menu):
        """
        Build set death option if appropriate.
        """
        if (
            self.primary.obj.get_type() == EventType.DEATH
            and self.reference_base
            and self.reference_base.obj.handle
            == self.primary_participant[1].handle
            and self.reference_base.obj.get_death_ref().ref
            != self.primary.obj.handle
        ):
            action = action_handler(
                "Person", self.grstate, self.reference_base, self.primary
            )
            context_menu.append(
                menu_item(
                    "gramps-person",
                    _("Set preferred death event"),
                    action.set_death_event,
                )
            )


def get_object_text(obj_list, single, plural):
    """
    Return a text string describing a list.
    """
    if obj_list:
        if len(obj_list) == 1:
            text = "1 %s" % single
        else:
            text = "%s %s" % (str(len(obj_list)), plural)
    else:
        text = "%s %s" % (_("No"), plural)
    return text
