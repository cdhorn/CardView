#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
GrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import hashlib
import os
import pickle
import re

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
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Citation, Media, MediaRef, Note, Source, Span
from gramps.gen.mime import get_description, get_type
from gramps.gen.utils.db import navigation_label
from gramps.gen.utils.file import (
    create_checksum,
    find_file,
    media_path,
    media_path_full,
    relative_path,
)
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import ErrorDialog, WarningDialog
from gramps.gui.editors import (
    EditAddress,
    EditAttribute,
    EditCitation,
    EditMedia,
    EditMediaRef,
    EditName,
    EditNote,
    EditSource,
    EditSrcAttribute,
)
from gramps.gui.selectors import SelectorFactory
from gramps.gui.utils import match_primary_mask

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext, GrampsObject
from ..common.common_const import (
    BUTTON_MIDDLE,
    BUTTON_PRIMARY,
    BUTTON_SECONDARY,
    GRAMPS_EDITORS,
)
from ..common.common_utils import (
    attribute_option_text,
    button_pressed,
    button_released,
    citation_option_text,
    menu_item,
    note_option_text,
    submenu_item,
)
from ..menus.menu_config import build_config_menu
from .frame_selectors import get_attribute_types
from .frame_view import GrampsFrameView

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsFrame class
#
# ------------------------------------------------------------------------
class GrampsFrame(GrampsFrameView):
    """
    Provides core methods for working with the Gramps objects it manages.
    """

    def __init__(self, grstate, groptions, primary_obj, reference_tuple=None):
        if reference_tuple:
            (base_obj, reference_obj) = reference_tuple
            assert reference_obj.ref == primary_obj.get_handle()
            self.reference_base = GrampsObject(base_obj)
            self.reference = GrampsObject(reference_obj)
        else:
            self.reference_base = None
            self.reference = None
        GrampsFrameView.__init__(self, grstate, groptions, self.switch_object)
        self.primary = GrampsObject(primary_obj)
        self.secondary = None
        self.focus = self.primary
        self.dnd_drop_targets = []
        self.css = ""
        if not groptions.bar_mode:
            self.init_layout()
        self.eventbox.connect("button-press-event", self.button_pressed)
        self.eventbox.connect("button-release-event", self.button_released)

    def get_context(self):
        """
        Return self context.
        """
        return GrampsContext(
            self.primary, self.reference, self.secondary, self.reference_base
        )

    def get_title(self):
        """
        Generate a title describing the framed object.
        """
        if not hasattr(self.primary.obj, "handle"):
            title = self.primary.obj_lang
            if self.secondary:
                title = "".join((title, ": ", self.secondary.obj_lang))
            return title
        title, dummy_obj = navigation_label(
            self.grstate.dbstate.db,
            self.primary.obj_type,
            self.primary.obj.get_handle(),
        )
        if self.reference:
            return "".join((title, ": ", self.reference.obj_lang))
        if self.secondary:
            return "".join((title, ": ", self.secondary.obj_lang))
        return title

    def enable_drag(self, obj=None, eventbox=None, drag_data_get=None):
        """
        Enable self as a drag source.
        """
        obj = obj or self.focus
        eventbox = eventbox or self.eventbox
        drag_data_get = drag_data_get or self.drag_data_get
        if eventbox:
            eventbox.drag_source_set(
                Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY
            )
            target_list = Gtk.TargetList.new([])
            target_list.add(
                obj.dnd_type.atom_drag_type,
                obj.dnd_type.target_flags,
                obj.dnd_type.app_id,
            )
            eventbox.drag_source_set_target_list(target_list)
            eventbox.drag_source_set_icon_name(obj.dnd_icon)
            eventbox.connect("drag_data_get", drag_data_get)

    def drag_data_get(
        self, _dummy_widget, _dummy_context, data, info, _dummy_time
    ):
        """
        Return requested data.
        """
        if info == self.focus.dnd_type.app_id:
            returned_data = (
                self.focus.dnd_type.drag_type,
                id(self),
                self.focus.obj.get_handle(),
                0,
            )
            data.set(
                self.focus.dnd_type.atom_drag_type,
                8,
                pickle.dumps(returned_data),
            )

    def enable_drop(
        self, eventbox=None, dnd_drop_targets=None, drag_data_received=None
    ):
        """
        Enable self as a basic drop target.
        """
        eventbox = eventbox or self.eventbox
        dnd_drop_targets = dnd_drop_targets or self.dnd_drop_targets
        drag_data_received = drag_data_received or self.drag_data_received
        if eventbox:
            if hasattr(self.focus.obj, "note_list"):
                for target in DdTargets.all_text_targets():
                    dnd_drop_targets.append(target)
                dnd_drop_targets.append(Gtk.TargetEntry.new("text/html", 0, 7))
                dnd_drop_targets.append(DdTargets.NOTE_LINK.target())
            if hasattr(self.primary.obj, "media_list"):
                dnd_drop_targets.append(DdTargets.MEDIAOBJ.target())
            if hasattr(self.focus.obj, "attribute_list"):
                dnd_drop_targets.append(DdTargets.ATTRIBUTE.target())
            if hasattr(self.focus.obj, "citation_list"):
                dnd_drop_targets.append(DdTargets.CITATION_LINK.target())
                dnd_drop_targets.append(DdTargets.SOURCE_LINK.target())
            if hasattr(self.focus.obj, "urls"):
                dnd_drop_targets.append(DdTargets.URL.target())
                dnd_drop_targets.append(DdTargets.URI_LIST.target())
                dnd_drop_targets.append(Gtk.TargetEntry.new("URL", 0, 8))
            eventbox.drag_dest_set(
                Gtk.DestDefaults.ALL, dnd_drop_targets, Gdk.DragAction.COPY
            )
            eventbox.connect("drag-data-received", drag_data_received)

    def drag_data_received(
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
        Handle dropped data, override in derived classes as needed.
        """
        if data and data.get_data():
            try:
                dnd_type, obj_id, obj_or_handle, dummy_var1 = pickle.loads(
                    data.get_data()
                )
            except pickle.UnpicklingError:
                return self._dropped_text(data.get_data().decode("utf-8"))
            if id(self) != obj_id:
                return self._child_drop_handler(dnd_type, obj_or_handle, data)
            return False

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing, should be defined in derived classes.
        """

    def _base_drop_handler(self, dnd_type, obj_or_handle, _dummy_data):
        """
        Handle drop processing largely common to all objects.
        """
        if DdTargets.CITATION_LINK.drag_type == dnd_type:
            self._added_citation(obj_or_handle)
            return True
        if DdTargets.SOURCE_LINK.drag_type == dnd_type:
            self.add_new_citation(None, source_handle=obj_or_handle)
            return True
        if DdTargets.NOTE_LINK.drag_type == dnd_type:
            self._added_note(obj_or_handle)
            return True
        return False

    def _dropped_text(self, data):
        """
        Examine and try to handle dropped text in a reasonable manner.
        """
        if hasattr(self.focus.obj, "media_list"):
            links = re.findall(r"(?P<url>file?://[^\s]+)", data)
            if links:
                for link in links:
                    self.add_new_media(None, filepath=link)
                return True
        added_urls = 0
        if hasattr(self.focus.obj, "urls"):
            links = re.findall(r"(?P<url>https?://[^\s]+)", data)
            if links:
                for link in links:
                    self.add_url(None, path=link)
                    added_urls = added_urls + len(link)
                return True
        if not added_urls or (len(data) > (2 * added_urls)):
            if hasattr(self.focus.obj, "note_list"):
                self.add_new_note(None, content=data)
                return True
        return False

    def load_age(self, base_date, current_date):
        """
        Calculate and show age.
        """
        if "age" in self.widgets:
            span = Span(base_date, current_date)
            if span.is_valid():
                year = str(current_date.get_year())
                precision = global_config.get(
                    "preferences.age-display-precision"
                )
                age = str(span.format(precision=precision).strip("()"))
                if age[:2] == "0 ":
                    age = ""
                text = "".join(
                    ("<b>", year, "</b>\n", age.replace(", ", ",\n"))
                )
                label = Gtk.Label(
                    label=self.detail_markup.format(text.strip()),
                    use_markup=True,
                    justify=Gtk.Justification.CENTER,
                )
                self.widgets["age"].pack_start(label, False, False, 0)

    def button_pressed(self, obj, event):
        """
        Handle button pressed.
        """
        if button_pressed(event, BUTTON_SECONDARY):
            self.build_action_menu(obj, event)
            return True
        if button_pressed(event, BUTTON_PRIMARY):
            return False
        if button_pressed(event, BUTTON_MIDDLE):
            build_config_menu(self, self.grstate, self.groptions, event)
            return True
        return False

    def button_released(self, obj, event):
        """
        Handle button released.
        """
        if button_released(event, BUTTON_PRIMARY):
            if match_primary_mask(event.get_state()):
                self.dump_context()
                return True
            self.switch_object(None, None, self.focus.obj_type, self.focus.obj)
            return True
        return False

    def switch_object(self, _dummy_obj, _dummy_event, obj_type, obj_or_handle):
        """
        Change active object for the view.
        """
        if "Ref" in obj_type:
            context = GrampsContext(self.primary, obj_or_handle, None)
        elif obj_type in ["Address", "Attribute", "Name", "Url", "LdsOrd"]:
            context = GrampsContext(self.primary, None, obj_or_handle)
        else:
            if isinstance(obj_or_handle, str):
                obj = self.grstate.fetch(obj_type, obj_or_handle)
            else:
                obj = obj_or_handle
            context = GrampsContext(obj, None, None)
        return self.grstate.load_page(context.pickled)

    def dump_context(self, *_dummy_args):
        """
        Dump context.
        """
        from .frame_window import FrameDebugWindow

        try:
            FrameDebugWindow(self.grstate, self.get_context())
        except WindowActiveError:
            WarningDialog(
                _("Could Not Open Context Object View"),
                _(
                    "A context object view window is already "
                    "open, close it before launching a new one."
                ),
                parent=self.grstate.uistate.window,
            )

    def build_action_menu(self, obj, event):
        """
        Build the action menu for a right click, should be defined in
        derived classes.
        """

    def _edit_object_option(self):
        """
        Build the edit option.
        """
        if self.secondary and not self.secondary.is_reference:
            name = " ".join((_("Edit"), self.secondary.obj_lang.lower()))
            return menu_item("gtk-edit", name, self._edit_secondary_object)
        if self.primary.obj_type == "Person":
            name = " ".join(
                (_("Edit"), name_displayer.display(self.primary.obj))
            )
        else:
            name = " ".join((_("Edit"), self.primary.obj_lang.lower()))
        return menu_item("gtk-edit", name, self.edit_primary_object)

    def edit_primary_object(self, _dummy_var1=None, obj=None, obj_type=None):
        """
        Launch the desired editor for a primary object.
        """
        obj = obj or self.primary.obj
        obj_type = obj_type or self.primary.obj_type
        try:
            GRAMPS_EDITORS[obj_type](
                self.grstate.dbstate, self.grstate.uistate, [], obj
            )
        except WindowActiveError:
            pass

    def _edit_secondary_object(self, _dummy_var1=None):
        """
        Launch the desired editor for a secondary object.
        """
        try:
            GRAMPS_EDITORS[self.secondary.obj_type](
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.secondary.obj,
                self.save_object,
            )
        except WindowActiveError:
            pass

    def save_object(self, obj, action_text=None):
        """
        Save the edited object.
        """
        if not obj:
            return
        if action_text:
            message = action_text
        else:
            message = " ".join(
                (
                    _("Edited"),
                    self.secondary.obj_lang,
                    _("for"),
                    self.primary.obj_lang,
                    self.primary.obj.get_gramps_id(),
                )
            )
        self.primary.commit(self.grstate, message)

    def _commit_message(self, obj_type, obj_label, action="add"):
        """
        Construct a commit message string.
        """
        if action == "add":
            action = _("Added")
            preposition = _("to")
        elif action == "remove":
            action = _("Removed")
            preposition = _("from")
        else:
            action = _("Updated")
            preposition = _("for")

        if self.secondary:
            return " ".join(
                (
                    action,
                    obj_type,
                    obj_label,
                    preposition,
                    self.secondary.obj_lang,
                    _("for"),
                    self.primary.obj_lang,
                    self.primary.obj.get_gramps_id(),
                )
            )
        return " ".join(
            (
                action,
                obj_type,
                obj_label,
                preposition,
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
        )

    def edit_name(self, _dummy_obj, name):
        """
        Edit a name.
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(str(name.serialize()).encode("utf-8"))
        callback = lambda x: self._edited_name(x, sha256_hash.hexdigest())
        try:
            EditName(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                name,
                callback,
            )
        except WindowActiveError:
            pass

    def _edited_name(self, name, old_hash):
        """
        Save edited name.
        """
        self.grstate.update_history_object(old_hash, name)
        message = self._commit_message(
            _("Name"), name.get_regular_name(), action="update"
        )
        self.primary.commit(self.grstate, message)

    def edit_attribute(self, _dummy_obj, attribute):
        """
        Edit an attribute.
        """
        attribute_types = get_attribute_types(
            self.grstate.dbstate.db, self.primary.obj_type
        )
        sha256_hash = hashlib.sha256()
        sha256_hash.update(str(attribute.serialize()).encode("utf-8"))
        callback = lambda x: self._edited_attribute(x, sha256_hash.hexdigest())
        try:
            if self.primary.obj_type in ["Source", "Citation"]:
                EditSrcAttribute(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    attribute,
                    "",
                    attribute_types,
                    callback,
                )
            else:
                EditAttribute(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    attribute,
                    "",
                    attribute_types,
                    callback,
                )
        except WindowActiveError:
            pass

    def _edited_attribute(self, attribute, old_hash):
        """
        Save edited attribute.
        """
        if attribute:
            self.grstate.update_history_object(old_hash, attribute)
            message = self._commit_message(
                _("Attribute"), attribute.get_type(), action="update"
            )
            self.primary.commit(self.grstate, message)

    def edit_address(self, _dummy_obj, address):
        """
        Edit an address.
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(str(address.serialize()).encode("utf-8"))
        callback = lambda x: self._edited_address(x, sha256_hash.hexdigest())
        try:
            EditAddress(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                address,
                callback,
            )
        except WindowActiveError:
            pass

    def _edited_address(self, address, old_hash):
        """
        Save edited address.
        """
        self.grstate.update_history_object(old_hash, address)
        message = " ".join(
            (
                _("Edited"),
                _("Address"),
                _("for"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
        )
        self.primary.commit(self.grstate, message)

    def _attributes_option(
        self, obj, add_attribute, remove_attribute, edit_attribute
    ):
        """
        Build the attributes submenu.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item("list-add", _("Add a new attribute"), add_attribute)
        )
        if len(obj.get_attribute_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(
                submenu_item(
                    "gramps-attribute", _("Remove an attribute"), removemenu
                )
            )
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            attribute_list = []
            for attribute in obj.get_attribute_list():
                text = attribute_option_text(attribute)
                attribute_list.append((text, attribute))
            attribute_list.sort(key=lambda x: x[0])
            for text, attribute in attribute_list:
                removemenu.add(
                    menu_item("list-remove", text, remove_attribute, attribute)
                )
                menu.add(
                    menu_item(
                        "gramps-attribute",
                        text,
                        edit_attribute,
                        attribute,
                    )
                )
        return submenu_item("gramps-attribute", _("Attributes"), menu)

    def _citations_option(
        self,
        obj,
        add_new_source_citation,
        add_existing_source_citation,
        add_existing_citation,
        remove_citation,
    ):
        """
        Build the citations submenu.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item(
                "list-add",
                _("Add new citation for a new source"),
                add_new_source_citation,
            )
        )
        menu.add(
            menu_item(
                "list-add",
                _("Add new citation for an existing source"),
                add_existing_source_citation,
            )
        )
        menu.add(
            menu_item(
                "list-add",
                _("Add an existing citation"),
                add_existing_citation,
            )
        )
        if len(obj.get_citation_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(
                submenu_item(
                    "gramps-citation", _("Remove a citation"), removemenu
                )
            )
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            citation_list = []
            for handle in obj.get_citation_list():
                citation = self.fetch("Citation", handle)
                text = citation_option_text(self.grstate.dbstate.db, citation)
                citation_list.append((text, citation))
            citation_list.sort(key=lambda x: x[0])
            for text, citation in citation_list:
                removemenu.add(
                    menu_item("list-remove", text, remove_citation, citation)
                )
                menu.add(
                    menu_item(
                        "gramps-citation", text, self.edit_citation, citation
                    )
                )
        return submenu_item("gramps-citation", _("Citations"), menu)

    def add_new_source_citation(self, _dummy_obj):
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
                self._add_new_citation,
            )
        except WindowActiveError:
            pass

    def add_existing_source_citation(self, _dummy_obj):
        """
        Select an existing source from which to create a citation.
        """
        select_source = SelectorFactory("Source")
        dialog = select_source(self.grstate.dbstate, self.grstate.uistate)
        source_handle = dialog.run()
        if source_handle:
            self._add_new_citation(source_handle)

    def _add_new_citation(self, obj_or_handle):
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
                self._added_citation,
            )
        except WindowActiveError:
            pass

    def _added_citation(self, handle):
        """
        Add the new or existing citation to the current object.
        """
        if handle:
            citation = self.fetch("Citation", handle)
            message = self._commit_message(
                _("Citation"), citation.get_gramps_id()
            )
            self.focus.save_hash()
            if self.focus.obj.add_citation(handle):
                self.focus.sync_hash(self.grstate)
                self.primary.commit(self.grstate, message)

    def add_existing_citation(self, _dummy_obj):
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
                        callback=self._added_citation,
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
                        callback=self._added_citation,
                    )
                except WindowActiveError:
                    pass
            else:
                raise ValueError("Selection must be either source or citation")

    def edit_citation(self, _dummy_obj, citation):
        """
        Edit a citation.
        """
        self.edit_primary_object(None, citation, "Citation")

    def remove_citation(self, _dummy_obj, citation):
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
            message = self._commit_message(
                _("Citation"), citation.get_gramps_id(), action="remove"
            )
            self.focus.save_hash()
            self.focus.obj.remove_citation_references([citation.get_handle()])
            self.focus.sync_hash(self.grstate)
            self.primary.commit(self.grstate, message)

    def _notes_option(
        self,
        obj,
        add_new_note,
        add_existing_note,
        remove_note,
        no_children=False,
    ):
        """
        Build the notes submenu.
        """
        menu = Gtk.Menu()
        menu.add(menu_item("list-add", _("Add a new note"), add_new_note))
        menu.add(
            menu_item("list-add", _("Add an existing note"), add_existing_note)
        )
        if len(obj.get_note_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(
                submenu_item("gramps-notes", _("Remove a note"), removemenu)
            )
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            note_list = []
            for handle in obj.get_note_list():
                note = self.fetch("Note", handle)
                text = note_option_text(note)
                note_list.append((text, note))
            note_list.sort(key=lambda x: x[0])
            for text, note in note_list:
                removemenu.add(
                    menu_item("list-remove", text, remove_note, note)
                )
                menu.add(
                    menu_item(
                        "gramps-notes", text, self.edit_note, note.handle
                    )
                )
        if (
            self.grstate.config.get("options.global.include-child-notes")
            and not no_children
        ):
            handle_list = []
            for child_obj in obj.get_note_child_list():
                for handle in child_obj.get_note_list():
                    if handle not in handle_list:
                        handle_list.append(handle)
            note_list = []
            for handle in handle_list:
                note = self.fetch("Note", handle)
                text = note_option_text(note)
                note_list.append((text, note))
            if len(note_list) > 0:
                menu.add(Gtk.SeparatorMenuItem())
                menu.add(Gtk.SeparatorMenuItem())
                note_list.sort(key=lambda x: x[0])
                for text, note in note_list:
                    menu.add(
                        menu_item(
                            "gramps-notes", text, self.edit_note, note.handle
                        )
                    )
        return submenu_item("gramps-notes", _("Notes"), menu)

    def add_new_note(self, _dummy_obj, content=None):
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
                self._added_note,
            )
        except WindowActiveError:
            pass

    def _added_note(self, handle):
        """
        Add the new or existing note to the current object.
        """
        if handle:
            note = self.fetch("Note", handle)
            message = self._commit_message(_("Note"), note.get_gramps_id())
            self.focus.save_hash()
            if self.focus.obj.add_note(handle):
                self.focus.sync_hash(self.grstate)
                self.primary.commit(self.grstate, message)

    def add_existing_note(self, _dummy_obj):
        """
        Add an existing note.
        """
        select_note = SelectorFactory("Note")
        selector = select_note(self.grstate.dbstate, self.grstate.uistate, [])
        selection = selector.run()
        if selection:
            self._added_note(selection.handle)

    def edit_note(self, _dummy_obj, handle):
        """
        Edit a note.
        """
        note = self.fetch("Note", handle)
        self.edit_primary_object(None, note, "Note")

    def remove_note(self, _dummy_obj, note):
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
            message = self._commit_message(
                _("Note"), note.get_gramps_id(), action="remove"
            )
            self.focus.save_hash()
            self.focus.obj.remove_note(note.get_handle())
            self.focus.sync_hash(self.grstate)
            self.primary.commit(self.grstate, message)

    def _change_privacy_option(self):
        """
        Build privacy option based on current object state.
        """
        if self.focus.obj.get_privacy():
            return menu_item(
                "gramps-unlock", _("Make public"), self._change_privacy, False
            )
        return menu_item(
            "gramps-lock", _("Make private"), self._change_privacy, True
        )

    def _change_privacy(self, _dummy_obj, mode):
        """
        Update the privacy indicator for the current object.
        """
        text = _("Public")
        if mode:
            text = _("Private")
        if self.secondary:
            message = " ".join(
                (
                    _("Made"),
                    self.secondary.obj_lang,
                    _("for"),
                    self.primary.obj_lang,
                    self.primary.obj.get_gramps_id(),
                    text,
                )
            )
        else:
            message = " ".join(
                (
                    _("Made"),
                    self.primary.obj_lang,
                    self.primary.obj.get_gramps_id(),
                    text,
                )
            )
        self.focus.save_hash()
        self.focus.obj.set_privacy(mode)
        self.focus.sync_hash(self.grstate)
        self.primary.commit(self.grstate, message)

    def add_new_media(self, _dummy_obj, filepath=None):
        """
        Add a new media item.
        """
        media = Media()
        if filepath:
            if filepath[:5] != "file:":
                return
            filename = filepath[5:]
            while filename[:2] == "//":
                filename = filename[1:]
            if not os.path.isfile(filename):
                return

            if global_config.get("behavior.addmedia-relative-path"):
                base_path = str(media_path(self.grstate.dbstate.db))
                if not os.path.exists(base_path):
                    return
                filename = relative_path(filename, base_path)
            media.set_path(filename)
        try:
            EditMedia(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                media,
                self.add_new_media_ref,
            )
        except WindowActiveError:
            pass

    def add_new_media_ref(self, obj_or_handle):
        """
        Add a new media reference.
        """
        if isinstance(obj_or_handle, str):
            media = self.fetch("Media", obj_or_handle)
        else:
            media = obj_or_handle
        for media_ref in self.primary.obj.get_media_list():
            if media_ref.ref == media.get_handle():
                return
        ref = MediaRef()
        ref.ref = media.get_handle()
        try:
            EditMediaRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                media,
                ref,
                self._added_new_media_ref,
            )
        except WindowActiveError:
            pass

    def _added_new_media_ref(self, reference, media):
        """
        Finish adding a new media reference.
        """
        message = " ".join(
            (
                _("Added"),
                _("MediaRef"),
                media.get_gramps_id(),
                _("to"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
        )
        self.primary.obj.add_media_reference(reference)
        self.primary.commit(self.grstate, message)

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.grstate.config.get("options.global.border-width")
        color = self.get_color_css()
        self.css = "".join(
            (".frame { border-width: ", str(border), "px; ", color, " }")
        ).encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(self.css)
        context = self.frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")
        if self.groptions.ref_mode in [2, 4]:
            context = self.ref_frame.get_style_context()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            context.add_class("frame")

    def get_color_css(self):
        """
        For derived objects to set their color scheme if in use.
        """
        scheme = global_config.get("colors.scheme")
        background = self.grstate.config.get(
            "options.global.default-background-color"
        )
        return "".join(("background-color: ", background[scheme], ";"))

    def get_css_style(self):
        """
        Return css style string.
        """
        return self.css
