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
ChildGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
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
from gramps.gui.editors import EditChildRef, EditCitation, EditNote
from gramps.gui.selectors import SelectorFactory


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_const import _GENDERS, _LEFT_BUTTON, _RIGHT_BUTTON
from frame_person import PersonGrampsFrame
from frame_utils import (
    button_activated,
    get_person_color_css,
    TextLink,
)

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# ChildGrampsFrame class
#
# ------------------------------------------------------------------------
class ChildGrampsFrame(PersonGrampsFrame):
    """
    The ChildGrampsFrame exposes some of the basic facts about a Child.
    """

    def __init__(
        self,
        grstate,
        context,
        child,
        child_ref,
        relation=None,
        number=0,
        groups=None,
        family_backlink=None
    ):
        PersonGrampsFrame.__init__(
            self, grstate, context, child, obj_ref=child_ref,
            relation=relation, number=number, groups=groups,
            family_backlink=family_backlink
        )
        self.ref_eventbox.connect("button-press-event", self.route_ref_action)

        if child_ref.get_father_relation():
                reltype = child_ref.get_father_relation()
                hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
                hbox.pack_end(self.make_label(_("Father"), left=False), False, False, 0)
                self.ref_body.pack_start(hbox, False, False, 0)
                hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
                hbox.pack_end(self.make_label(str(reltype), left=False), False, False, 0)
                self.ref_body.pack_start(hbox, False, False, 0)
    
        if child_ref.get_mother_relation():
            reltype = child_ref.get_mother_relation()
            hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
            hbox.pack_end(self.make_label(_("Mother"), left=False), False, False, 0)
            self.ref_body.pack_start(hbox, False, False, 0)
            hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.END)
            hbox.pack_end(self.make_label(str(reltype), left=False), False, False, 0)
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
            action_menu.append(self._edit_child_ref_option())
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
            label = Gtk.MenuItem(label=_("Child reference"))
            label.set_sensitive(False)
            action_menu.append(label)
            
            action_menu.show_all()
            if Gtk.get_minor_version() >= 22:
                action_menu.popup_at_pointer(event)
            else:
                action_menu.popup(None, None, None, None, event.button, event.time)

    def _edit_child_ref_option(self):
        """
        Build the edit option.
        """
        name = "{} {}".format(_("Edit"), name_displayer.display(self.obj))
        return self._menu_item("gtk-edit", name, self.edit_child_ref)

    def edit_child_ref(self, skip=None, obj=None, obj_type=None):
        """
        Launch the editor.
        """
        try:
            name = name_displayer.display(self.obj)
            EditChildRef(name, self.grstate.dbstate, self.grstate.uistate, [], self.obj_ref, self.save_child_ref)
        except WindowActiveError:
            pass

    def save_child_ref(self, child_ref, action_text=None):
        """
        Save the edited object.
        """
        if child_ref:
            family = self.grstate.dbstate.db.get_family_from_handle(self.family_backlink)
            child_ref_list = []
            for ref in family.get_child_ref_list():
                if child_ref.ref == ref.ref:
                    if child_ref.is_equivalent(ref) == IDENTICAL:
                        return
                    child_ref_list.append(child_ref)
                else:
                    child_ref_list.append(ref)
            action = "{} {} {} {} {}".format(
                _("Edited ChildRef"),
                self.obj.get_gramps_id(),
                _("for"),
                _("Family"),
                family.get_gramps_id()
            )
            if action_text:
                action = action_text
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                family.set_child_ref_list(child_ref_list)
                self.grstate.dbstate.db.commit_family(family, trans)

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
                _("ChildRef"),
                self.obj.get_gramps_id()
            )
            self.save_child_ref(self.obj_ref, action_text=action)

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
        if old_citation:
            text = self._citation_option_text(old_citation)
            prefix = _("You are about to remove the following citation from this object:")
            extra = _("Note this only removes the reference and does not delete the actual citation. " \
                      "The citation could be added back unless permanently deleted elsewhere.")
            confirm = _("Are you sure you want to continue?")
            if self.confirm_action(
                _("Warning"),
                "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm)
            ):
                if self.obj_ref.remove_citation_references([old_citation.get_handle()]):
                    action = "{} {} {} {} {}".format(
                        _("Removed Citation"),
                        old_citation.get_gramps_id(),
                        _("from"),
                        _("ChildRef"),
                        self.obj.get_gramps_id()
                    )
                    self.save_child_ref(self.obj_ref, action_text=action)

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
                _("ChildRef"),
                self.obj.get_gramps_id()
            )
            self.save_child_ref(self.obj_ref, action_text=action)

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
        if old_note:
            text = self._note_option_text(old_note)
            prefix = _("You are about to remove the following note from this object:")
            extra = _("Note this only removes the reference and does not delete the actual note. " \
                      "The note could be added back unless permanently deleted elsewhere.")
            confirm = _("Are you sure you want to continue?")
            if self.confirm_action(
                _("Warning"),
                "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm)
            ):
                if self.obj_ref.remove_note(old_note.get_handle()):
                    action = "{} {} {} {} {}".format(
                        _("Removed Note"),
                        old_note.get_gramps_id(),
                        _("from"),
                        _("ChildRef"),
                        self.obj.get_gramps_id()
                    )
                    self.save_child_ref(self.obj_ref, action_text=action)

    def _change_ref_privacy_option(self):
        """
        Build privacy option based on current object state.
        """
        if self.obj_ref.private:
            return self._menu_item("gramps-unlock", _("Make public"), self.change_ref_privacy, False)
        return self._menu_item("gramps-lock", _("Make private"), self.change_ref_privacy, True)

    def change_ref_privacy(self, obj, mode):
        """
        Update the privacy indicator for the current object.
        """
        family = self.grstate.dbstate.db.get_family_from_handle(self.family_backlink)
        if mode:
            text = _("Private")
        else:
            text = _("Public")
        action = "{} {} {} {} {} {}".format(
            _("Made"),
            _("ChildRef"),
            self.obj.get_gramps_id(),
            _("Family"),
            family.get_gramps_id(),
            text,
        )
        commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            for child_ref in family.get_child_ref_list():
                if child_ref.ref == self.obj_ref.ref:
                    child_ref.set_privacy(mode)
                    break
            self.grstate.dbstate.db.commit_family(family, trans)
