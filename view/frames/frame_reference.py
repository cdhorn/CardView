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
ReferenceGrampsFrame
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
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Attribute, Citation, Note, Source
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import (
    EditAttribute,
    EditCitation,
    EditNote,
    EditSource,
)
from gramps.gui.selectors import SelectorFactory
from gramps.gui.utils import match_primary_mask

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext
from ..common.common_const import (
    BUTTON_MIDDLE,
    BUTTON_PRIMARY,
    BUTTON_SECONDARY,
)
from ..common.common_utils import (
    attribute_option_text,
    button_pressed,
    button_released,
    citation_option_text,
    menu_item,
    note_option_text,
)
from ..menus.menu_config import build_config_menu
from .frame_primary import PrimaryGrampsFrame
from .frame_selectors import get_attribute_types

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# ReferenceGrampsFrame class
#
# ------------------------------------------------------------------------
class ReferenceGrampsFrame(PrimaryGrampsFrame):
    """
    The ReferenceGrampsFrame class provides support for object References.
    """

    def __init__(self, grstate, groptions, primary_obj, reference_tuple=None):
        PrimaryGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            primary_obj,
            reference_tuple=reference_tuple,
        )
        self.dnd_drop_ref_targets = []
        if not reference_tuple or not groptions.ref_mode:
            return

        self.ref_widgets["id"].load(
            self.reference.obj,
            self.reference.obj_type,
            gramps_id=self.primary.obj.get_gramps_id(),
        )
        self.ref_widgets["icons"].load(
            self.reference.obj, self.reference.obj_type, title=self.get_title()
        )
        self.ref_eventbox.connect(
            "button-press-event", self.ref_button_pressed
        )
        self.ref_eventbox.connect(
            "button-release-event", self.ref_button_released
        )

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
                dnd_type, obj_id, obj_or_handle, dummy_var1 = pickle.loads(
                    data.get_data()
                )
            except pickle.UnpicklingError:
                return self.dropped_ref_text(data.get_data().decode("utf-8"))
            if id(self) != obj_id:
                if DdTargets.NOTE_LINK.drag_type == dnd_type:
                    self.added_ref_note(obj_or_handle)
                elif DdTargets.CITATION_LINK.drag_type == dnd_type:
                    self.added_ref_citation(obj_or_handle)

    def dropped_ref_text(self, data):
        """
        Examine and try to handle dropped text in a reasonable manner.
        """
        if data and hasattr(self.reference.obj, "note_list"):
            self.add_new_ref_note(None, content=data)

    def ref_button_pressed(self, obj, event):
        """
        Handle button pressed.
        """
        if button_pressed(event, BUTTON_SECONDARY):
            self.build_ref_context_menu(obj, event)
            return True
        if button_pressed(event, BUTTON_PRIMARY):
            return False
        if button_pressed(event, BUTTON_MIDDLE):
            build_config_menu(self, self.grstate, self.groptions, event)
            return True
        return False

    def ref_button_released(self, obj, event):
        """
        Handle button release.
        """
        if button_released(event, BUTTON_PRIMARY):
            if match_primary_mask(event.get_state()):
                self.dump_context()
                return True
            page_context = GrampsContext(
                self.reference_base, self.reference, None
            )
            self.grstate.load_page(page_context.pickled)
            return True
        return False

    def build_ref_context_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click on a reference object.
        """
        context_menu = Gtk.Menu()
        self.add_ref_custom_actions(context_menu)
        if hasattr(self.reference.obj, "attribute_list"):
            context_menu.append(
                self._attributes_option(
                    self.reference.obj,
                    self.add_ref_attribute,
                    self.remove_ref_attribute,
                    self.edit_ref_attribute,
                )
            )
        if hasattr(self.reference.obj, "citation_list"):
            context_menu.append(
                self._citations_option(
                    self.reference.obj,
                    self.add_new_ref_source_citation,
                    self.add_existing_ref_source_citation,
                    self.add_existing_ref_citation,
                    self.remove_ref_citation,
                )
            )
        if hasattr(self.reference.obj, "note_list"):
            context_menu.append(
                self._notes_option(
                    self.reference.obj,
                    self.add_new_ref_note,
                    self.add_existing_ref_note,
                    self.remove_ref_note,
                    no_children=True,
                )
            )
        context_menu.append(self._change_ref_privacy_option())
        context_menu.add(Gtk.SeparatorMenuItem())
        reference_type = self._get_reference_type()
        label = Gtk.MenuItem(label=reference_type)
        label.set_sensitive(False)
        context_menu.append(label)
        context_menu.attach_to_widget(self, None)
        context_menu.show_all()
        if Gtk.get_minor_version() >= 22:
            context_menu.popup_at_pointer(event)
        else:
            context_menu.popup(
                None, None, None, None, event.button, event.time
            )

    def add_ref_custom_actions(self, context_menu):
        """
        For derived objects to inject their own actions into the menu.
        """

    def _get_reference_type(self):
        """
        Return textual string describing reference type.
        """
        if self.reference.obj_type == "ChildRef":
            text = _("Child")
        elif self.reference.obj_type == "PersonRef":
            text = _("Person")
        elif self.reference.obj_type == "EventRef":
            text = _("Event")
        elif self.reference.obj_type == "RepoRef":
            text = _("Repository")
        elif self.reference.obj_type == "MediaRef":
            text = _("Media")
        return " ".join((text, _("reference")))

    def save_ref(self, obj_ref, _dummy_var1=None):
        """
        Save the edited or modified object.
        """
        if not obj_ref:
            return
        message = " ".join(
            (
                _("Updated"),
                self.reference.obj_lang,
                self.primary.obj.get_gramps_id(),
                _("for"),
                self.reference_base.obj_lang,
                self.reference_base.obj.get_gramps_id(),
            )
        )
        self.reference_base.commit(self.grstate, message)

    def _commit_ref_message(self, obj_type, obj_gramps_id, action="add"):
        """
        Construct commit message for a reference.
        """
        if action == "add":
            label = _("Added")
            preposition = _("to")
        elif action == "remove":
            label = _("Removed")
            preposition = _("from")
        else:
            label = _("Updated")
            preposition = _("for")

        return " ".join(
            (
                label,
                obj_type,
                obj_gramps_id,
                preposition,
                self.reference.obj_lang,
                self.primary.obj.get_gramps_id(),
                _("for"),
                self.reference_base.obj_lang,
                self.reference_base.obj.get_gramps_id(),
            )
        )

    def edit_ref_attribute(self, _dummy_obj, attribute):
        """
        Edit an attribute.
        """
        attribute_types = get_attribute_types(
            self.grstate.dbstate.db, self.primary.obj_type
        )
        try:
            EditAttribute(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                attribute,
                "",
                attribute_types,
                self._edited_ref_attribute,
            )
        except WindowActiveError:
            pass

    def _edited_ref_attribute(self, attribute):
        """
        Save edited attribute.
        """
        if attribute:
            message = self._commit_ref_message(
                _("Attribute"), attribute.get_type(), action="update"
            )
            self.reference_base.commit(self.grstate, message)

    def add_ref_attribute(self, _dummy_obj):
        """
        Add a new attribute.
        """
        attribute_types = get_attribute_types(
            self.grstate.dbstate.db, self.primary.obj_type
        )
        try:
            attribute = Attribute()
            EditAttribute(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                attribute,
                "",
                attribute_types,
                self.added_ref_attribute,
            )
        except WindowActiveError:
            pass

    def added_ref_attribute(self, attribute):
        """
        Save the new attribute to finish adding it.
        """
        if attribute:
            message = self._commit_ref_message(
                _("Attribute"), str(attribute.get_type())
            )
            self.reference.obj.add_attribute(attribute)
            self.reference_base.commit(self.grstate, message)

    def remove_ref_attribute(self, _dummy_obj, attribute):
        """
        Remove the given attribute from the current object.
        """
        if not attribute:
            return
        text = attribute_option_text(attribute)
        prefix = _(
            "You are about to remove the following attribute from this object:"
        )
        if self.confirm_action(_("Warning"), prefix, "\n\n<b>", text, "</b>"):
            message = self._commit_ref_message(
                _("Attribute"), str(attribute.get_type()), action="remove"
            )
            self.reference.obj.remove_attribute(attribute)
            self.reference_base.commit(self.grstate, message)

    def add_new_ref_source_citation(self, _dummy_obj):
        """
        Add a new source from which to create a new citation.
        """
        source = Source()
        try:
            EditSource(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                source,
                self._add_new_ref_citation,
            )
        except WindowActiveError:
            pass

    def add_existing_ref_source_citation(self, _dummy_obj):
        """
        Select an existing source from which to create a citation.
        """
        select_source = SelectorFactory("Source")
        dialog = select_source(self.grstate.dbstate, self.grstate.uistate)
        source_handle = dialog.run()
        if source_handle:
            self._add_new_ref_citation(source_handle)

    def _add_new_ref_citation(self, obj_or_handle):
        """
        Add a new citation.
        """
        if isinstance(obj_or_handle, str):
            source = self.fetch("Source", obj_or_handle)
        else:
            source = obj_or_handle
        citation = Citation()
        citation.set_reference_handle(source.get_handle())
        try:
            EditCitation(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                citation,
                source,
                self._added_ref_citation,
            )
        except WindowActiveError:
            pass

    def _added_ref_citation(self, handle):
        """
        Add the new or existing citation to the current object.
        """
        if handle and self.reference.obj.add_citation(handle):
            citation = self.fetch("Citation", handle)
            message = self._commit_ref_message(
                _("Citation"), citation.get_gramps_id()
            )
            self.reference_base.commit(self.grstate, message)

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
                        callback=self._added_ref_citation,
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
                        callback=self._added_ref_citation,
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
        if self.confirm_action(
            _("Warning"), prefix, "\n\n<b>", text, "</b>\n\n", extra
        ):
            message = self._commit_ref_message(
                _("Citation"), citation.get_gramps_id(), action="remove"
            )
            self.reference.obj.remove_citation_references(
                [citation.get_handle()]
            )
            self.reference_base.commit(self.grstate, message)

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
            message = self._commit_ref_message(_("Note"), note.get_gramps_id())
            self.reference_base.commit(self.grstate, message)

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
        if self.confirm_action(
            _("Warning"), prefix, "\n\n<b>", text, "</b>\n\n", extra
        ):
            message = self._commit_ref_message(
                _("Note"), note.get_gramps_id(), action="remove"
            )
            self.reference.obj.remove_note(note.get_handle())
            self.reference_base.commit(self.grstate, message)

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
        Update the privacy indicator for the current ref object.
        """
        if mode:
            text = _("Private")
        else:
            text = _("Public")
        message = " ".join(
            (
                _("Made"),
                self.reference.obj_lang,
                self.primary.obj.get_gramps_id(),
                _("for"),
                self.reference_base.obj_lang,
                self.reference_base.obj.get_gramps_id(),
                text,
            )
        )
        self.reference.obj.set_privacy(mode)
        self.reference_base.commit(self.grstate, message)
