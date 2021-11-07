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
# Python modules
#
# ------------------------------------------------------------------------
import pickle

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

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
from gramps.gen.utils.db import family_name
from gramps.gui.editors import EditEventRef, EditPerson
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext, GrampsObject
from ..common.common_const import _LEFT_BUTTON, _RIGHT_BUTTON
from ..common.common_utils import (
    TextLink,
    button_activated,
    get_confidence,
    get_confidence_color_css,
    get_event_category_color_css,
    get_event_role_color_css,
    get_participants,
    get_person_color_css,
    get_relation,
    get_relationship_color_css,
    menu_item,
    submenu_item,
)
from .frame_primary import PrimaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# EventGrampsFrame class
#
# ------------------------------------------------------------------------
class EventGrampsFrame(PrimaryGrampsFrame):
    """
    The EventGrampsFrame exposes some of the basic facts about an Event.
    """

    def __init__(
        self,
        grstate,
        groptions,
        reference_person,
        event,
        event_ref,
        event_person,
        event_family,
        relation_to_reference,
        category=None,
        groups=None,
    ):
        PrimaryGrampsFrame.__init__(self, grstate, groptions, event)
        self.reference = GrampsObject(event_ref)
        self.event = event
        self.event_ref = event_ref
        self.event_category = category
        self.reference_person = reference_person
        self.event_person = event_person
        self.event_family = event_family
        self.relation_to_reference = relation_to_reference
        self.confidence = 0
        self.event_participant = None
        self.role_type = "other"

        if event and event.date and groptions.age_base:
            self.load_age(groptions.age_base, event.date)

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
        if relation_to_reference not in ["self", "", None]:
            text = "{} {} {}".format(
                event_type, _("of"), relation_to_reference.title()
            )
        elif not reference_person:
            if event_family:
                text = "{} {} {}".format(
                    event_type,
                    _("of"),
                    family_name(event_family, grstate.dbstate.db),
                )
            elif event_person:
                text = "{} {} {}".format(
                    event_type, _("of"), event_person_name
                )
        elif role:
            if not role.is_primary():
                self.role_type = "secondary"
                participant_name = "Unknown"
                participant_handle = ""
                participants, participant_string = get_participants(
                    grstate.dbstate.db, event
                )
                for (
                    dummy_var1,
                    participant,
                    participant_event_ref,
                ) in participants:
                    if participant_event_ref.get_role().is_primary():
                        participant_name = name_displayer.display(participant)
                        participant_handle = participant.get_handle()
                if participant_handle:
                    text = "{} {} {}".format(
                        event_type, _("of"), participant_name
                    )
            else:
                if role.is_family():
                    self.role_type = "family"
                else:
                    self.role_type = "primary"
        name = TextLink(
            text,
            "Event",
            event.get_handle(),
            self.switch_object,
            hexpand=True,
            bold=True,
        )
        self.widgets["title"].pack_start(name, True, True, 0)

        if (
            role and not role.is_primary() and not role.is_family()
        ) or self.get_option("show-role-always"):
            if self.event_person:
                if (
                    relation_to_reference
                    and relation_to_reference != "self"
                    and reference_person
                ):
                    inverse_relation = get_relation(
                        grstate.dbstate.db, reference_person, event_person
                    )
                    if inverse_relation:
                        self.add_fact(
                            self.make_label(
                                "{}: {}".format(
                                    _("Implicit Family"),
                                    inverse_relation.split()[0].title(),
                                )
                            )
                        )
                    else:
                        self.add_fact(self.make_label(_("Implicit Family")))
                else:
                    self.add_fact(self.make_label(str(role)))

        date = glocale.date_displayer.display(event.date)
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
                if event_person:
                    text = "{} {} {}".format(
                        event_type, _("of"), event_person_name
                    )
                else:
                    text = "{}".format(event_type)
            self.add_fact(self.make_label(text))

        if self.get_option("show-participants"):
            if not participants:
                participants, participant_string = get_participants(
                    grstate.dbstate.db, event
                )
            if participant_string and len(participants) > 1:
                self.add_fact(
                    self.make_label(
                        "Participants {}".format(participant_string)
                    )
                )

        text = self.get_quality_text()
        if text:
            self.add_fact(self.make_label(text.lower().capitalize()))

        if event_ref and self.role_type != "other" or self.event_family:
            if "id" in self.ref_widgets:
                self.ref_widgets["id"].load(
                    event_ref, "EventRef", gramps_id=event.get_gramps_id()
                )
            self.ref_widgets["body"].pack_start(
                self.make_label(str(role)), False, False, 0
            )

            if "indicators" in self.ref_widgets:
                if "active" in self.groptions.option_space:
                    size = 12
                else:
                    size = 5
                self.ref_widgets["indicators"].load(
                    event_ref, "EventRef", size=size
                )

            self.dnd_drop_ref_targets = []
            self.ref_eventbox.connect(
                "button-press-event", self.route_ref_action
            )
            self.enable_drag(
                obj=self.secondary,
                eventbox=self.ref_eventbox,
                drag_data_get=self.drag_data_ref_get,
            )
            self.enable_drop(
                eventbox=self.ref_eventbox,
                dnd_drop_targets=self.dnd_drop_ref_targets,
                drag_data_received=self.drag_data_ref_received,
            )
        else:
            if groptions.ref_mode != 1:
                list(
                    map(
                        self.ref_eventbox.remove,
                        self.ref_eventbox.get_children(),
                    )
                )
                self.set_spacing(0)

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

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
        citations = len(self.event.citation_list)
        if self.event.citation_list:
            for handle in self.event.citation_list:
                citation = self.fetch("Citation", handle)
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
            return get_event_category_color_css(
                self.event_category, self.grstate.config
            )
        if scheme == 4:
            return get_confidence_color_css(
                self.confidence, self.grstate.config
            )

        if self.event_person:
            living = probably_alive(self.event_person, self.grstate.dbstate.db)
        else:
            living = False
        return get_person_color_css(self.event_person, living=living)

    def add_custom_actions(self):
        """
        Add action menu items for the event.
        """
        self.action_menu.append(self._participants_option())

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
        participants, text = get_participants(
            self.grstate.dbstate.db, self.primary.obj
        )
        if len(participants) > 1:
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
                    gotomenu.add(
                        menu_item(
                            "gramps-person", text, self.goto_person, handle
                        )
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
                if not event_ref.get_role().is_primary():
                    removemenu.add(
                        menu_item(
                            "list-remove",
                            text,
                            self.remove_participant,
                            person,
                            event_ref,
                        )
                    )
                if not self.event_person.handle == handle:
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

    def drag_data_ref_get(
        self, _dummy_widget, _dummy_context, data, info, _dummy_time
    ):
        """
        Return requested data.
        """
        if info == self.secondary.dnd_type.app_id:
            returned_data = (
                self.secondary.dnd_type.drag_type,
                id(self),
                self.secondary.obj,
                0,
            )
            data.set(
                self.secondary.dnd_type.atom_drag_type,
                8,
                pickle.dumps(returned_data),
            )

    def drag_data_ref_received(
        self,
        _dummy_widget,
        _dummy_context,
        _dummy_x,
        _dummy_y,
        data,
        _dummy_info,
        _dummy_time,
    ):
        """
        Handle dropped data.
        """
        if data and data.get_data():
            try:
                dnd_type, obj_id, obj_handle, dummy_var1 = pickle.loads(
                    data.get_data()
                )
            except pickle.UnpicklingError:
                return self.dropped_ref_text(data.get_data().decode("utf-8"))
            if id(self) == obj_id:
                return
            if DdTargets.NOTE_LINK.drag_type == dnd_type:
                self.added_ref_note(obj_handle)

    def dropped_ref_text(self, data):
        """
        Examine and try to handle dropped text in a reasonable manner.
        """
        if data and hasattr(self.secondary.obj, "note_list"):
            self.add_new_ref_note(None, content=data)

    def route_ref_action(self, obj, event):
        """
        Route the ref related action if the frame was clicked on.
        """
        if button_activated(event, _RIGHT_BUTTON):
            self.build_ref_action_menu(obj, event)
        elif not button_activated(event, _LEFT_BUTTON):
            if self.event_ref.get_role().is_family():
                participant = self.event_family
            else:
                participant = self.event_person
            context = GrampsContext(participant, self.secondary.obj, None)
            return self.grstate.load_page(context.pickled)

    def build_ref_action_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click on a reference object.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            action_menu = Gtk.Menu()
            action_menu.append(self._edit_event_ref_option())
            action_menu.append(
                self._notes_option(
                    self.secondary.obj,
                    self.add_new_ref_note,
                    self.add_existing_ref_note,
                    self.remove_ref_note,
                    no_children=True,
                )
            )
            action_menu.append(self._change_ref_privacy_option())
            action_menu.add(Gtk.SeparatorMenuItem())
            label = Gtk.MenuItem(
                label="{} {}".format(_("Event"), _("reference"))
            )
            label.set_sensitive(False)
            action_menu.append(label)

            action_menu.show_all()
            if Gtk.get_minor_version() >= 22:
                action_menu.popup_at_pointer(event)
            else:
                action_menu.popup(
                    None, None, None, None, event.button, event.time
                )

    def _edit_event_ref_option(self):
        """
        Build the edit option.
        """
        name = "{} {}".format(_("Edit"), _("reference"))
        return menu_item("gtk-edit", name, self.edit_self)

    def add_new_ref_note(self, _dummy_obj, content=None):
        """
        Add a new note.
        """
        note = Note()
        if content:
            note.set(content)
        if self.event_ref.get_role().is_family():
            callback = self.update_family_event
        else:
            callback = self.update_person_event
        try:
            EditNote(
                self.grstate.dbstate, self.grstate.uistate, [], note, callback
            )
        except WindowActiveError:
            pass

    def added_ref_note(self, handle):
        """
        Add the new or existing note to the current object.
        """
        if handle and self.secondary.obj.add_note(handle):
            if self.event_ref.get_role().is_family():
                self.update_family_event(self.secondary.obj)
            else:
                self.update_person_event(self.secondary.obj)

    def add_existing_ref_note(self, _dummy_obj):
        """
        Add an existing note.
        """
        select_note = SelectorFactory("Note")
        selector = select_note(self.grstate.dbstate, self.grstate.uistate, [])
        selection = selector.run()
        if selection:
            self.added_ref_note(selection.handle)

    def remove_ref_note(self, _dummy_obj, note):
        """
        Remove the given note from the current object.
        """
        if not note:
            return
        text = note_option_text(note)
        prefix = _(
            "You are about to remove the following note from this object:"
        )
        extra = _("This removes the reference but does not delete the note.")
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"),
            "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm),
        ):
            action = "{} {} {} {} {} {}".format(
                _("Removed"),
                _("Note"),
                note.get_gramps_id(),
                _("from"),
                _("EventRef"),
                self.primary.obj.get_gramps_id(),
            )
            self.secondary.obj.remove_note(note.get_handle())
            if self.event_ref.get_role().is_family():
                with DbTxn(action, self.grstate.dbstate.db) as trans:
                    self.grstate.dbstate.db.commit_family(
                        self.event_family, trans
                    )
            else:
                with DbTxn(action, self.grstate.dbstate.db) as trans:
                    self.grstate.dbstate.db.commit_person(
                        self.event_person, trans
                    )

    def _change_ref_privacy_option(self):
        """
        Build privacy option based on current object state.
        """
        if self.secondary.obj.private:
            return menu_item(
                "gramps-unlock",
                _("Make public"),
                self.change_ref_privacy,
                False,
            )
        return menu_item(
            "gramps-lock", _("Make private"), self.change_ref_privacy, True
        )

    def change_ref_privacy(self, _dummy_obj, mode):
        """
        Update the privacy indicator for the current object.
        """
        if mode:
            text = _("Private")
        else:
            text = _("Public")
        action = "{} {} {} {}".format(
            _("Made"),
            _("EventRef"),
            self.primary.obj.get_gramps_id(),
            text,
        )
        self.event_ref.set_privacy(mode)
        if self.event_ref.get_role().is_family():
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.grstate.dbstate.db.commit_family(self.event_family, trans)
        else:
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.grstate.dbstate.db.commit_person(self.event_person, trans)
