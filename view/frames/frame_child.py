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
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Citation, Note, Source
from gramps.gen.lib.const import IDENTICAL
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import EditChildRef, EditCitation, EditNote
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext, GrampsObject
from ..common.common_const import _LEFT_BUTTON, _RIGHT_BUTTON
from ..common.common_utils import (
    button_activated,
    citation_option_text,
    menu_item,
    note_option_text,
)
from .frame_person import PersonGrampsFrame

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
        groptions,
        family,
        child_ref,
    ):
        self.family = family
        self.child = grstate.fetch("Person", child_ref.ref)
        PersonGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            self.child,
        )
        if not groptions.ref_mode:
            return
        self.reference = GrampsObject(child_ref)
        self.dnd_drop_ref_targets = []
        self.ref_widgets["id"].load(
            child_ref, "ChildRef", gramps_id=self.primary.obj.get_gramps_id()
        )
        self.ref_eventbox.connect("button-press-event", self.route_ref_action)

        vbox = None
        if child_ref.get_father_relation():
            reltype = child_ref.get_father_relation()
            if groptions.ref_mode in [1, 3]:
                left = groptions.ref_mode == 1
                self.ref_widgets["body"].pack_start(
                    self.make_label(_("Father"), left=left), False, False, 0
                )
                self.ref_widgets["body"].pack_start(
                    self.make_label(str(reltype), left=left), False, False, 0
                )
            else:
                vbox = Gtk.VBox()
                vbox.pack_start(
                    self.make_label("{}: {}".format(_("Father"), reltype)),
                    True,
                    True,
                    0,
                )

        if child_ref.get_mother_relation():
            reltype = child_ref.get_mother_relation()
            if groptions.ref_mode in [1, 3]:
                left = groptions.ref_mode == 1
                self.ref_widgets["body"].pack_start(
                    self.make_label(_("Mother"), left=left), False, False, 0
                )
                self.ref_widgets["body"].pack_start(
                    self.make_label(str(reltype), left=left), False, False, 0
                )
            else:
                if not vbox:
                    vbox = Gtk.VBox()
                vbox.pack_start(
                    self.make_label("{}: {}".format(_("Mother"), reltype)),
                    True,
                    True,
                    0,
                )

        if vbox:
            self.ref_widgets["body"].pack_start(vbox, True, True, 0)

        self.ref_widgets["icons"].load(child_ref, "ChildRef")

        self.enable_drag(
            obj=self.reference,
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
        if info == self.reference.dnd_type.app_id:
            returned_data = (
                self.reference.dnd_type.drag_type,
                id(self),
                self.reference.obj,
                0,
            )
            data.set(
                self.reference.dnd_type.atom_drag_type,
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
        if data and hasattr(self.reference.obj, "note_list"):
            self.add_new_ref_note(None, content=data)

    def route_ref_action(self, obj, event):
        """
        Route the ref related action if the frame was clicked on.
        """
        if button_activated(event, _RIGHT_BUTTON):
            self.build_ref_action_menu(obj, event)
        elif not button_activated(event, _LEFT_BUTTON):
            page_context = GrampsContext(self.family, self.reference.obj, None)
            return self.grstate.load_page(page_context.pickled)

    def build_ref_action_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click on a reference object.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            action_menu = Gtk.Menu()
            action_menu.append(self._edit_child_ref_option())
            action_menu.append(
                self._citations_option(
                    self.reference.obj,
                    self.add_new_ref_citation,
                    self.add_existing_ref_citation,
                    self.remove_ref_citation,
                )
            )
            action_menu.append(
                self._notes_option(
                    self.reference.obj,
                    self.add_new_ref_note,
                    self.add_existing_ref_note,
                    self.remove_ref_note,
                    no_children=True,
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
                action_menu.popup(
                    None, None, None, None, event.button, event.time
                )

    def _edit_child_ref_option(self):
        """
        Build the edit option.
        """
        name = "{} {}".format(
            _("Edit"), name_displayer.display(self.primary.obj)
        )
        return menu_item("gtk-edit", name, self.edit_child_ref)

    def edit_child_ref(self, *_dummy_obj):
        """
        Launch the editor.
        """
        try:
            name = name_displayer.display(self.primary.obj)
            EditChildRef(
                name,
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.reference.obj,
                self.save_child_ref,
            )
        except WindowActiveError:
            pass

    def save_child_ref(self, child_ref, action_text=None, delete=False):
        """
        Save the edited object.
        """
        if not child_ref:
            return
        family = self.fetch("Family", self.groptions.backlink)
        child_ref_list = []
        for ref in family.get_child_ref_list():
            if child_ref.ref == ref.ref:
                if child_ref.is_equivalent(ref) == IDENTICAL:
                    if not delete:
                        return
                child_ref_list.append(child_ref)
            else:
                child_ref_list.append(ref)
        if action_text:
            action = action_text
        else:
            action = "{} {} {} {} {} {}".format(
                _("Edited"),
                _("ChildRef"),
                self.primary.obj.get_gramps_id(),
                _("for"),
                _("Family"),
                family.get_gramps_id(),
            )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            family.set_child_ref_list(child_ref_list)
            self.grstate.dbstate.db.commit_family(family, trans)

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
        if handle and self.reference.obj.add_citation(handle):
            citation = self.fetch("Citation", handle)
            action = "{} {} {} {} {} {}".format(
                _("Added"),
                _("Citation"),
                citation.get_gramps_id(),
                _("to"),
                _("ChildRef"),
                self.primary.obj.get_gramps_id(),
            )
            self.save_child_ref(self.reference.obj, action_text=action)

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
                _("ChildRef"),
                self.primary.obj.get_gramps_id(),
            )
            self.reference.obj.remove_citation_references(
                [citation.get_handle()]
            )
            self.save_child_ref(
                self.reference.obj, action_text=action, delete=True
            )

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
        if handle and self.reference.obj.add_note(handle):
            note = self.fetch("Note", handle)
            action = "{} {} {} {} {} {}".format(
                _("Added"),
                _("Note"),
                note.get_gramps_id(),
                _("to"),
                _("ChildRef"),
                self.primary.obj.get_gramps_id(),
            )
            self.save_child_ref(self.reference.obj, action_text=action)

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
                _("ChildRef"),
                self.primary.obj.get_gramps_id(),
            )
            self.reference.obj.remove_note(note.get_handle())
            self.save_child_ref(
                self.reference.obj, action_text=action, delete=True
            )

    def _change_ref_privacy_option(self):
        """
        Build privacy option based on current object state.
        """
        if self.reference.obj.private:
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
        family = self.fetch("Family", self.groptions.backlink)
        if mode:
            text = _("Private")
        else:
            text = _("Public")
        action = "{} {} {} {} {} {}".format(
            _("Made"),
            _("ChildRef"),
            self.primary.obj.get_gramps_id(),
            _("Family"),
            family.get_gramps_id(),
            text,
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            for child_ref in family.get_child_ref_list():
                if child_ref.ref == self.reference.obj.ref:
                    child_ref.set_privacy(mode)
                    break
            self.grstate.dbstate.db.commit_family(family, trans)
