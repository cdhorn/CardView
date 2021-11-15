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
EventGrampsFrame.
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
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import EventRef, EventRoleType, Person
from gramps.gen.utils.alive import probably_alive
from gramps.gui.editors import EditEventRef, EditPerson
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import (
    TextLink,
    get_confidence,
    get_confidence_color_css,
    get_event_category,
    get_event_category_color_css,
    get_event_role_color_css,
    get_family_color_css,
    get_participants,
    get_primary_participant,
    get_participants_text,
    get_person_color_css,
    get_relation,
    get_relationship_color_css,
    menu_item,
    submenu_item,
)
from .frame_reference import ReferenceGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# EventGrampsFrame class
#
# ------------------------------------------------------------------------
class EventGrampsFrame(ReferenceGrampsFrame):
    """
    The EventGrampsFrame exposes some of the basic facts about an Event.
    """

    def __init__(
        self,
        grstate,
        groptions,
        event,
        reference_tuple=None,
        groups=None,
    ):
        ReferenceGrampsFrame.__init__(
            self, grstate, groptions, event, reference_tuple=reference_tuple
        )
        self.event_confidence = 0

        if event and event.get_date_object() and groptions.age_base:
            self.load_age(groptions.age_base, event.get_date_object())

        self.participants = get_participants(grstate.dbstate.db, event)
        self.primary_participant = get_primary_participant(self.participants)

        event_type = glocale.translation.sgettext(event.type.xml_str())
        title, role = self._get_title_and_role(
            event_type, self.primary_participant
        )

        name = TextLink(
            title,
            "Event",
            event.get_handle(),
            self.switch_object,
            hexpand=True,
            bold=True,
        )
        self.widgets["title"].pack_start(name, True, True, 0)

        if role:
            if self.get_option("show-role-always") or role not in [
                "Primary",
                "Family",
            ]:
                self.add_fact(self.make_label(str(role)))

        date = glocale.date_displayer.display(event.get_date_object())
        if date:
            self.add_fact(self.make_label(date))

        text = place_displayer.display_event(grstate.dbstate.db, event)
        if text:
            place = TextLink(
                text,
                "Place",
                event.place,
                self.switch_object,
                hexpand=False,
                bold=False,
                markup=self.markup,
            )
            self.add_fact(place)

        if self.get_option("show-description"):
            text = event.get_description()
            if not text:
                text = "{} {} {}".format(
                    event_type, _("of"), self.primary_participant[3]
                )
            self.add_fact(self.make_label(text))

        if self.get_option("show-participants") and len(self.participants) > 1:
            if "active" in self.groptions.option_space:
                self._load_participants()
            else:
                participant_text = get_participants_text(
                    self.participants,
                    primary=self.primary_participant,
                )
                self.add_fact(
                    self.make_label("Participants {}".format(participant_text))
                )

        text = self.get_quality_text()
        if text:
            self.add_fact(self.make_label(text.lower().capitalize()))

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def _get_title_and_role(self, event_type, primary_participant):
        """
        Calculate event title and role if there is a reference person.
        """
        (
            primary_obj_type,
            primary_obj,
            dummy_primary_obj_event_ref,
            primary_obj_name,
        ) = primary_participant

        role = ""
        title = ""
        if (
            self.reference
            and self.reference.obj_type == "Person"
            and primary_obj_type == "Person"
        ):
            if self.reference.obj.get_handle() == primary_obj.get_handle():
                title = event_type
                role = "Primary"
            else:
                relationship = get_relation(
                    self.grstate.dbstate.db,
                    primary_obj,
                    self.reference.obj,
                )
                if relationship:
                    title = "{} {} {}".format(
                        event_type, _("of"), relationship.split()[0].title()
                    )
                    inverse_relationship = get_relation(
                        self.grstate.dbstate.db,
                        self.reference.obj,
                        primary_obj,
                    )
                    role = "{}: {}".format(
                        _("Implicit Family"),
                        inverse_relationship.split()[0].title(),
                    )
        if not title:
            title = "{} {} {}".format(event_type, _("of"), primary_obj_name)
            if self.reference and self.reference.obj_type == "Person":
                for (
                    dummy_var1,
                    obj,
                    obj_event_ref,
                    dummy_var2,
                ) in self.participants:
                    if self.reference.obj.get_handle() == obj.get_handle():
                        role = str(obj_event_ref.get_role())
                        break
        return title, role

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
            self.make_label(primary_obj_name),
            label=self.make_label(str(primary_obj_event_ref.get_role())),
            extra=True,
        )

        roles = []
        for (
            dummy_obj_type,
            obj,
            obj_event_ref,
            obj_name,
        ) in self.participants:
            if obj.get_handle() == primary_obj.get_handle():
                continue
            roles.append((str(obj_event_ref.get_role()), obj_name))
        roles.sort(key=lambda x: x[0])
        for (role, obj_name) in roles:
            self.add_fact(
                self.make_label(obj_name),
                label=self.make_label(role),
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
            text = "{}{}{}".format(text, comma, citation_text)
            comma = ", "
        if self.get_option("show-best-confidence") and confidence_text:
            text = "{}{}{}".format(text, comma, confidence_text)
        return text

    def get_quality_labels(self):
        """
        Generate textual description for confidence, source and citation counts.
        """
        sources = []
        citations = len(self.primary.obj.citation_list)
        if self.primary.obj.get_citation_list():
            for handle in self.primary.obj.get_citation_list():
                citation = self.fetch("Citation", handle)
                if citation.source_handle not in sources:
                    sources.append(citation.source_handle)
                if citation.confidence > self.event_confidence:
                    self.event_confidence = citation.confidence

        if sources:
            if len(sources) == 1:
                source_text = "1 {}".format(_("Source"))
            else:
                source_text = "{} {}".format(len(sources), _("Sources"))
        else:
            source_text = _("No Sources")

        if citations:
            if citations == 1:
                citation_text = "1 {}".format(_("Citation"))
            else:
                citation_text = "{} {}".format(citations, _("Citations"))
        else:
            citation_text = _("No Citations")

        return (
            source_text,
            citation_text,
            get_confidence(self.event_confidence),
        )

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.grstate.config.get("options.global.use-color-scheme"):
            return ""

        scheme = self.get_option("color-scheme")
        if scheme == 1:
            return get_relationship_color_css(
                self.relation_to_reference, self.grstate.config
            )
        if scheme == 2:
            return get_event_role_color_css(
                self.role_type, self.grstate.config
            )
        if scheme == 3:
            category = get_event_category(self.primary.obj)
            return get_event_category_color_css(category, self.grstate.config)
        if scheme == 4:
            return get_confidence_color_css(
                self.event_confidence, self.grstate.config
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

    def add_custom_actions(self, action_menu):
        """
        Add action menu items for the event.
        """
        action_menu.append(self._participants_option())

    def edit_self(self, *_dummy_obj):
        """
        Launch the desired editor based on object type.
        """
        if self.event_person.handle == self.reference_person.handle:
            if self.event_ref.get_role().is_family():
                callback = self.update_family_event
            else:
                callback = self.update_person_event
            try:
                EditEventRef(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    self.event,
                    self.event_ref,
                    callback,
                )
            except WindowActiveError:
                pass
            return
        try:
            self.primary.obj_edit(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.primary.obj,
            )
        except WindowActiveError:
            pass

    def update_person_event(self, event_ref, *_dummy_var1):
        """
        Commit person to save an event reference update.
        """
        event = self.fetch("Event", event_ref.ref)
        action = "{} {} {} {} {} {}".format(
            _("Update"),
            _("Person"),
            self.event_person.get_gramps_id(),
            _("Event"),
            event.get_gramps_id(),
            _("Reference"),
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.grstate.dbstate.db.commit_person(self.event_person, trans)

    def update_family_event(self, event_ref, *_dummy_var1):
        """
        Commit family to save an event reference update.
        """
        event = self.fetch("Event", event_ref.ref)
        action = "{} {} {} {} {} {}".format(
            _("Update"),
            _("Family"),
            self.event_family.get_gramps_id(),
            _("Event"),
            event.get_gramps_id(),
            _("Reference"),
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.grstate.dbstate.db.commit_family(self.event_family, trans)

    def _participants_option(self):
        """
        Build participants option menu.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item(
                "gramps-person",
                _("Add a new person as a participant"),
                self.add_new_participant,
            )
        )
        menu.add(
            menu_item(
                "gramps-person",
                _("Add an existing person as a participant"),
                self.add_existing_participant,
            )
        )
        if len(self.participants) > 1:
            gotomenu = Gtk.Menu()
            menu.add(
                submenu_item(
                    "gramps-person", _("Go to a participant"), gotomenu
                )
            )
            editmenu = Gtk.Menu()
            menu.add(
                submenu_item(
                    "gramps-person", _("Edit a participant"), editmenu
                )
            )
            removemenu = Gtk.Menu()
            removesubmenu = submenu_item(
                "gramps-person", _("Remove a participant"), removemenu
            )
            menu.add(removesubmenu)
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            participant_list = []
            for (obj_type, obj, obj_event_ref, obj_name) in self.participants:
                if obj_type == "Person":
                    text = "{}: {}".format(
                        str(obj_event_ref.get_role()), obj_name
                    )
                    participant_list.append((text, obj, obj_event_ref))
            participant_list.sort(key=lambda x: x[0])
            for (text, person, event_ref) in participant_list:
                handle = person.get_handle()
                gotomenu.add(
                    menu_item("gramps-person", text, self.goto_person, handle)
                )
                editmenu.add(
                    menu_item(
                        "gramps-person",
                        text,
                        self.edit_primary_object,
                        person,
                        "Person",
                    )
                )
                removemenu.add(
                    menu_item(
                        "list-remove",
                        text,
                        self.remove_participant,
                        person,
                        event_ref,
                    )
                )
                menu.add(
                    menu_item(
                        "gramps-person",
                        text,
                        self.edit_participant,
                        person,
                        event_ref,
                    )
                )
            if len(removemenu) == 0:
                removesubmenu.destroy()
        return submenu_item("gramps-person", _("Participants"), menu)

    def edit_participant(self, _dummy_obj, person, event_ref):
        """
        Edit the event participant refererence.
        """
        if self.event_ref.get_role().is_family():
            callback = self.update_family_event
        else:
            callback = self.update_participant_event
        try:
            self.event_participant = person
            EditEventRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.event,
                event_ref,
                callback,
            )
        except WindowActiveError:
            pass

    def update_participant_event(self, event_ref, event):
        """
        Save the event participant to save any update.
        """
        if self.event_participant:
            event = self.fetch("Event", event_ref.ref)
            action = "{} {} {} {} {}".format(
                _("Update Participant"),
                self.event_family.get_gramps_id(),
                _("Event"),
                event.get_gramps_id(),
                _("Reference"),
            )
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.grstate.dbstate.db.commit_person(
                    self.event_participant, trans
                )

    def add_new_participant(self, _dummy_obj):
        """
        Add a new person as participant to an event.
        """
        person = Person()
        event_ref = EventRef()
        event_ref.ref = self.event.handle
        event_ref.set_role(EventRoleType(EventRoleType.UNKNOWN))
        person.add_event_ref(event_ref)
        try:
            EditPerson(self.grstate.dbstate, self.grstate.uistate, [], person)
        except WindowActiveError:
            pass

    def add_existing_participant(self, _dummy_obj):
        """
        Add an existing person as participant to an event.
        """
        select_person = SelectorFactory("Person")
        dialog = select_person(self.grstate.dbstate, self.grstate.uistate)
        person = dialog.run()
        if person:
            event_ref = EventRef()
            event_ref.ref = self.event.handle
            event_ref.set_role(EventRoleType(EventRoleType.UNKNOWN))
            person.add_event_ref(event_ref)
            if self.event_ref.get_role().is_primary():
                callback = self.update_participant_event
            elif self.event_ref.get_role().is_family():
                callback = self.update_family_event
            else:
                callback = self.update_participant_event
            self.event_participant = person
            try:
                EditEventRef(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    self.event,
                    event_ref,
                    callback,
                )
            except WindowActiveError:
                pass

    def remove_participant(self, _dummy_obj, person, event_ref):
        """
        Remove a participant from an event.
        """
        name = name_displayer.display(person)
        role = str(event_ref.get_role())
        text = "{}: {}".format(role, name)
        prefix = _(
            "You are about to remove the following participant from this event:"
        )
        extra = _(
            "Note this does not delete the event or the participant. You can "
            "also use the undo option under edit if you change your mind later."
        )
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"),
            "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm),
        ):
            new_list = []
            for ref in person.get_event_ref_list():
                if not event_ref.is_equal(ref):
                    new_list.append(ref)
            event = self.fetch("Event", event_ref.ref)
            action = "{} {} {} {} {} {}".format(
                _("Remove"),
                _("Person"),
                person.get_gramps_id(),
                _("Event"),
                event.get_gramps_id(),
                _("Reference"),
            )
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                person.set_event_ref_list(new_list)
                self.grstate.dbstate.db.commit_person(person, trans)
