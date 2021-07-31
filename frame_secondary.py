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
SecondaryGrampsFrame
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
from gramps.gui.editors import (
    EditAddress,
    EditCitation,
    EditName,
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
from frame_classes import GrampsConfig
from frame_const import _EDITORS, _LEFT_BUTTON, _RIGHT_BUTTON
from frame_utils import button_activated, get_gramps_object_type
from page_layout import ProfileViewLayout

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# SecondaryGrampsFrame class
#
# ------------------------------------------------------------------------
class SecondaryGrampsFrame(Gtk.VBox, GrampsConfig):
    """
    The SecondaryGrampsFrame class provides core methods for constructing the
    view and working with the secondary Gramps object it exposes.
    """

    def __init__(self, grstate, context, primary_obj, secondary_obj, groups=None):
        Gtk.VBox.__init__(self, hexpand=True, vexpand=False)
        GrampsConfig.__init__(self, grstate)
        self.context = context
        self.primary_obj = primary_obj
        self.primary_type, skip1, skip2 = get_gramps_object_type(primary_obj)
        self.secondary_obj = secondary_obj
        self.secondary_type, self.dnd_type, self.dnd_icon = get_gramps_object_type(secondary_obj)
        self.dnd_drop_targets = []
        self.obj_type_lang = glocale.translation.sgettext(self.secondary_type)
        self.action_menu = None
        self.facts_row = 0

        vcontent = Gtk.VBox()
        self.title = Gtk.HBox()
        vcontent.pack_start(self.title, expand=True, fill=True, padding=0)
        self.facts_grid = Gtk.Grid(row_spacing=2, column_spacing=6, halign=Gtk.Align.START, hexpand=False)
        vcontent.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
        body = Gtk.HBox(hexpand=True, margin=3)
        body.pack_start(vcontent, expand=True, fill=True, padding=0)
        if self.secondary_obj.private:
            vlock = Gtk.VBox()
            image = Gtk.Image()
            image.set_from_icon_name("gramps-lock", Gtk.IconSize.BUTTON)
            vlock.pack_start(image, False, False, 0)
            body.pack_start(vlock, False, False, 0)
        if groups and "data" in groups:
            groups["data"].add_widget(body)
        self.frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        self.frame.set_size_request(160, -1)
        self.frame.add(body)
        self.eventbox = Gtk.EventBox()
        self.eventbox.connect("button-press-event", self.route_action)
        self.eventbox.add(self.frame)
        self.add(self.eventbox)

    def enable_drag(self):
        """
        Enable self as a drag source.
        """
        if self.eventbox:
            self.eventbox.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                          [], Gdk.DragAction.COPY)
            target_list = Gtk.TargetList.new([])
            target_list.add(self.dnd_type.atom_drag_type,
                            self.dnd_type.target_flags,
                            self.dnd_type.app_id)
            self.eventbox.drag_source_set_target_list(target_list)
            self.eventbox.drag_source_set_icon_name(self.dnd_icon)
            self.eventbox.connect('drag_data_get', self.drag_data_get)

    def drag_data_get(self, widget, context, sel_data, info, time):
        """
        Return requested data.
        """
        if info == self.dnd_type.app_id:
            data = (self.dnd_type.drag_type, id(self), self.obj.get_handle(), 0)
            sel_data.set(self.dnd_type.atom_drag_type, 8, pickle.dumps(data))

    def enable_drop(self):
        """
        Enable self as a drop target.
        """
        if self.eventbox:
            self.dnd_drop_targets.append(DdTargets.URI_LIST.target())
            for target in DdTargets.all_text_targets():
                self.dnd_drop_targets.append(target)
            self.dnd_drop_targets.append(Gtk.TargetEntry.new('text/html', 0, 7))
            self.dnd_drop_targets.append(Gtk.TargetEntry.new('URL', 0, 8))
            self.dnd_drop_targets.append(DdTargets.NOTE_LINK.target())
            self.dnd_drop_targets.append(DdTargets.CITATION_LINK.target())
            self.eventbox.drag_dest_set(
                Gtk.DestDefaults.ALL,
                self.dnd_drop_targets,
                Gdk.DragAction.COPY
            )
            self.eventbox.connect("drag-data-received", self.on_drag_data_received)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        """
        Handle dropped data.
        """
        if data and data.get_data():
            try:
                dnd_type, obj_id, obj_handle, skip = pickle.loads(data.get_data())
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
        if data:
            if hasattr(self.secondary_obj, "note_list"):
                self.add_new_note(None, content=data)

    def add_fact(self, fact, label=None, row=None, column=0, stop=1):
        """
        Add a simple fact.
        """
        row_number = row or self.facts_row
        if label:
            self.facts_grid.attach(label, column, row_number, stop, 1)
            self.facts_grid.attach(fact, column + 1, row_number, stop, 1)
        else:
            self.facts_grid.attach(fact, column, row_number, stop + 1, 1)
        if row is None:
            self.facts_row = self.facts_row + 1

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
            self.switch_object(None, None, self.primary_type, self.primary_obj.get_handle())

    def layout_editor(self):
        """
        Launch page layout editor.
        """
        try:
            ProfileViewLayout(self.grstate.uistate, self.grstate.config, self.primary_type)
        except WindowActiveError:
            pass

    def build_action_menu(self, obj, event):
        """
        Build the action menu for a right click. First action will always be edit,
        then any custom actions of the derived children, then the global actions
        supported for all objects enabled for them.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.action_menu = Gtk.Menu()
            self.action_menu.append(self._edit_secondary_object_option())
            self.add_custom_actions()
            if hasattr(self.secondary_obj, "citation_list"):
                self.action_menu.append(
                    self._citations_option(
                        self.secondary_obj, self.add_new_citation, self.add_existing_citation, self.remove_citation
                    )
                )
            if hasattr(self.secondary_obj, "note_list"):
                self.action_menu.append(
                    self._notes_option(
                        self.secondary_obj, self.add_new_note, self.add_existing_note, self.remove_note
                    )
                )
            self.action_menu.append(self._change_privacy_option())
            self.action_menu.show_all()
            if Gtk.get_minor_version() >= 22:
                self.action_menu.popup_at_pointer(event)
            else:
                self.action_menu.popup(None, None, None, None, event.button, event.time)

    def add_custom_actions(self):
        """
        For derived objects to inject their own actions into the menu.
        """

    def _menu_item(self, icon, label, callback, data1=None, data2=None):
        """
        Helper for constructing a menu item.
        """
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=label)
        if data2 is not None:
            item.connect("activate", callback, data1, data2)
        elif data1 is not None:
            item.connect("activate", callback, data1)
        else:
            item.connect("activate", callback)
        return item

    def _submenu_item(self, icon, label, menu):
        """
        Helper for constructing a submenu item.
        """
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=label)
        item.set_submenu(menu)
        return item

    def _edit_secondary_object_option(self):
        """
        Build the edit option.
        """
        name = "{} {}".format(_("Edit"), self.secondary_type.lower())
        return self._menu_item("gtk-edit", name, self.edit_secondary_object)

    def edit_primary_object(self, skip=None, obj=None, obj_type=None):
        """
        Launch the desired editor based on object type defaulting to the managed object.
        """
        obj = obj or self.primary_obj
        obj_type = obj_type or self.primary_type
        try:
            _EDITORS[obj_type](self.grstate.dbstate, self.grstate.uistate, [], obj)
        except WindowActiveError:
            pass

    def edit_secondary_object(self, skip=None):
        """
        Launch the desired editor based on object type defaulting to the managed object.
        """
        try:
            _EDITORS[self.secondary_type](self.grstate.dbstate, self.grstate.uistate, [], self.secondary_obj, self.save_object)
        except WindowActiveError:
            pass

    def save_object(self, obj, action_text=None):
        """
        Save the edited object.
        """
        if not obj:
            return
        action = "{} {} {} {} {}".format(
            _("Edited"),
            glocale.translation.sgettext(self.secondary_type),
            _("for"),
            glocale.translation.sgettext(self.primary_type),
            self.primary_obj.get_gramps_id()
        )
        if action_text:
            action = action_text
        commit_method = self.grstate.dbstate.db.method("commit_%s", self.primary_type)
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            commit_method(self.primary_obj, trans)

    def _citations_option(self, obj, add_new_citation, add_existing_citation, remove_citation):
        """
        Build the citations submenu.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("list-add", _("Add a new citation"), add_new_citation))
        menu.add(self._menu_item("list-add", _("Add an existing citation"), add_existing_citation))
        if len(obj.get_citation_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(self._submenu_item("gramps-citation", _("Remove a citation"), removemenu))
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            citation_list = []
            for handle in obj.get_citation_list():
                citation = self.grstate.dbstate.db.get_citation_from_handle(handle)
                text = self._citation_option_text(citation)
                citation_list.append((text, citation))
            citation_list.sort(key=lambda x: x[0])
            for text, citation in citation_list:
                removemenu.add(self._menu_item("list-remove", text, remove_citation, citation))
                menu.add(self._menu_item("gramps-citation", text, self.edit_citation, citation))
        return self._submenu_item("gramps-citation", _("Citations"), menu)

    def _citation_option_text(self, citation):
        """
        Helper to build citation description string.
        """
        if citation.source_handle:
            source = self.grstate.dbstate.db.get_source_from_handle(citation.source_handle)
            if source.get_title():
                text = source.get_title()
            else:
                text = "[{}]".format(_("Missing Source"))
        if citation.page:
            text = "{}: {}".format(text, citation.page)
        else:
            text = "{}: [{}]".format(text, _("Missing Page"))
        return text

    def add_new_citation(self, obj):
        """
        Add a new citation.
        """
        citation = Citation()
        source = Source()
        try:
            EditCitation(self.grstate.dbstate, self.grstate.uistate, [], citation, source, self.added_citation)
        except WindowActiveError:
            pass

    def added_citation(self, handle):
        """
        Add the new or existing citation to the current object.
        """
        if handle and self.secondary_obj.add_citation(handle):
            citation = self.grstate.dbstate.db.get_citation_from_handle(handle)
            action = "{} {} {} {} {} {} {}".format(
                _("Added Citation"),
                citation.get_gramps_id(),
                _("to"),
                glocale.translation.sgettext(self.secondary_type),
                _("for"),
                glocale.translation.sgettext(self.primary_type),
                self.primary_obj.get_gramps_id()
            )
            self.save_object(self.secondary_obj, action_text=action)

    def add_existing_citation(self, obj):
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
                                 callback=self.added_citation)
                except WindowActiveError:
                    pass
            elif isinstance(selection, Citation):
                try:
                    EditCitation(self.grstate.dbstate, self.grstate.uistate, [],
                                 selection, callback=self.added_citation)
                except WindowActiveError:
                    pass
            else:
                raise ValueError("Selection must be either source or citation")

    def edit_citation(self, obj, citation):
        """
        Edit a citation.
        """
        self.edit_primary_object(None, citation, "Citation")

    def remove_citation(self, obj, old_citation):
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
            action = "{} {} {} {} {} {} {}".format(
                _("Removed Citation"),
                old_citation.get_gramps_id(),
                _("from"),
                glocale.translation.sgettext(self.secondary_type),
                _("for"),
                glocale.translation.sgettext(self.primary_type),
                self.primary_obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.primary_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.secondary_obj.remove_citation_references([old_citation.get_handle()])
                commit_method(self.primary_obj, trans)

    def _notes_option(self, obj, add_new_note, add_existing_note, remove_note, no_children=False):
        """
        Build the notes submenu.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("list-add", _("Add a new note"), add_new_note))
        menu.add(self._menu_item("list-add", _("Add an existing note"), add_existing_note))
        if len(obj.get_note_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(self._submenu_item("gramps-notes", _("Remove a note"), removemenu))
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            note_list = []
            for handle in obj.get_note_list():
                note = self.grstate.dbstate.db.get_note_from_handle(handle)
                text = self._note_option_text(note)
                note_list.append((text, note))
            note_list.sort(key=lambda x: x[0])
            for text, note in note_list:
                removemenu.add(self._menu_item("list-remove", text, remove_note, note))
                menu.add(self._menu_item("gramps-notes", text, self.edit_note, note.handle))
        if self.option("page", "include-child-notes") and not no_children:
                note_list = []
                for child_obj in obj.get_note_child_list():
                    for handle in child_obj.get_note_list():
                        note = self.grstate.dbstate.db.get_note_from_handle(handle)
                        text = self._note_option_text(note)
                        note_list.append((text, note))
                if len(note_list) > 0:
                    menu.add(Gtk.SeparatorMenuItem())
                    menu.add(Gtk.SeparatorMenuItem())
                    note_list.sort(key=lambda x: x[0])
                    for text, note in note_list:
                        menu.add(self._menu_item("gramps-notes", text, self.edit_note, note.handle))
        return self._submenu_item("gramps-notes", _("Notes"), menu)

    def _note_option_text(self, note):
        """
        Helper to build note description string.
        """
        notetype = str(note.get_type())
        text = note.get()[:50].replace('\n', ' ')
        if len(text) > 40:
            text = text[:40]+"..."
        return "{}: {}".format(notetype, text)

    def add_new_note(self, obj, content=None):
        """
        Add a new note.
        """
        note = Note()
        if content:
            note.set(content)
        try:
            EditNote(self.grstate.dbstate, self.grstate.uistate, [], note, self.added_note)
        except WindowActiveError:
            pass

    def added_note(self, handle):
        """
        Add the new or existing note to the current object.
        """
        if handle and self.secondary_obj.add_note(handle):
            note = self.grstate.dbstate.db.get_note_from_handle(handle)
            action = "{} {} {} {} {} {} {}".format(
                _("Added Note"),
                note.get_gramps_id(),
                _("to"),
                glocale.translation.sgettext(self.secondary_type),
                _("for"),
                glocale.translation.sgettext(self.primary_type),
                self.primary_obj.get_gramps_id()
            )
            self.save_object(self.secondary_obj, action_text=action)

    def add_existing_note(self, obj):
        """
        Add an existing note.
        """
        select_note = SelectorFactory('Note')
        selector = select_note(self.grstate.dbstate, self.grstate.uistate, [])
        selection = selector.run()
        if selection:
            self.added_note(selection.handle)

    def edit_note(self, obj, handle):
        """
        Edit a note.
        """
        note = self.grstate.dbstate.db.get_note_from_handle(handle)
        self.edit_primary_object(None, note, "Note")

    def remove_note(self, obj, old_note):
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
            action = "{} {} {} {} {} {} {}".format(
                _("Removed Note"),
                old_note.get_gramps_id(),
                _("from"),
                glocale.translation.sgettext(self.secondary_type),
                _("for"),
                glocale.translation.sgettext(self.primary_type),
                self.primary_obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.primary_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.secondary_obj.remove_note(old_note.get_handle())
                commit_method(self.primary_obj, trans)

    def _change_privacy_option(self):
        """
        Build privacy option based on current object state.
        """
        if self.secondary_obj.get_privacy():
            return self._menu_item("gramps-unlock", _("Make public"), self.change_privacy, False)
        return self._menu_item("gramps-lock", _("Make private"), self.change_privacy, True)

    def change_privacy(self, obj, mode):
        """
        Update the privacy indicator for the current object.
        """
        if mode:
            text = _("Private")
        else:
            text = _("Public")
        action = "{} {} {} {} {} {}".format(
            _("Made"),
            glocale.translation.sgettext(self.secondary_type),
            _("for"),
            glocale.translation.sgettext(self.primary_type),
            self.primary_obj.get_gramps_id(),
            text,
        )
        commit_method = self.grstate.dbstate.db.method("commit_%s", self.primary_type)
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.secondary_obj.set_privacy(mode)
            commit_method(self.primary_obj, trans)

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
