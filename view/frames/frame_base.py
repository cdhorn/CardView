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
import pickle
import re


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
from gramps.gui.editors import (
    EditCitation,
    EditNote,
)
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import (
    Citation,
    Note,
    Source,
)
from gramps.gui.ddtargets import DdTargets
from gramps.gui.selectors import SelectorFactory


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_classes import GrampsConfig, GrampsObject
from .frame_const import _EDITORS, _LEFT_BUTTON, _RIGHT_BUTTON
from .frame_utils import (
    button_activated,
    citation_option_text,
    menu_item,
    note_option_text,
    submenu_item
)
from ..pages.page_layout import ProfileViewLayout

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsFrame class
#
# ------------------------------------------------------------------------
class GrampsFrame(Gtk.VBox, GrampsConfig):
    """
    The GrampsFrame class provides core methods for constructing the view
    and working with the primary and secondary Gramps objects it helps expose.
    """

    def __init__(
        self, grstate, context, primary_obj, secondary_obj=None
    ):
        Gtk.VBox.__init__(self, hexpand=True, vexpand=False)
        GrampsConfig.__init__(self, grstate)
        self.context = context
        self.primary = GrampsObject(primary_obj)
        self.focus = self.primary
        self.has_reference = False
        self.secondary = None
        if secondary_obj:
            self.secondary = GrampsObject(secondary_obj)
            if self.secondary.is_reference:
                self.has_reference = True
            else:
                self.focus = self.secondary
        self.dnd_drop_targets = []
        self.action_menu = None

        self.eventbox = Gtk.EventBox()
        self.eventbox.connect("button-press-event", self.route_action)
        self.frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        self.facts_grid = Gtk.Grid(
            row_spacing=2,
            column_spacing=6,
            halign=Gtk.Align.START,
            hexpand=False,
        )
        self.facts_row = 0

    def enable_drag(self):
        """
        Enable self as a drag source.
        """
        if self.eventbox:
            self.eventbox.drag_source_set(
                Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY
            )
            target_list = Gtk.TargetList.new([])
            target_list.add(
                self.focus.dnd_type.atom_drag_type,
                self.focus.dnd_type.target_flags,
                self.focus.dnd_type.app_id,
            )
            self.eventbox.drag_source_set_target_list(target_list)
            self.eventbox.drag_source_set_icon_name(self.focus.dnd_icon)
            self.eventbox.connect("drag_data_get", self.drag_data_get)

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

    def enable_drop(self):
        """
        Enable self as a basic drop target, override in derived classes as
        needed.
        """
        if self.eventbox:
            self.dnd_drop_targets.append(DdTargets.URI_LIST.target())
            for target in DdTargets.all_text_targets():
                self.dnd_drop_targets.append(target)
            self.dnd_drop_targets.append(Gtk.TargetEntry.new("text/html", 0, 7))
            self.dnd_drop_targets.append(Gtk.TargetEntry.new("URL", 0, 8))
            self.dnd_drop_targets.append(DdTargets.NOTE_LINK.target())
            self.dnd_drop_targets.append(DdTargets.CITATION_LINK.target())
            self.eventbox.drag_dest_set(
                Gtk.DestDefaults.ALL, self.dnd_drop_targets, Gdk.DragAction.COPY
            )
            self.eventbox.connect("drag-data-received", self.drag_data_received)

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
                dnd_type, obj_id, obj_handle, dummy_var1 = pickle.loads(
                    data.get_data()
                )
            except pickle.UnpicklingError:
                return self.dropped_text(data.get_data().decode("utf-8"))
            if id(self) == obj_id:
                return
            if DdTargets.CITATION_LINK.drag_type == dnd_type:
                self.added_citation(obj_handle)
            elif DdTargets.NOTE_LINK.drag_type == dnd_type:
                self.added_note(obj_handle)

    def dropped_text(self, data):
        """
        Examine and try to handle dropped text in a reasonable manner.
        """
        added_urls = 0
        if hasattr(self.focus.obj, "urls"):
            links = re.findall(r"(?P<url>https?://[^\s]+)", data)
            if links:
                for link in links:
                    self.add_url(None, path=link)
                    added_urls = added_urls + len(link)
        if not added_urls or (len(data) > (2 * added_urls)):
            if hasattr(self.focus.obj, "note_list"):
                self.add_new_note(None, content=data)

    def route_action(self, obj, event):
        """
        Route the action if the frame was clicked on.
        """
        if button_activated(event, _RIGHT_BUTTON):
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                self.layout_editor()
            else:
                self.build_action_menu(obj, event)
        elif not button_activated(event, _LEFT_BUTTON):
            self.switch_object(
                None, None, self.focus.obj_type, self.focus.obj.get_handle()
            )

    def layout_editor(self):
        """
        Launch page layout editor.
        """
        try:
            ProfileViewLayout(
                self.grstate.uistate, self.grstate.config, self.primary.obj_type
            )
        except WindowActiveError:
            pass

    def build_action_menu(self, obj, event):
        """
        Build the action menu for a right click, should be defined in
        derived classes.
        """

    def _edit_object_option(self):
        """
        Build the edit option.
        """
        if self.secondary:
            name = "{} {}".format(_("Edit"), self.secondary.obj_lang.lower())
            return menu_item("gtk-edit", name, self.edit_secondary_object)
        if self.primary.obj_type == "Person":
            name = "{} {}".format(
                _("Edit"), name_displayer.display(self.primary.obj)
            )
        else:
            name = "{} {}".format(_("Edit"), self.primary.obj_lang.lower())
        return menu_item("gtk-edit", name, self.edit_primary_object)

    def edit_primary_object(self, _dummy_var1=None, obj=None, obj_type=None):
        """
        Launch the desired editor for a primary object.
        """
        obj = obj or self.primary.obj
        obj_type = obj_type or self.primary.obj_type
        try:
            _EDITORS[obj_type](
                self.grstate.dbstate, self.grstate.uistate, [], obj
            )
        except WindowActiveError:
            pass

    def edit_secondary_object(self, _dummy_var1=None):
        """
        Launch the desired editor for a secondary object.
        """
        try:
            self.secondary.obj_edit(
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
            action = action_text
        else:
            action = "{} {} {} {} {}".format(
                _("Edited"),
                self.secondary.obj_lang,
                _("for"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
        commit_method = self.grstate.dbstate.db.method(
            "commit_%s", self.primary.obj_type
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            commit_method(self.primary.obj, trans)

    def _commit_message(self, action, obj_type, obj, preposition):
        """
        Construct a commit message string.
        """
        if self.secondary:
            return "{} {} {} {} {} {} {} {}".format(
                action,
                obj_type,
                obj.get_gramps_id(),
                preposition,
                self.secondary.obj_lang,
                _("for"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
        return "{} {} {} {} {} {}".format(
            action,
            obj_type,
            obj.get_gramps_id(),
            preposition,
            self.primary.obj_lang,
            self.primary.obj.get_gramps_id(),
        )

    def _citations_option(
        self, obj, add_new_citation, add_existing_citation, remove_citation
    ):
        """
        Build the citations submenu.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item(
                "list-add", _("Add a new citation"), add_new_citation
            )
        )
        menu.add(
            menu_item(
                "list-add", _("Add an existing citation"), add_existing_citation
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
                citation = self.grstate.dbstate.db.get_citation_from_handle(
                    handle
                )
                text = citation_option_text(self.grstate.dbstate.db, citation)
                citation_list.append((text, citation))
            citation_list.sort(key=lambda x: x[0])
            for text, citation in citation_list:
                removemenu.add(
                    menu_item(
                        "list-remove", text, remove_citation, citation
                    )
                )
                menu.add(
                    menu_item(
                        "gramps-citation", text, self.edit_citation, citation
                    )
                )
        return submenu_item("gramps-citation", _("Citations"), menu)

    def add_new_citation(self, _dummy_obj):
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
                self.added_citation,
            )
        except WindowActiveError:
            pass

    def added_citation(self, handle):
        """
        Add the new or existing citation to the current object.
        """
        if handle and self.focus.obj.add_citation(handle):
            citation = self.grstate.dbstate.db.get_citation_from_handle(handle)
            action = self._commit_message(
                _("Added"), _("Citation"), citation, _("to")
            )
            self.save_object(self.focus.obj, action_text=action)

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
                        callback=self.added_citation,
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
                        callback=self.added_citation,
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
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"),
            "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm),
        ):
            action = self._commit_message(
                _("Removed"), _("Citation"), citation, _("from")
            )
            commit_method = self.grstate.dbstate.db.method(
                "commit_%s", self.primary.obj_type
            )
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.focus.obj.remove_citation_references(
                    [citation.get_handle()]
                )
                commit_method(self.primary.obj, trans)

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
            menu_item(
                "list-add", _("Add an existing note"), add_existing_note
            )
        )
        if len(obj.get_note_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(
                submenu_item(
                    "gramps-notes", _("Remove a note"), removemenu
                )
            )
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            note_list = []
            for handle in obj.get_note_list():
                note = self.grstate.dbstate.db.get_note_from_handle(handle)
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
        if self.option("page", "include-child-notes") and not no_children:
            note_list = []
            for child_obj in obj.get_note_child_list():
                for handle in child_obj.get_note_list():
                    note = self.grstate.dbstate.db.get_note_from_handle(handle)
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
                self.added_note,
            )
        except WindowActiveError:
            pass

    def added_note(self, handle):
        """
        Add the new or existing note to the current object.
        """
        if handle and self.focus.obj.add_note(handle):
            note = self.grstate.dbstate.db.get_note_from_handle(handle)
            action = self._commit_message(_("Added"), _("Note"), note, _("to"))
            self.save_object(self.focus.obj, action_text=action)

    def add_existing_note(self, _dummy_obj):
        """
        Add an existing note.
        """
        select_note = SelectorFactory("Note")
        selector = select_note(self.grstate.dbstate, self.grstate.uistate, [])
        selection = selector.run()
        if selection:
            self.added_note(selection.handle)

    def edit_note(self, _dummy_obj, handle):
        """
        Edit a note.
        """
        note = self.grstate.dbstate.db.get_note_from_handle(handle)
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
        extra = _(
            "This removes the reference but does not delete the note."
        )
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"),
            "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm),
        ):
            action = self._commit_message(
                _("Removed"), _("Note"), note, _("from")
            )
            commit_method = self.grstate.dbstate.db.method(
                "commit_%s", self.primary.obj_type
            )
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.focus.obj.remove_note(note.get_handle())
                commit_method(self.primary.obj, trans)

    def _change_privacy_option(self):
        """
        Build privacy option based on current object state.
        """
        if self.focus.obj.get_privacy():
            return menu_item(
                "gramps-unlock", _("Make public"), self.change_privacy, False
            )
        return menu_item(
            "gramps-lock", _("Make private"), self.change_privacy, True
        )

    def change_privacy(self, _dummy_obj, mode):
        """
        Update the privacy indicator for the current object.
        """
        text = _("Public")
        if mode:
            text = _("Private")
        if self.secondary:
            action = "{} {} {} {} {} {}".format(
                _("Made"),
                self.secondary.obj_lang,
                _("for"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
                text,
            )
        else:
            action = "{} {} {} {}".format(
                _("Made"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
                text,
            )
        commit_method = self.grstate.dbstate.db.method(
            "commit_%s", self.primary.obj_type
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.focus.obj.set_privacy(mode)
            commit_method(self.primary.obj, trans)

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.grstate.config.get("options.global.border-width")
        color = self.get_color_css()
        css = ".frame {{ border-width: {}px; {} }}".format(border, color)
        css = css.encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = self.frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")

    def get_color_css(self):
        """
        For derived objects to set their color scheme if in use.
        """
        return ""
