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

from html import escape

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
from gramps.gen.lib.const import IDENTICAL
from gramps.gen.utils.alive import probably_alive
from gramps.gui.editors import EditCitation, EditNote, EditPersonRef
from gramps.gui.selectors import SelectorFactory


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_primary import _LEFT_BUTTON, _RIGHT_BUTTON, button_activated
from frame_person import PersonGrampsFrame
from frame_utils import (
    _GENDERS,
    get_person_color_css,
    TextLink,
)

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# AssociationGrampsFrame class
#
# ------------------------------------------------------------------------
class AssociationGrampsFrame(PersonGrampsFrame):
    """
    The AssociationGrampsFrame exposes some of the basic facts about an Association.
    """

    def __init__(
        self,
        grstate,
        context,
        person,
        person_ref,
        groups=None,
    ):
        self.ref_person = grstate.dbstate.db.get_person_from_handle(person_ref.ref)
        PersonGrampsFrame.__init__(self, grstate, context, self.ref_person, obj_ref=person_ref, groups=groups)
        self.base_person = person

        self.ref_eventbox.connect("button-press-event", self.route_ref_action)

        association = person_ref.get_relation()
        if not association:
            association = _("[None Provided]")
        hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
        hbox.pack_end(self.make_label(_("Association"), left=False), False, False, 0)
        self.ref_body.pack_start(hbox, False, False, 0)
        hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
        hbox.pack_end(self.make_label(association, left=False), False, False, 0)
        self.ref_body.pack_start(hbox, False, False, 0)

        relation = grstate.uistate.relationship.get_one_relationship(
            grstate.dbstate.db, person, self.ref_person
        )
        if relation:
            hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
            hbox.pack_end(self.make_label(_("Relationship"), left=False), False, False, 0)
            self.ref_body.pack_start(hbox, False, False, 0)
            hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
            hbox.pack_end(self.make_label(relation.capitalize(), left=False), False, False, 0)
            self.ref_body.pack_start(hbox, False, False, 0)
            
    def route_ref_action(self, obj, event):
        """
        Route the ref related action if the frame was clicked on.
        """
        if button_activated(event, _RIGHT_BUTTON):
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                self.layout_editor()
            else:
                self.build_ref_action_menu(obj, event)
        elif not button_activated(event, _LEFT_BUTTON):
            self.switch_object(None, None, self.obj_type, self.obj.get_handle())

    def build_ref_action_menu(self, obj, event):
        """
        Build the action menu for a right click on a reference object.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            action_menu = Gtk.Menu()
            action_menu.append(self._edit_person_ref_option())
            action_menu.append(
                self._citations_option(
                    self.obj_ref, self.add_new_ref_citation,
                    self.add_existing_ref_citation, self.remove_ref_citation
                )
            )
            action_menu.append(
                self._notes_option(
                    self.obj_ref, self.add_new_ref_note,
                    self.add_existing_ref_note, self.remove_ref_note,
                    no_children=True
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
                action_menu.popup(None, None, None, None, event.button, event.time)

    def _edit_person_ref_option(self):
        """
        Build the edit option.
        """
        name = "{} {}".format(_("Edit"), name_displayer.display(self.obj))
        return self._menu_item("gtk-edit", name, self.edit_person_ref)

    def edit_person_ref(self, skip=None, obj=None, obj_type=None):
        """
        Launch the editor.
        """
        try:
            EditPersonRef(self.grstate.dbstate, self.grstate.uistate, [], self.obj_ref, self.save_person_ref)
        except WindowActiveError:
            pass

    def save_person_ref(self, person_ref, action_text=None):
        """
        Save the edited object.
        """
        if not person_ref:
            return
            action = "{} {} {} {} {}".format(
                _("Edited PersonRef"),
                self.obj.get_gramps_id(),
                _("for"),
                _("Person"),
                self.base_person.get_gramps_id()
            )
            if action_text:
                action = action_text
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.grstate.dbstate.db.commit_person(self.base_person, trans)
                
    def add_new_ref_citation(self, obj):
        """
        Add a new citation.
        """
        citation = Citation()
        source = Source()
        try:
            EditCitation(self.grstate.dbstate, self.grstate.uistate, [], citation, source, self.added_ref_citation)
        except WindowActiveError:
            pass

    def added_ref_citation(self, handle):
        """
        Add the new or existing citation to the current object.
        """
        if handle and self.obj_ref.add_citation(handle):
            citation = self.grstate.dbstate.db.get_citation_from_handle(handle)
            action = "{} {} {} {} {}".format(
                _("Added Citation"),
                citation.get_gramps_id(),
                _("to"),
                _("PersonRef"),
                self.obj.get_gramps_id()
            )
            self.save_person_ref(self.obj_ref, action_text=action)

    def add_existing_ref_citation(self, obj):
        """
        Add an existing citation.
        """
        select_citation = SelectorFactory('Citation')
        selector = select_citation(self.grstate.dbstate, self.grstate.uistate, [])
        selection = selector.run()
        if selection:
            if isinstance(selection, Source):
                try:
                    EditCitation(self.grstate.dbstate, self.grstate.uistate, [],
                                 Citation(), selection,
                                 callback=self.added_ref_citation)
                except WindowActiveError:
                    pass
            elif isinstance(selection, Citation):
                try:
                    EditCitation(self.grstate.dbstate, self.grstate.uistate, [],
                                 selection, callback=self.added_ref_citation)
                except WindowActiveError:
                    pass
            else:
                raise ValueError("Selection must be either source or citation")

    def remove_ref_citation(self, obj, old_citation):
        """
        Remove the given citation from the current object.
        """
        if not old_citation:
            return
        text = self._citation_option_text(old_citation)
        prefix = _("You are about to remove the following citation from this object:")
        extra = _("Note this only removes the reference and does not delete the actual citation. " \
                  "The citation could be added back unless permanently deleted elsewhere.")
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"),
            "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm)
        ):
            action = "{} {} {} {} {}".format(
                _("Removed Citation"),
                old_citation.get_gramps_id(),
                _("from"),
                _("PersonRef"),
                self.obj.get_gramps_id()
            )
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.obj_ref.remove_citation_references([old_citation.get_handle()])
                self.grstate.dbstate.db.commit_person(self.base_person, trans)

    def add_new_ref_note(self, obj, content=None):
        """
        Add a new note.
        """
        note = Note()
        if content:
            note.set(content)
        try:
            EditNote(self.grstate.dbstate, self.grstate.uistate, [], note, self.added_ref_note)
        except WindowActiveError:
            pass

    def added_ref_note(self, handle):
        """
        Add the new or existing note to the current object.
        """
        if handle and self.obj_ref.add_note(handle):
            note = self.grstate.dbstate.db.get_note_from_handle(handle)
            action = "{} {} {} {} {}".format(
                _("Added Note"),
                note.get_gramps_id(),
                _("to"),
                _("PersonRef"),
                self.obj.get_gramps_id()
            )
            self.save_person_ref(self.obj_ref, action_text=action)

    def add_existing_ref_note(self, obj):
        """
        Add an existing note.
        """
        select_note = SelectorFactory('Note')
        selector = select_note(self.grstate.dbstate, self.grstate.uistate, [])
        selection = selector.run()
        if selection:
            self.added_ref_note(selection.handle)

    def remove_ref_note(self, obj, old_note):
        """
        Remove the given note from the current object.
        """
        if not old_note:
            return
        text = self._note_option_text(old_note)
        prefix = _("You are about to remove the following note from this object:")
        extra = _("Note this only removes the reference and does not delete the actual note. " \
                  "The note could be added back unless permanently deleted elsewhere.")
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"),
            "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm)
        ):
            action = "{} {} {} {} {}".format(
                _("Removed Note"),
                old_note.get_gramps_id(),
                _("from"),
                _("PersonRef"),
                self.obj.get_gramps_id()
            )
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.obj_ref.remove_note(old_note.get_handle())
                self.grstate.dbstate.db.commit_person(self.base_person, trans)

    def _change_ref_privacy_option(self):
        """
        Build privacy option based on current object state.
        """
        if self.obj_ref.get_privacy():
            return self._menu_item("gramps-unlock", _("Make public"), self.change_ref_privacy, False)
        return self._menu_item("gramps-lock", _("Make private"), self.change_ref_privacy, True)


    def change_ref_privacy(self, obj, mode):
        """
        Update the privacy indicator for the current object.
        """
        if mode:
            text = _("Private")
        else:
            text = _("Public")
        action = "{} {} {} {} {} {}".format(
            _("Made"),
            _("PersonRef"),
            self.obj.get_gramps_id(),
            _("Person"),
            self.base_person.get_gramps_id(),
            text,
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.obj_ref.set_privacy(mode)
            self.grstate.dbstate.db.commit_person(self.base_person, trans)
