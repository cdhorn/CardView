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
RepositoryGrampsFrame
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
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Note
from gramps.gen.lib.const import IDENTICAL
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import EditNote, EditRepoRef
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
    menu_item,
    note_option_text,
)
from .frame_primary import PrimaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# RepositoryGrampsFrame Class
#
# ------------------------------------------------------------------------
class RepositoryGrampsFrame(PrimaryGrampsFrame):
    """
    The RepositoryGrampsFrame exposes some of the basic facts about a
    Repository.
    """

    def __init__(self, grstate, groptions, repository, repo_ref=None):
        PrimaryGrampsFrame.__init__(self, grstate, groptions, repository)
        self.reference = GrampsObject(repo_ref)

        title = TextLink(
            repository.name,
            "Repository",
            repository.get_handle(),
            self.switch_object,
            bold=True,
        )
        self.widgets["title"].pack_start(title, True, False, 0)

        if repository.get_address_list():
            address = repository.get_address_list()[0]
            if address.street:
                self.add_fact(self.make_label(address.street))
            text = ""
            comma = ""
            if address.city:
                text = address.city
                comma = ", "
            if address.state:
                text = "{}{}{}".format(text, comma, address.state)
                comma = ", "
            if address.country:
                text = "{}{}{}".format(text, comma, address.country)
            if address.postal:
                text = "{} {}".format(text, address.postal)
            if text:
                self.add_fact(self.make_label(text))
            if address.phone:
                self.add_fact(self.make_label(address.phone))

        if groptions.ref_mode and repo_ref:
            self.ref_widgets["id"].load(
                repo_ref, "RepoRef", gramps_id=repository.get_gramps_id()
            )
            vbox = Gtk.VBox()
            if self.get_option("show-call-number"):
                if repo_ref.call_number:
                    text = "{}: {}".format(
                        _("Call number"), repo_ref.call_number
                    ).replace("::", ":")
                    vbox.pack_start(self.make_label(text), False, False, 0)

            if self.get_option("show-media-type"):
                if repo_ref.media_type:
                    text = glocale.translation.sgettext(
                        repo_ref.media_type.xml_str()
                    )
                    if text:
                        text = "{} {}: {}".format(_("Media"), _("type"), text)
                    vbox.pack_start(self.make_label(text), False, False, 0)
            self.ref_widgets["body"].pack_start(vbox, False, False, 0)

            if "indicators" in self.ref_widgets:
                if "active" in self.groptions.option_space:
                    size = 12
                else:
                    size = 5
                self.ref_widgets["indicators"].load(
                    repo_ref, "RepoRef", size=size
                )

            self.dnd_drop_ref_targets = []
            self.ref_eventbox.connect(
                "button-press-event", self.route_ref_action
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

        if self.get_option("show-repository-type"):
            if repository.get_type():
                label = self.make_label(str(repository.get_type()), left=False)
                self.widgets["attributes"].add_fact(label)

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

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
            if DdTargets.NOTE_LINK.drag_type == dnd_type:
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
            source = self.fetch("Source", self.groptions.backlink)
            context = GrampsContext(source, self.reference.obj, None)
            return self.grstate.load_page(context.pickled)

    def build_ref_action_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click on a reference object.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            action_menu = Gtk.Menu()
            action_menu.append(self._edit_repo_ref_option())
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
            label = Gtk.MenuItem(
                label="{} {}".format(_("Repository"), _("reference"))
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

    def _edit_repo_ref_option(self):
        """
        Build the edit option.
        """
        name = "{} {}".format(_("Edit"), _("reference"))
        return menu_item("gtk-edit", name, self.edit_repo_ref)

    def edit_repo_ref(self, *_dummy_obj):
        """
        Launch the editor.
        """
        try:
            EditRepoRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.primary.obj,
                self.reference.obj,
                self.save_repo_ref,
            )
        except WindowActiveError:
            pass

    def save_repo_ref(self, changed_repo_ref, action_text=None, delete=False):
        """
        Save the edited object.
        """
        if not changed_repo_ref:
            return
        if isinstance(changed_repo_ref, tuple):
            repo_ref = changed_repo_ref[0]
        else:
            repo_ref = changed_repo_ref
        source = self.fetch("Source", self.groptions.backlink)
        repo_ref_list = []
        for ref in source.get_reporef_list():
            if repo_ref.ref == ref.ref:
                if repo_ref.is_equivalent(ref) == IDENTICAL:
                    if not delete:
                        return
                repo_ref_list.append(repo_ref)
            else:
                repo_ref_list.append(ref)
        if action_text:
            action = action_text
        else:
            action = "{} {} {} {} {} {}".format(
                _("Edited"),
                _("RepoRef"),
                self.primary.obj.get_gramps_id(),
                _("for"),
                _("Source"),
                source.get_gramps_id(),
            )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            source.set_reporef_list(repo_ref_list)
            self.grstate.dbstate.db.commit_source(source, trans)

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
                _("RepoRef"),
                self.primary.obj.get_gramps_id(),
            )
            self.save_repo_ref(self.reference.obj, action_text=action)

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
                _("RepoRef"),
                self.primary.obj.get_gramps_id(),
            )
            self.reference.obj.remove_note(note.get_handle())
            self.save_repo_ref(
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
        source = self.fetch("Source", self.groptions.backlink)
        if mode:
            text = _("Private")
        else:
            text = _("Public")
        action = "{} {} {} {} {} {}".format(
            _("Made"),
            _("RepoRef"),
            self.primary.obj.get_gramps_id(),
            _("Source"),
            source.get_gramps_id(),
            text,
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            for repo_ref in source.get_reporef_list():
                if repo_ref.ref == self.reference.obj.ref:
                    repo_ref.set_privacy(mode)
                    break
            self.grstate.dbstate.db.commit_source(source, trans)
