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
NoteAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Note
from gramps.gui.editors import EditNote
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# NoteAction class
#
# action_object is the Note when applicable
# target_object and target_child_object are NoteBase objects
#
# ------------------------------------------------------------------------
class NoteAction(GrampsAction):
    """
    Class to support actions related to note objects.
    """

    def __init__(
        self,
        grstate,
        action_object=None,
        target_object=None,
        target_child_object=None,
    ):
        GrampsAction.__init__(
            self, grstate, action_object, target_object, target_child_object
        )
        self.content = None

    def set_content(self, content):
        """
        Set content.
        """
        self.content = content

    def edit_note(self, *_dummy_args):
        """
        Launch note editor.
        """
        try:
            EditNote(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
            )
        except WindowActiveError:
            pass

    def update_note(self, *_dummy_args):
        """
        Update a note.
        """
        if self.content and self.action_object:
            self.action_object.obj.append(self.content)
        self.edit_note()

    def added_note(self, note_handle):
        """
        Add the new or existing note to the current object.
        """
        if note_handle:
            active_target_object = self.get_target_object()
            note = self.db.get_note_from_handle(note_handle)
            message = self.commit_message(_("Note"), note.get_gramps_id())
            active_target_object.save_hash()
            if active_target_object.obj.add_note(note_handle):
                active_target_object.sync_hash(self.grstate)
                self.target_object.commit(self.grstate, message)

    def add_new_note(self, *_dummy_args):
        """
        Create a new note to be added to an object.
        """
        self.set_action_object(Note())
        if self.content:
            self.action_object.obj.set(self.content)
        self.edit_note(self.added_note)

    def add_existing_note(self, *_dummy_args):
        """
        Select an existing note to be added to an object.
        """
        get_note_selector = SelectorFactory("Note")
        note_selector = get_note_selector(
            self.grstate.dbstate, self.grstate.uistate, []
        )
        note = note_selector.run()
        if note:
            self.added_note(note.get_handle())

    def remove_note(self, *_dummy_args):
        """
        Remove the note from the current object.
        """
        if not self.action_object:
            return
        note = self.action_object.obj
        text = self.describe_object(note)
        prefix = _(
            "You are about to remove the following note from this object:"
        )
        extra = _("This removes the reference but does not delete the note.")
        if self.confirm_action(
            _("Warning"), prefix, "\n\n<b>", text, "</b>\n\n", extra
        ):
            message = self.commit_message(
                _("Note"), note.get_gramps_id(), action="remove"
            )
            active_target_object = self.get_target_object()
            active_target_object.save_hash()
            active_target_object.obj.remove_note(note.get_handle())
            active_target_object.sync_hash(self.grstate)
            self.target_object.commit(self.grstate, message)


factory.register_action("Note", NoteAction)
