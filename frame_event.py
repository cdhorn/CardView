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
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Event, EventRef, EventType, EventRoleType, Span, Person
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.utils.alive import probably_alive
from gramps.gui.editors import EditEventRef, EditPerson
from gramps.gui.selectors import SelectorFactory


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import _EDITORS, GrampsFrame
from frame_utils import (
    get_confidence,
    get_confidence_color_css,
    get_event_category_color_css,
    get_key_person_events,
    get_participants,
    get_relation,
    get_person_color_css,
    get_relationship_color_css,
    TextLink,
)

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# EventGrampsFrame class
#
# ------------------------------------------------------------------------
class EventGrampsFrame(GrampsFrame):
    """
    The EventGrampsFrame exposes some of the basic facts about an Event.
    """

    def __init__(
        self,
        dbstate,
        uistate,
        space,
        config,
        router,
        reference_person,
        event,
        event_ref,
        event_person,
        event_family,
        relation_to_reference,
        category=None,
        groups=None,
    ):
        GrampsFrame.__init__(self, dbstate, uistate, router, space, config, event, "timeline", groups=groups)
        self.event = event
        self.event_ref = event_ref
        self.event_category = category
        self.reference_person = reference_person
        self.event_person = event_person
        self.event_family = event_family
        self.relation_to_reference = relation_to_reference
        self.confidence = 0
        self.event_participant = None

        self.enable_drag()
        self.enable_drop()

        if self.option(self.context, "show-age"):
            if reference_person:
                target_person = reference_person
            else:
                target_person = event_person
            try:
                key_events = get_key_person_events(
                    self.dbstate.db, target_person, birth_only=True
                )
                birth = key_events["birth"]

                if birth and birth.date and event.date:
                    span = Span(birth.date, event.date)
                    if span.is_valid():
                        year = event.date.get_year()
                        if birth.handle == event.handle:
                            text = "<b>{}</b>".format(year)
                        else:
                            precision = global_config.get("preferences.age-display-precision")
                            age = str(span.format(precision=precision).strip("()"))
                            text = "<b>{}</b>\n{}".format(year, age.replace(", ", ",\n"))
                        label = Gtk.Label(
                            label=self.markup.format(text),
                            use_markup=True,
                            justify=Gtk.Justification.CENTER,
                        )
                        self.age.pack_start(label, False, False, 0)
            except AttributeError:
                pass

        if event_ref:
            role = self.event_ref.get_role()
        else:
            role = None
        event_type = glocale.translation.sgettext(event.type.xml_str())
        if event_person:
            event_person_name = name_displayer.display(event_person)
        participants = []
        participant_string = ""

        text = event_type
        if (relation_to_reference not in ["self", "", None]):
            text = "{} {} {}".format(event_type, _("of"), relation_to_reference.title())
        elif role and not role.is_primary():
            participant_name = "Unknown"
            participant_handle = ""
            participants, participant_string = get_participants(self.dbstate.db, event)
            for participant_type, participant, participant_event_ref in participants:
                if participant_event_ref.get_role().is_primary():
                    participant_name = name_displayer.display(participant)
                    participant_handle = participant.get_handle()
            if participant_handle:
                text = "{} {} {}".format(event_type, _("of"), participant_name)
        name = TextLink(
            text,
            "Event",
            event.get_handle(),
            self.switch_object,
            hexpand=True,
            bold=True
        )
        self.title.pack_start(name, True, True, 0)

        if (
                (role and not role.is_primary() and not role.is_family()) or
                self.option(self.context, "show-role-always")
        ):
            self.add_fact(self.make_label(str(role)))

        date = glocale.date_displayer.display(event.date)
        if date:
            self.add_fact(self.make_label(date))

        place = place_displayer.display_event(self.dbstate.db, event)
        if place:
            self.add_fact(self.make_label(place))

        if self.option(self.context, "show-description"):
            text = event.get_description()
            if not text:
                text = "{} {} {}".format(event_type, _("of"), event_person_name)
            self.add_fact(self.make_label(text))

        if self.option(self.context, "show-participants"):
            if not participants:
                participants, participant_string = get_participants(self.dbstate.db, event)
            if participant_string and len(participants) > 1:
                self.add_fact(self.make_label("Participants {}".format(participant_string)))

        source_text, citation_text, confidence_text = self.get_quality_labels()
        text = ""
        comma = ""
        if self.option(self.context, "show-source-count") and source_text:
            text = source_text
            comma = ", "
        if self.option(self.context, "show-citation-count") and citation_text:
            text = "{}{}{}".format(text, comma, citation_text)
            comma = ", "
        if self.option(self.context, "show-best-confidence") and confidence_text:
            text = "{}{}{}".format(text, comma, confidence_text)
        if text:
            self.add_fact(self.make_label(text.lower().capitalize()))
        self.set_css_style()
            
    def get_quality_labels(self):
        """
        Generate textual description for confidence, source and citation counts.
        """
        sources = []
        citations = len(self.event.citation_list)
        if self.event.citation_list:
            for handle in self.event.citation_list:
                citation = self.dbstate.db.get_citation_from_handle(handle)
                if citation.source_handle not in sources:
                    sources.append(citation.source_handle)
                if citation.confidence > self.confidence:
                    self.confidence = citation.confidence

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

        return source_text, citation_text, get_confidence(self.confidence)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.config.get(
                "preferences.profile.person.layout.use-color-scheme"
        ):
            return ""

        scheme = self.option("timeline", "color-scheme")
        if scheme == 1:
            return get_relationship_color_css(self.relation_to_reference, self.config)
        if scheme == 2:
            return get_event_category_color_css(self.event_category, self.config)
        if scheme == 3:
            return get_confidence_color_css(self.confidence, self.config)

        if self.event_person:
            living = probably_alive(self.event_person, self.dbstate.db)
        else:
            living = False
        return get_person_color_css(self.event_person, self.config, living=living)

    def add_custom_actions(self):
        """
        Add action menu items for the event.
        """
        self.action_menu.append(self._participants_option())

    def edit_self(self, *obj):
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
                    self.dbstate, self.uistate, [], self.event, self.event_ref, callback
                )
            except WindowActiveError:
                pass
            return
        try:
            _EDITORS[self.obj_type](self.dbstate, self.uistate, [], self.obj)
        except WindowActiveError:
            pass

    def update_person_event(self, event_ref, primary):
        """
        Commit person to save an event reference update.
        """
        event = self.dbstate.db.get_event_from_handle(event_ref.ref)
        action = "{} {} {} {} {}".format(
            _("Update Person"),
            self.event_person.get_gramps_id(),
            _("Event"),
            event.get_gramps_id(),
            _("Reference")
        )
        with DbTxn(action, self.dbstate.db) as trans:
            self.dbstate.db.commit_person(self.event_person, trans)

    def update_family_event(self, event_ref, primary):
        """
        Commit family to save an event reference update.
        """
        event = self.dbstate.db.get_event_from_handle(event_ref.ref)
        action = "{} {} {} {} {}".format(
            _("Update Family"),
            self.event_family.get_gramps_id(),
            _("Event"),
            event.get_gramps_id(),
            _("Reference")
        )
        with DbTxn(action, self.dbstate.db) as trans:
            self.dbstate.db.commit_family(self.event_family, trans)

    def _participants_option(self):
        """
        Build participants option menu.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("gramps-person", _("Add a new person as a participant"), self.add_new_participant))
        menu.add(self._menu_item("gramps-person", _("Add an existing person as a participant"), self.add_existing_participant))
        participants, text = get_participants(self.dbstate.db, self.obj)
        if len(participants) > 1:
            gotomenu = Gtk.Menu()
            menu.add(self._submenu_item("gramps-person", _("Go to a participant"), gotomenu))
            editmenu = Gtk.Menu()
            menu.add(self._submenu_item("gramps-person", _("Edit a participant"), editmenu))
            removemenu = Gtk.Menu()
            removesubmenu = self._submenu_item("gramps-person", _("Remove a participant"), removemenu)
            menu.add(removesubmenu)
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            participant_list = []
            for obj_type, obj, event_ref in participants:
                if obj_type == "Person":
                    name = name_displayer.display(obj)
                    role = str(event_ref.get_role())
                    text = "{}: {}".format(role, name)
                    participant_list.append((text, obj, event_ref))
            participant_list.sort(key=lambda x: x[0])
            for (text, person, event_ref) in participant_list:
                handle = person.get_handle()
                if not self.event_person.handle == handle:
                    gotomenu.add(self._menu_item("gramps-person", text, self.goto_person, handle))
                    editmenu.add(self._menu_item("gramps-person", text, self.edit_object, person, "Person"))
                if not event_ref.get_role().is_primary():
                    removemenu.add(self._menu_item("list-remove", text, self.remove_participant, person, event_ref))
                if not self.event_person.handle == handle:                    
                    menu.add(self._menu_item("gramps-person", text, self.edit_participant, person, event_ref))
            if len(removemenu) == 0:
                removesubmenu.destroy()
        return self._submenu_item("gramps-person", _("Participants"), menu)

    def edit_participant(self, obj, person, event_ref):
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
                self.dbstate, self.uistate, [], self.event, event_ref, callback
            )
        except WindowActiveError:
            pass

    def update_participant_event(self, event_ref, event):
        """
        Save the event participant to save any update.
        """
        if self.event_participant:
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            action = "{} {} {} {} {}".format(
                _("Update Participant"),
                self.event_family.get_gramps_id(),
                _("Event"),
                event.get_gramps_id(),
                _("Reference")
            )
            with DbTxn(action, self.dbstate.db) as trans:
                self.dbstate.db.commit_person(self.event_participant, trans)

    def add_new_participant(self, obj):
        """
        Add a new person as participant to an event.
        """
        person = Person()
        event_ref = EventRef()
        event_ref.ref = self.event.handle
        event_ref.set_role(EventRoleType(EventRoleType.UNKNOWN))
        person.add_event_ref(event_ref)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass
    
    def add_existing_participant(self, obj):
        """
        Add an existing person as participant to an event.
        """
        SelectPerson = SelectorFactory('Person')
        dialog = SelectPerson(self.dbstate, self.uistate)
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
                    self.dbstate, self.uistate, [], self.event, event_ref, callback
                )
            except WindowActiveError:
                pass

    def remove_participant(self, obj, person, event_ref):
        """
        Remove a participant from an event.
        """
        name = name_displayer.display(person)
        role = str(event_ref.get_role())
        text = "{}: {}".format(role, name)        
        prefix = _("You are about to remove the following participant from this event:")
        extra = _("Note this only removes the reference and does not delete the event or the participant. " \
                  "The participant can be added back at a later time.")
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
                _("Warning"),
                "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm)
        ):
            new_list = []
            for ref in person.get_event_ref_list():
                if not event_ref.is_equal(ref):
                    new_list.append(ref)
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            action = "{} {} {} {} {}".format(
                _("Remove Person"),
                person.get_gramps_id(),
                _("Event"),
                event.get_gramps_id(),
                _("Reference")
            )                
            with DbTxn(action, self.dbstate.db) as trans:
                person.set_event_ref_list(new_list)                
                self.dbstate.db.commit_person(person, trans)
