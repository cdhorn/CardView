#
# Gramps - a GTK+/GNOME based genealogy program
#
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
AssociationGrampsFrame
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
from gi.repository import Gtk, Gdk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Citation, Note, Source
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import EditCitation, EditNote, EditPersonRef
from gramps.gui.selectors import SelectorFactory


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_const import _LEFT_BUTTON, _RIGHT_BUTTON
from .frame_person import PersonGrampsFrame
from .frame_utils import (
    button_activated,
    citation_option_text,
    menu_item,
    note_option_text,
)

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AssociationGrampsFrame class
#
# ------------------------------------------------------------------------
class AssociationGrampsFrame(PersonGrampsFrame):
    """
    The AssociationGrampsFrame exposes some of the basic facts about an
    Association.
    """

    def __init__(
        self,
        grstate,
        groptions,
        person,
        person_ref,
    ):
        self.ref_person = grstate.fetch("Person", person_ref.ref)
        PersonGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            self.ref_person,
            obj_ref=person_ref,
        )
        self.base_person = person
        self.dnd_drop_ref_targets = []
        self.ref_eventbox.connect("button-press-event", self.route_ref_action)

        association = person_ref.get_relation()
        if not association:
            association = _("[None Provided]")
        if groptions.ref_mode == 2:
            self.ref_fact_body.pack_start(
                self.make_label(_("Association"), left=False), False, False, 0
            )
            self.ref_fact_body.pack_start(
                self.make_label(association, left=False), False, False, 0
            )
        else:
            self.ref_fact_body.pack_start(
                self.make_label("{}: {}".format(_("Association"), association)),
                True,
                True,
                0,
            )

        relation = grstate.uistate.relationship.get_one_relationship(
            grstate.dbstate.db, person, self.ref_person
        )
        if relation:
            if groptions.ref_mode == 2:
                self.ref_fact_body.pack_start(
                    self.make_label(_("Relationship"), left=False),
                    False,
                    False,
                    0,
                )
                self.ref_fact_body.pack_start(
                    self.make_label(relation.capitalize(), left=False),
                    False,
                    False,
                    0,
                )
            else:
                self.ref_fact_body.pack_start(
                    self.make_label(
                        "{}: {}".format(
                            _("Relationship"), relation.capitalize()
                        )
                    ),
                    True,
                    True,
                    0,
                )

        if self.get_option("options.global.enable-child-indicators"):
            if "active" in self.groptions.option_space:
                size = 12
            else:
                size = 5
            self.ref_indicators.load(person_ref, "PersonRef", size=size)

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
            if DdTargets.CITATION_LINK.drag_type == dnd_type:
                self.added_ref_citation(obj_handle)
            elif DdTargets.NOTE_LINK.drag_type == dnd_type:
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
            data = pickle.dumps(
                (
                    "Person",
                    self.base_person,
                    "PersonRef",
                    self.ref_person.get_handle(),
                )
            )
            return self.grstate.context_changed("PersonRef", data)

    def build_ref_action_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click on a reference object.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            action_menu = Gtk.Menu()
            action_menu.append(self._edit_person_ref_option())
            action_menu.append(
                self._citations_option(
                    self.secondary.obj,
                    self.add_new_ref_citation,
                    self.add_existing_ref_citation,
                    self.remove_ref_citation,
                )
            )
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
            label = Gtk.MenuItem(label=_("Person reference"))
            label.set_sensitive(False)
            action_menu.append(label)

            action_menu.show_all()
            if Gtk.get_minor_version() >= 22:
                action_menu.popup_at_pointer(event)
            else:
                action_menu.popup(
                    None, None, None, None, event.button, event.time
                )

    def _edit_person_ref_option(self):
        """
        Build the edit option.
        """
        name = "{} {}".format(
            _("Edit"), name_displayer.display(self.primary.obj)
        )
        return menu_item("gtk-edit", name, self.edit_person_ref)

    def edit_person_ref(self, *_dummy_obj):
        """
        Launch the editor.
        """
        try:
            EditPersonRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.secondary.obj,
                self.save_person_ref,
            )
        except WindowActiveError:
            pass

    def save_person_ref(self, person_ref, action_text=None):
        """
        Save the edited object.
        """
        if not person_ref:
            return
        action = "{} {} {} {} {} {}".format(
            _("Edited"),
            _("PersonRef"),
            self.primary.obj.get_gramps_id(),
            _("for"),
            _("Person"),
            self.base_person.get_gramps_id(),
        )
        if action_text:
            action = action_text
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.grstate.dbstate.db.commit_person(self.base_person, trans)

    def add_new_ref_citation(self, _dummy_obj):
        """
        Add a new citation.
        """
        citation = Citation()
        source = Source()
        try:
            EditCitation(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                citation,
                source,
                self.added_ref_citation,
            )
        except WindowActiveError:
            pass

    def added_ref_citation(self, handle):
        """
        Add the new or existing citation to the current object.
        """
        if handle and self.secondary.obj.add_citation(handle):
            citation = self.fetch("Citation", handle)
            action = "{} {} {} {} {} {}".format(
                _("Added"),
                _("Citation"),
                citation.get_gramps_id(),
                _("to"),
                _("PersonRef"),
                self.primary.obj.get_gramps_id(),
            )
            self.save_person_ref(self.secondary.obj, action_text=action)

    def add_existing_ref_citation(self, _dummy_obj):
        """
        Add an existing citation.
        """
        select_citation = SelectorFactory("Citation")
        selector = select_citation(
            self.grstate.dbstate, self.grstate.uistate, []
        )
        selection = selector.run()
        if selection:
            if isinstance(selection, Source):
                try:
                    EditCitation(
                        self.grstate.dbstate,
                        self.grstate.uistate,
                        [],
                        Citation(),
                        selection,
                        callback=self.added_ref_citation,
                    )
                except WindowActiveError:
                    pass
            elif isinstance(selection, Citation):
                try:
                    EditCitation(
                        self.grstate.dbstate,
                        self.grstate.uistate,
                        [],
                        selection,
                        callback=self.added_ref_citation,
                    )
                except WindowActiveError:
                    pass
            else:
                raise ValueError("Selection must be either source or citation")

    def remove_ref_citation(self, _dummy_obj, citation):
        """
        Remove the given citation from the current object.
        """
        if not citation:
            return
        text = citation_option_text(self.grstate.dbstate.db, citation)
        prefix = _(
            "You are about to remove the following citation from this object:"
        )
        extra = _(
            "This removes the reference but does not delete the citation."
        )
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"),
            "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm),
        ):
            action = "{} {} {} {} {} {}".format(
                _("Removed"),
                _("Citation"),
                citation.get_gramps_id(),
                _("from"),
                _("PersonRef"),
                self.primary.obj.get_gramps_id(),
            )
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.secondary.obj.remove_citation_references(
                    [citation.get_handle()]
                )
                self.grstate.dbstate.db.commit_person(self.base_person, trans)

    def add_new_ref_note(self, _dummy_obj, content=None):
        """
        Add a new note.
        """
        note = Note()
        if content:
            note.set(content)
        try:
            EditNote(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                note,
                self.added_ref_note,
            )
        except WindowActiveError:
            pass

    def added_ref_note(self, handle):
        """
        Add the new or existing note to the current object.
        """
        if handle and self.secondary.obj.add_note(handle):
            note = self.fetch("Note", handle)
            action = "{} {} {} {} {} {}".format(
                _("Added"),
                _("Note"),
                note.get_gramps_id(),
                _("to"),
                _("PersonRef"),
                self.primary.obj.get_gramps_id(),
            )
            self.save_person_ref(self.secondary.obj, action_text=action)

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
                _("PersonRef"),
                self.primary.obj.get_gramps_id(),
            )
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.secondary.obj.remove_note(note.get_handle())
                self.grstate.dbstate.db.commit_person(self.base_person, trans)

    def _change_ref_privacy_option(self):
        """
        Build privacy option based on current object state.
        """
        if self.secondary.obj.get_privacy():
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
        action = "{} {} {} {} {} {} {}".format(
            _("Made"),
            _("PersonRef"),
            self.primary.obj.get_gramps_id(),
            _("for"),
            _("Person"),
            self.base_person.get_gramps_id(),
            text,
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.secondary.obj.set_privacy(mode)
            self.grstate.dbstate.db.commit_person(self.base_person, trans)
